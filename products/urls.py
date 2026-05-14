from django.contrib import admin
from django.urls import path, include
from products import views

# products/urls.py
urlpatterns = [
    # 기존: path('products/save/', ...) -> 접속: /api/products/save/
    path('save/', views.save_deposit_products), 

    # 기존: path('products/', ...) -> 접속: /api/products/
    path('', views.ProductListView.as_view()),

    # ✨ 차트 데이터 경로 (깔끔하게!)
    # 이제 접속 주소는: /api/stock-chart-data/ 가 됩니다.
    path('stock-chart-data/', views.stock_chart_data, name='stock_chart_data'),
]