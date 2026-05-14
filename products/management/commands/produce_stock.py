# apps/management/commands/produce_stock.py
import json
import time
from django.core.management.base import BaseCommand
from kafka import KafkaProducer
import requests  # 한국투자증권 API 호출용
import os
from dotenv import load_dotenv
from requests.exceptions import RequestException
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
                try: # 🎯 "일단 시도해 봐!"
                    res = requests.get(url, headers=headers, params=params)
                    data = res.json()
                    
                    if 'output' in data and data['output']:
                        output = data['output']
                        stock_info = {
                            "name": "삼성전자",
                            "price": output.get('stck_prpr'),
                            "change": output.get('prdy_vrss'),
                            "timestamp": time.time()
                        }
                        producer.send('stock-data', value=stock_info)
                        self.stdout.write(f"✅ 정상 전송: {stock_info['price']}원")
                    else:
                        error_msg = data.get('msg1', '알 수 없는 에러')
                        self.stdout.write(self.style.WARNING(f"⚠️ API 차단됨: {error_msg}"))

                    # 정상일 때는 3초 쉬고 다시 시도 (API 호출 제한 방지)
                    time.sleep(3) 

                except RequestException as e: # 🎯 "인터넷이 끊기거나 에러가 나면?"
                    # 프로그램이 죽지 않게 에러만 출력하고 5초 쉬었다가 다음 루프로 넘어갑니다!
                    self.stdout.write(self.style.ERROR(f"🚨 네트워크 오류 발생 (5초 후 재시도): {e}"))
                    time.sleep(5)
                    continue
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"에러 발생: {e}"))