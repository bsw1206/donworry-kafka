import json
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from products.models import Stock, StockHistory
class Command(BaseCommand):
    help = 'Kafka에서 주식 데이터를 가져옵니다.'

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            'stock-data', # 구독할 토픽 이름
            bootstrap_servers=['127.0.0.1:9092'],
            auto_offset_reset='earliest', # 처음부터 읽기
            enable_auto_commit=True,
            group_id='django-group-1', # 컨슈머 그룹
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        self.stdout.write(self.style.SUCCESS('데이터 수신 대기 중...'))

        for message in consumer:
            data = message.value
            stock_code = "005930"
            # 🎯 1. 데이터 타입 정제 (문자열 -> 정수)
            current_price = int(data.get("price", 0)) 
            
            # 🎯 2. 기존 가격과 비교하기 (최적화)
            # DB에서 현재 저장된 삼성전자의 정보를 가져옵니다.
            try:
                stock_obj = Stock.objects.get(code=stock_code)
                last_price = stock_obj.current_price
            except Stock.DoesNotExist:
                stock_obj = None
                last_price = None

            # 🎯 3. 가격이 변했을 때만 동작!
            if stock_obj is None or last_price != current_price:
                # Stock 테이블 업데이트 또는 생성
                stock_obj, created = Stock.objects.update_or_create(
                    code=stock_code,
                    defaults={
                        "name": data.get("name"),
                        "current_price": current_price,
                        "change": data.get("change"),
                    }
                )
                
                # 가격이 변했으니 이력(History)에도 남깁니다.
                StockHistory.objects.create(
                    stock=stock_obj,
                    price=current_price
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"📢 새 종목 등록: {stock_obj.name}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"🔄 가격 변동 감지! 갱신 완료: {current_price}원"))
            
            # 🎯 2. 가격이 그대로일 때 실행되는 구역
            else:
                self.stdout.write(f"😴 가격 변동 없음 ({current_price}원). 기록을 건너뜁니다.")