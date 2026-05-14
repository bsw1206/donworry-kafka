# products/serializers.py
from rest_framework import serializers
from .models import Product, ProductOption

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    bank_name = serializers.CharField(source='company.kor_co_nm', read_only=True)

    class Meta:
        model = Product
        fields = ['fin_prdt_cd', 'bank_name', 'fin_prdt_nm', 'options']

