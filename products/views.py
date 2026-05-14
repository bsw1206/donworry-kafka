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
    # 1. DB에서 삼성전자 데이터 꺼내오기
    try:
        samsung_stock = Stock.objects.get(code='005930')
    except Stock.DoesNotExist:
        samsung_stock = None

    # 2. HTML로 넘겨줄 보따리(context)에 담기
    context = {
        'samsung_stock': samsung_stock, 
    }
    
    # 3. 보따리 들고 index.html로 출발!
    return render(request, 'products/index.html', context)

# products/views.py
from django.shortcuts import render
from .models import Stock, StockHistory

def product_list(request):
    # DB에서 삼성전자 데이터를 가져옵니다.
    # 만약 아직 데이터가 없을 경우를 대비해 None 처리를 해줍니다.
    try:
        samsung_stock = Stock.objects.get(code='005930')
    except Stock.DoesNotExist:
        samsung_stock = None

    context = {
        'samsung_stock': samsung_stock,
        # 기존에 팀원이 넘겨주던 데이터들...
    }
    return render(request, 'products/product_list.html', context)

# products/views.py
from django.http import JsonResponse

def stock_chart_data(request):
    # 최근 20개의 가격 데이터를 가져옵니다.
    histories = StockHistory.objects.filter(stock__code='005930').order_by('-created_at')[:20]
    data = {
        "labels": [h.created_at.strftime('%H:%M:%S') for h in reversed(histories)],
        "prices": [h.price for h in reversed(histories)],
    }
    return JsonResponse(data)