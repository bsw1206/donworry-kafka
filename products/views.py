# products/views.py (임시 저장 로직 포함)
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import FinancialCompany, Product, ProductOption
from dotenv import load_dotenv
API_KEY = 'FINLIFE_API_KEY'

@api_view(['GET'])
def save_deposit_products(request):
    url = f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'
    response = requests.get(url).json()
    
    # 1. 금융회사 저장
    for co in response['result']['baseList']:
        FinancialCompany.objects.get_or_create(
            fin_co_no=co['fin_co_no'],
            kor_co_nm=co['kor_co_nm']
        )
        
        # 2. 상품 저장
        Product.objects.get_or_create(
            fin_prdt_cd=co['fin_prdt_cd'],
            company_id=co['fin_co_no'],
            fin_prdt_nm=co['fin_prdt_nm'],
            join_way=co['join_way'],
            spcl_cnd=co['spcl_cnd']
        )
        
    # 3. 옵션 저장
    for opt in response['result']['optionList']:
        product = Product.objects.get(fin_prdt_cd=opt['fin_prdt_cd'])
        ProductOption.objects.get_or_create(
            product=product,
            save_trm=opt['save_trm'],
            intr_rate=opt['intr_rate'],
            intr_rate2=opt['intr_rate2']
        )
    return Response({"message": "저장 완료"})

# products/views.py 추가
from rest_framework import generics
from .serializers import ProductSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')