import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import FinancialCompany, Product, ProductOption

class Command(BaseCommand):
    help = '금감원 API에서 금융 상품(정기예금, 적금, 연금저축) 데이터를 가져와 DB에 적재합니다.'

    def handle(self, *args, **kwargs):
        # settings.py에 선언한 FINLIFE_API_KEY를 가져옵니다.
        api_key = getattr(settings, 'FINLIFE_API_KEY', None)
        self.stdout.write(self.style.WARNING(f"현재 인식된 API 키: [{api_key}]"))
        if not api_key:
            self.stdout.write(self.style.ERROR("API 키가 설정되지 않았습니다. .env 파일과 settings.py를 확인해주세요."))
            return

        # 1. 수집할 3가지 상품 API URL 목록
        endpoints = {
            'deposit': f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1',
            'saving': f'http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1',
            'pension': f'http://finlife.fss.or.kr/finlifeapi/annuitySavingProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1'
        }

        # 2. 각 URL을 순회하며 데이터 수집 및 적재 실행
        for product_type, url in endpoints.items():
            self.stdout.write(f"{product_type} 데이터 수집 시작...")
            self.fetch_and_save(url, product_type)
        
        self.stdout.write(self.style.SUCCESS("모든 데이터 적재가 완료되었습니다!"))

    def fetch_and_save(self, url, product_type):
        response = requests.get(url).json()
        
        try:
            result = response.get('result', {})
            base_list = result.get('baseList', [])
            option_list = result.get('optionList', [])
        except AttributeError:
            self.stdout.write(self.style.ERROR(f"{product_type} 데이터를 불러오는데 실패했습니다."))
            return

        # 3. 데이터 적재 (baseList -> optionList 순서 보장)
        for base in base_list:
            company, _ = FinancialCompany.objects.get_or_create(
                fin_co_no=base.get('fin_co_no'),
                defaults={'kor_co_nm': base.get('kor_co_nm')}
            )

            # 최대 한도 금액(max_limit)이 null로 오는 경우 처리
            max_limit = base.get('max_limit')
            if max_limit is not None:
                max_limit = int(max_limit)

            Product.objects.update_or_create(
                fin_prdt_cd=base.get('fin_prdt_cd'),
                defaults={
                    'company': company,
                    'product_type': product_type,
                    'fin_prdt_nm': base.get('fin_prdt_nm'),
                    'join_way': base.get('join_way'),
                    'join_member': base.get('join_member'),
                    'join_deny': int(base.get('join_deny', 1)),
                    'spcl_cnd': base.get('spcl_cnd'),
                    'etc_note': base.get('etc_note'),
                    'max_limit': max_limit,
                    'dcls_month': base.get('dcls_month'),
                    'dcls_strt_day': base.get('dcls_strt_day'),
                    'dcls_end_day': base.get('dcls_end_day'),
                    # 적금/연금저축 전용 필드 처리
                    'rsrv_type': base.get('rsrv_type') if product_type == 'saving' else None,
                    'prft_strc': base.get('prft_strc') if product_type == 'pension' else None,
                }
            )

        for option in option_list:
            try:
                product = Product.objects.get(fin_prdt_cd=option.get('fin_prdt_cd'))
                ProductOption.objects.update_or_create(
                    product=product,
                    save_trm=int(option.get('save_trm', 0) or 0),
                    intr_rate_type=option.get('intr_rate_type', ''),
                    defaults={
                        # 금리가 null로 올 경우 -1로 대체 (화면 표시할 때 필터링 용도)
                        'intr_rate': option.get('intr_rate') or -1,
                        'intr_rate2': option.get('intr_rate2') or -1,
                    }
                )
            except Product.DoesNotExist:
                continue