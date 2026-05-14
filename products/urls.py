# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 데이터 수집용: http://127.0.0.1:8000/api/products/save/
    path('products/save/', views.save_deposit_products),
    
    # 목록 조회용: http://127.0.0.1:8000/api/products/
    path('products/', views.ProductListView.as_view()),

    path('api/stock-chart-data/', views.stock_chart_data, name='stock_chart_data'),
]