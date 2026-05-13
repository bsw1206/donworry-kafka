from django.db import models
from django.conf import settings

class FinancialCompany(models.Model):
    fin_co_no = models.CharField(max_length=100, primary_key=True) # 금융사 코드
    kor_co_nm = models.CharField(max_length=100) # 한글명
    homp_url = models.URLField(max_length=200, blank=True, null=True) # 공식 홈페이지
    cal_tel = models.CharField(max_length=50, blank=True, null=True) # 콜센터 번호

class Product(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, primary_key=True) # 상품 코드
    company = models.ForeignKey(FinancialCompany, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=20) # deposit, saving, pension
    fin_prdt_nm = models.CharField(max_length=100) # 상품명
    join_way = models.TextField(blank=True, null=True) # 가입 방법
    join_member = models.TextField(blank=True, null=True) # 가입 대상
    join_deny = models.IntegerField(default=1) # 가입 제한
    spcl_cnd = models.TextField(blank=True, null=True) # 우대금리 조건
    etc_note = models.TextField(blank=True, null=True) # 유의사항
    max_limit = models.BigIntegerField(blank=True, null=True) # 최대 가입 금액
    dcls_month = models.CharField(max_length=6) # 공시 제출월
    dcls_strt_day = models.CharField(max_length=8) # 공시 시작일
    dcls_end_day = models.CharField(max_length=8, blank=True, null=True) # 공시 종료일
    
    # 적금 전용 (null 허용)
    rsrv_type = models.CharField(max_length=10, blank=True, null=True) 
    # 연금저축 전용 (null 허용)
    prft_strc = models.CharField(max_length=100, blank=True, null=True) 

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    intr_rate_type = models.CharField(max_length=5) # 단리(S), 복리(M)
    save_trm = models.IntegerField() # 가입 기간(개월)
    intr_rate = models.FloatField(blank=True, null=True) # 기본금리
    intr_rate2 = models.FloatField(blank=True, null=True) # 최고금리

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product') # 중복 찜 방지