# products/models.py
from django.db import models

class FinancialCompany(models.Model):
    fin_co_no = models.CharField(max_length=20, primary_key=True)
    kor_co_nm = models.CharField(max_length=100)

class Product(models.Model):
    fin_prdt_cd = models.CharField(max_length=50, primary_key=True)
    company = models.ForeignKey(FinancialCompany, on_delete=models.CASCADE)
    fin_prdt_nm = models.CharField(max_length=100)
    join_way = models.TextField(null=True)
    spcl_cnd = models.TextField(null=True)

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    save_trm = models.IntegerField()  # 저축 기간
    intr_rate = models.FloatField(null=True)  # 기본 금리
    intr_rate2 = models.FloatField(null=True) # 최고 우대 금리

# products/models.py 수정

class Stock(models.Model):
    code = models.CharField(max_length=20, primary_key=True)  # 종목 코드 (예: 005930)
    name = models.CharField(max_length=50)                   # 종목명 (예: 삼성전자)
    current_price = models.IntegerField(null=True)           # 현재가
    change = models.IntegerField(null=True)                  # 전일 대비 변동폭
    updated_at = models.DateTimeField(auto_now=True)         # 데이터 갱신 시간

    def __str__(self):
        return f"{self.name} ({self.code})"