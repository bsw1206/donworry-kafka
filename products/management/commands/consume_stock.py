import json
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from products.models import Stock
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
            # 🎯 여기서 가져온 데이터를 DB에 저장하거나 가공하면 됩니다!
            self.stdout.write(self.style.SUCCESS(f"받은 데이터: {data}"))

            stock_obj, created = Stock.objects.update_or_create(
                code="005930", # 삼성전자 코드
                defaults={
                    "name": data.get("name"),
                    "current_price": data.get("price"),
                    "change": data.get("change"),
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"새 종목 등록: {stock_obj.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"가격 갱신 완료: {stock_obj.current_price}원"))