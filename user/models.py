import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class CustomUserManager(UserManager):
    def get_by_natural_key(self, account):
        return self.get(account=account)  # 通过account获取用户

class User(AbstractBaseUser):

    USERNAME_FIELD = 'account'

    user_id = models.CharField(primary_key=True, max_length=50)
    email = models.CharField(max_length=30, null=True, blank=True)
    account = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=30,)
    name = models.CharField(max_length=50, null=True, blank=True)
    profile_picture_path = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()  # 使用自定义管理器

    def __str__(self):
        return str(vars(self))

    class Meta:
        db_table = 'blog_user'  # 映射到现有的表名
        managed = False  # Django 不会对这个表执行迁移操作
