"""
URL configuration for donworry project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

