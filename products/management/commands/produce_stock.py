# apps/management/commands/produce_stock.py
import json
import time
from django.core.management.base import BaseCommand
from kafka import KafkaProducer
import requests  # 한국투자증권 API 호출용
import os

def get_access_token():
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
                print("🚀 API 응답 원본:", data)
                # 필요한 정보만 파싱 (현재가, 종목명 등)
                output = data.get('output', {})
                stock_info = {
                    "name": "삼성전자",
                    "price": output.get('stck_prpr'), # 현재가
                    "change": output.get('prdy_vrss'), # 전일 대비
                    "timestamp": time.time()
                }

                producer.send('stock-data', value=stock_info)
                self.stdout.write(f"Kafka 전송 완료: {stock_info['price']}원")
                
                time.sleep(2) # API 호출 제한을 고려해 2초 간격
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"에러 발생: {e}"))