# apps/management/commands/produce_stock.py
import json
import time
from django.core.management.base import BaseCommand
from kafka import KafkaProducer
import requests  # 한국투자증권 API 호출용
import os
from dotenv import load_dotenv
load_dotenv()
def get_access_token():

    app_key = os.getenv("KIS_MOCK_APP_KEY")
    app_secret = os.getenv("KIS_MOCK_APP_SECRET")
    
    # 🎯 [디버깅] 키가 제대로 불려왔는지 첫 5글자만 찍어보기!
    print(f"🔑 앱 키 확인: {str(app_key)[:5]}***") 
    print(f"🔑 시크릿 키 확인: {str(app_secret)[:5]}***")
    """한국투자증권 Access Token 발급"""
    url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP" # 모의투자용 URL
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": os.getenv("KIS_MOCK_APP_KEY"),
        "appsecret": os.getenv("KIS_MOCK_APP_SECRET")
    }
    
    res = requests.post(url, headers=headers, data=json.dumps(body))
    return res.json().get('access_token')

class Command(BaseCommand):
    help = '한국투자증권 API 데이터를 Kafka로 전송합니다.'

    # handle 메서드 내부 수정 예시
    def handle(self, *args, **options):
        token = get_access_token()
        
        # Kafka Producer 설정
        producer = KafkaProducer(
            bootstrap_servers=['127.0.0.1:9092'], # 본인 EC2 IP
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # 한국투자증권 현재가 조회 API 설정
        url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": os.getenv("KIS_MOCK_APP_KEY"),
            "appsecret": os.getenv("KIS_MOCK_APP_SECRET"),
            "tr_id": "FHKST01010100" # 주식 현재가 조회용 TR ID
        }
        params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": "005930"} # J: 주식, 005930: 삼성전자

        self.stdout.write(self.style.SUCCESS('삼성전자 데이터 수집 시작...'))

        try:
            while True:
                res = requests.get(url, headers=headers, params=params)
                data = res.json()
                
                # 🎯 1. 데이터에 'output'(가격 정보)이 무사히 들어있을 때만 실행!
                if 'output' in data and data['output']:
                    output = data['output']
                    stock_info = {
                        "name": "삼성전자",
                        "price": output.get('stck_prpr'),
                        "change": output.get('prdy_vrss'),
                        "timestamp": time.time()
                    }

                    # 정상 데이터만 카프카로 전송
                    producer.send('stock-data', value=stock_info)
                    self.stdout.write(f"✅ 정상 전송: {stock_info['price']}원")
                
                # 🎯 2. API가 튕겨냈을 때 (가격 정보가 없을 때)
                else:
                    error_msg = data.get('msg1', '알 수 없는 에러')
                    self.stdout.write(self.style.WARNING(f"⚠️ API 차단됨 (1회 건너뜀): {error_msg}"))

                # 🎯 3. API 호출 제한에 안 걸리도록 쉬는 시간 늘리기 (2초 -> 3초 이상 권장)
                time.sleep(3)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"에러 발생: {e}"))