from django.contrib.auth.models import AbstractUser
from django.db import models

# 05_pjt 요구사항에 맞춘 커스텀 유저 모델
class User(AbstractUser):
    # 기본 username, email, password 등은 AbstractUser가 제공
    nickname = models.CharField(max_length=20, blank=True, null=True)
    # 관심 상품/종목 등을 저장 (05_pjt 참고)
    interest_stocks = models.CharField(max_length=200, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

# plan.md에 설계된 사용자 부가 정보 (설문 기반 추천용)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age_group = models.CharField(max_length=10, blank=True, null=True)
    income_level = models.CharField(max_length=20, blank=True, null=True)
    risk_type = models.CharField(max_length=20, blank=True, null=True)
    goal_period = models.CharField(max_length=20, blank=True, null=True)
    survey_done = models.BooleanField(default=False)