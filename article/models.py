from django.db import models

from user.models import User


class Article(models.Model):

    article_id = models.CharField(max_length=50, primary_key=True)
    user_id = models.CharField(max_length=30)
    # user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(vars(self))

    class Meta:
        db_table = 'blog_article'  # 映射到现有的表名
        managed = False  # Django 不会对这个表执行迁移操作

class Comment(models.Model):

    comment_id = models.CharField(max_length=50, primary_key=True)
    user_id = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    article_id = models.CharField(max_length=50)

    class Meta:
        db_table = 'blog_comment'  # 映射到现有的表名
        managed = False  # Django 不会对这个表执行迁移操作

class Tag(models.Model):

    tag_id = models.CharField(max_length=50, primary_key=True)
    tag_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'blog_tag'  # 映射到现有的表名
        managed = False  # Django 不会对这个表执行迁移操作