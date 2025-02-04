import os
import uuid

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse

from .models import Article, Comment, Tag
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView

from .models import User

#函数视图，创建评论
def create_comment(request, article):

    comment_id = uuid.uuid4()
    article_id = article
    images = request.FILES.getlist('images')
    user_id = request.POST.get('user_id')
    content = request.POST.get('content')

    # 将数据保存到blog_comment表
    sql_query = """
                  INSERT INTO blog_comment(comment_id,user_id,content,article_id)
                  VALUES(%s, %s, %s, %s)
              """
    with connection.cursor() as cursor:
         cursor.execute(sql_query, [comment_id, user_id, content, article_id])

    for image in images:
         image_id = uuid.uuid4()
         # 获取文件的原始文件名
         file_name = image.name

         # 设置保存文件的路径（例如将文件保存到 'media/uploads/' 文件夹中）
         save_path = os.path.join('media/uploads/', file_name)

         # 如果目标文件夹不存在，创建它
         if not os.path.exists(os.path.dirname(save_path)):
              os.makedirs(os.path.dirname(save_path))

         # 将文件保存到指定路径
         with open(save_path, 'wb+') as destination:
              for chunk in image.chunks():
                   destination.write(chunk)

         # 设置数据库中保存的文件路径
         save_path = os.path.join('uploads', file_name)
         # 将文件路径保存到数据库
         sql_query = """
                   INSERT INTO blog_image_path
                   VALUES (%s, %s)
               """

         with connection.cursor() as cursor:
              cursor.execute(sql_query, [image_id, save_path])

         # 将数据保存到blog_comment_image_path表
         sql_query = """
                                  INSERT INTO blog_comment_image_path
                                  VALUES (%s, %s)
                              """
         with connection.cursor() as cursor:
              cursor.execute(sql_query, [comment_id, image_id])


    return redirect('article:article_detail', article_id)

#根据关键词查询
def search_article_by_keyword(request):

    keyword = request.POST.get('keyword')
    return redirect('article:search_article', keyword)

#根据tag名查询
def search_article_by_tag(request, tag_name):

    return redirect('article:search_article', tag_name)

#删除评论
def delete_comment(request, comment_id, article_id):

     # 删除blog_image_path中的数据，通过级联删除blog_comment_image_path中数据
     sql_query = """
                       DELETE FROM blog_image_path
                       WHERE image_path_id IN (SELECT image_path_id FROM blog_comment_image_path 
                                               WHERE comment_id = %s)
                   """
     with connection.cursor() as cursor:
          cursor.execute(sql_query, [comment_id])

     # 删除评论本身
     sql_query = """
                       DELETE FROM blog_comment
                       WHERE comment_id = %s
                   """
     with connection.cursor() as cursor:
          cursor.execute(sql_query, [comment_id])

     # return render(request, 'article_detail.html', {'article_id': article_id})
     return redirect('article:article_detail', article_id)

#获取所有文章列表
class ArticleList(LoginRequiredMixin, ListView):

     template_name = 'article_list.html'

     def get_queryset(self):
          # articles = Article.objects.all()
          # 使用raw()
          sql = '''
                    SELECT image_path,ba.*,bu.name FROM blog_article AS ba
                    LEFT JOIN blog_article_image_path AS baip
                    ON ba.article_id = baip.article_id
                    LEFT JOIN blog_image_path AS bip
                    ON bip.image_path_id = baip.image_path_id
                    LEFT JOIN blog_user AS bu
                    ON bu.user_id = ba.user_id
                    GROUP BY ba.article_id
                    ORDER BY ba.created_at DESC
                    '''
          articles = Article.objects.raw(sql)
          return articles

     def get_context_data(self, *, object_list=None, **kwargs):
          context = super().get_context_data(**kwargs)

          # 获取tag
          sql = '''
                    SELECT image_path,ba.*,bu.name FROM blog_article AS ba
                    LEFT JOIN blog_article_image_path AS baip
                    ON ba.article_id = baip.article_id
                    LEFT JOIN blog_image_path AS bip
                    ON bip.image_path_id = baip.image_path_id
                    LEFT JOIN blog_user AS bu
                    ON bu.user_id = ba.user_id
                    GROUP BY ba.article_id
                    ORDER BY ba.created_at DESC
                    '''
          articles = Article.objects.raw(sql)

          MEDIA_URL = settings.MEDIA_URL
          context['MEDIA_URL'] = MEDIA_URL  # 手动传递 MEDIA_URL
          context['articles'] = articles

          return context

#根据用户id查询文章
class MyArticle(LoginRequiredMixin, ListView):
     template_name = 'my_article.html'
     # paginate_by = 9

     def get_queryset(self):
          user_id = self.kwargs['user']
          # my_article = Article.objects.filter(user_id=user_id).order_by('-created_at')
          sql = '''
                    SELECT image_path,ba.* FROM blog_article AS ba
                    LEFT JOIN blog_article_image_path AS baip
                    ON ba.article_id = baip.article_id
                    LEFT JOIN blog_image_path AS bip
                    ON bip.image_path_id = baip.image_path_id
                    WHERE ba.user_id = %s
                    GROUP BY ba.article_id
                    ORDER BY ba.created_at DESC
                    '''
          my_article = Article.objects.raw(sql, [user_id])
          return my_article

     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)

          user_id = self.kwargs['user']
          # 获取用户数据
          sql_query = """
                         SELECT * FROM blog_user
                         WHERE user_id = %s
                        """
          user = User.objects.get(user_id=user_id)

          context['MEDIA_URL'] = settings.MEDIA_URL # 手动传递 MEDIA_URL
          context['own_articles_user'] = user
          return context

#根据文章id获取id详情
class ArticleDetail(LoginRequiredMixin, ListView):

     template_name = 'article_detail.html'

     def get_queryset(self):
          article_id = self.kwargs['article']

          article_detail = Article.objects.filter(article_id=article_id)

          return article_detail

     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          article_id = self.kwargs['article']

          #获取图片地址
          sql = '''
                    SELECT image_path,ba.article_id FROM blog_article AS ba
                    LEFT JOIN blog_article_image_path AS baip
                    ON ba.article_id = baip.article_id
                    LEFT JOIN blog_image_path AS bip
                    ON bip.image_path_id = baip.image_path_id
                    WHERE ba.article_id = %s
                    '''

          image_paths = Article.objects.raw(sql, [article_id])

          #获取作者信息

          sql = '''
                    SELECT bu.name,ba.article_id,bu.user_id FROM blog_user AS bu
                    RIGHT JOIN blog_article AS ba
                    ON bu.`user_id` = ba.`user_id`
                    WHERE ba.article_id = %s
                    '''
          author = Article.objects.raw(sql, [article_id])

          # 获取评论信息

          sql = '''
                    SELECT bc.*,bu.name FROM blog_comment AS bc
                    LEFT JOIN blog_user AS bu
                    ON bc.user_id = bu.user_id
                    WHERE article_id = %s
                    ORDER BY created_at ASC
                    '''
          comments = Comment.objects.raw(sql, [article_id])

          #获取评论的图片信息
          sql = '''
                              SELECT bc.`comment_id`,bcip.*,bip.* FROM blog_comment AS bc
                              LEFT JOIN blog_user AS bu
                              ON bc.user_id = bu.user_id
                              LEFT JOIN blog_comment_image_path AS bcip
                              ON bcip.comment_id = bc.`comment_id`
                              LEFT JOIN blog_image_path AS bip
                              ON bcip.`image_path_id` = bip.`image_path_id`
                              WHERE article_id = %s
                              '''
          comments_pictures = Comment.objects.raw(sql, [article_id])

          # 获取tag信息

          sql = '''
                    SELECT bt.`tag_name`,ba.article_id FROM blog_article AS ba
                    LEFT JOIN blog_tag_article AS bta
                    ON ba.article_id = bta.article_id
                    LEFT JOIN blog_tag AS bt
                    ON bta.tag_id = bt.tag_id
                    WHERE ba.article_id = %s
                    '''
          tags = Article.objects.raw(sql, [article_id])

          # 添加额外的上下文数据
          context['image_paths'] = image_paths  # 通过 context 传递文章详细信息
          context['MEDIA_URL'] = settings.MEDIA_URL # 手动传递 MEDIA_URL
          context['author'] = author  # 手动传递 author_name
          context['comments'] = comments  # 手动传递 comments
          context['tags'] = tags  # 手动传递 tags
          context['comments_pictures'] = comments_pictures  # 手动传递 comments_pictures

          return context

#创建文章
class CreateArticle(LoginRequiredMixin, CreateView):

     template_name = 'create_article.html'
     model = Article
     fields = ['title', 'content']
     success_url = reverse_lazy('article:create_article_success')

     def get_context_data(self, **kwargs):

          #查询所有tag
          tags = Tag.objects.all()

          context = super().get_context_data(**kwargs)
          context['tags'] = tags
          return context

     def form_valid(self, form):
          new_article = form.save(commit=False)
          new_article.user_id = self.request.user.user_id
          new_article.article_id = uuid.uuid4()

          new_article.save()

          # 获取用户上传的图片集合
          images = self.request.FILES.getlist('images')

          # 遍历集合，将图片保存到本地，并将文件名保存到数据库
          for image in images:
               # 获取文件的原始文件名
               file_name = image.name

               # 设置保存文件的路径（例如将文件保存到 'media/uploads/' 文件夹中）
               save_path = os.path.join('media/uploads/', file_name)

               # 如果目标文件夹不存在，创建它
               if not os.path.exists(os.path.dirname(save_path)):
                    os.makedirs(os.path.dirname(save_path))

               # 将文件保存到指定路径
               with open(save_path, 'wb+') as destination:
                    for chunk in image.chunks():
                         destination.write(chunk)

               # 设置数据库中保存的文件路径
               save_path = os.path.join('uploads', file_name)
               # 将文件路径保存到数据库
               sql_query = """
                         INSERT INTO blog_image_path
                         VALUES (%s, %s)
                     """
               image_id = uuid.uuid4()
               with connection.cursor() as cursor:
                    cursor.execute(sql_query, [image_id, save_path])

               # 将数据保存到blog_article_image_path表
               sql_query = """
                                        INSERT INTO blog_article_image_path
                                        VALUES (%s, %s)
                                    """
               with connection.cursor() as cursor:
                    cursor.execute(sql_query, [new_article.article_id, image_id])

          # 将数据保存到blog_tag_article表

          tag_ids = self.request.POST.getlist('tags')

          for tag_id in tag_ids:
               sql_query = """
                                                  INSERT INTO blog_tag_article
                                                  VALUES (%s, %s)
                                              """
               with connection.cursor() as cursor:
                    cursor.execute(sql_query, [tag_id, new_article.article_id])

          return super().form_valid(form)

#创建文章成功页面
class CreateArticleSuccess(LoginRequiredMixin, TemplateView):

     template_name = 'create_article_success.html'

#删除文章
class DeleteArticle(LoginRequiredMixin, DeleteView):

     template_name = 'delete_article.html'
     model = Article

     # 重写get_success_url方法，跳转回用户文章界面
     def get_success_url(self):
          # 获取当前用户的用户名或其他标识
          user_id = self.request.user.user_id
          # 使用 reverse_lazy 并传递 user 参数
          return reverse_lazy('article:my_article', kwargs={'user': user_id})

     # 重写delete方法，删除文章和图片,评论和评论图片通过级联自动删除
     def delete(self, request, *args, **kwargs):
          # 获取要删除的文章对象
          article = self.get_object()


          # 删除blog_image_path中的数据，通过级联删除blog_article_image_path中数据
          sql_query = """
                       DELETE FROM blog_image_path
                       WHERE image_path_id IN (SELECT image_path_id FROM blog_article_image_path 
                                               WHERE article_id = %s)
                   """
          with connection.cursor() as cursor:
               cursor.execute(sql_query, [article.article_id])


          with connection.cursor() as cursor:
               # 删除与tag关联表中的数据
               sql = 'DELETE FROM blog_tag_article WHERE article_id = %s'
               cursor.execute(sql, [article.article_id])

          # 删除文章本身（调用父类的 delete 方法）
          response = super().delete(request, *args, **kwargs)

          return response

#给文章添加评论，该视图已弃用，更换为函数视图
class CreateComment(LoginRequiredMixin, CreateView):

     template_name = 'create_comment.html'
     model = Comment
     fields = ['content']
     success_url = reverse_lazy('article:create_article_success')

     def form_valid(self, form):
          new_comment = form.save(commit=False)
          new_comment.article_id = self.request.POST.get('article_id')
          new_comment.user_id = self.request.user.user_id
          new_comment.comment_id = uuid.uuid4()

          new_comment.save()

          # 获取用户上传的图片集合
          images = self.request.FILES.getlist('images')

          # 遍历集合，将图片保存到本地，并将文件名保存到数据库
          for image in images:
               # 获取文件的原始文件名
               file_name = image.name

               # 设置保存文件的路径（例如将文件保存到 'media/uploads/' 文件夹中）
               save_path = os.path.join('uploads', file_name)

               # 如果目标文件夹不存在，创建它
               if not os.path.exists(os.path.dirname(save_path)):
                    os.makedirs(os.path.dirname(save_path))

               # 将文件保存到指定路径
               with open(save_path, 'wb+') as destination:
                    for chunk in image.chunks():
                         destination.write(chunk)

               # 将文件路径保存到数据库
               sql_query = """
                         INSERT INTO blog_image_path
                         VALUES (%s, %s)
                     """
               image_id = uuid.uuid4()
               with connection.cursor() as cursor:
                    cursor.execute(sql_query, [image_id, save_path])

               # 将数据保存到blog_comment_image_path表
               sql_query = """
                                        INSERT INTO blog_comment_image_path
                                        VALUES (%s, %s)
                                    """
               with connection.cursor() as cursor:
                    cursor.execute(sql_query, [new_comment.comment_id, image_id])

          return super().form_valid(form)

#根据关键字查询文章
class SearchArticle(LoginRequiredMixin, ListView):

     template_name = 'search_article.html'

     def get_queryset(self):
          keyword = self.kwargs['keyword']
          print(keyword)

          sql = '''
                    SELECT image_path,ba.*,bu.name,bt.tag_name FROM blog_article AS ba
                    LEFT JOIN blog_article_image_path AS baip
                    ON ba.article_id = baip.article_id
                    LEFT JOIN blog_image_path AS bip
                    ON bip.image_path_id = baip.image_path_id
                    LEFT JOIN blog_user AS bu
                    ON bu.user_id = ba.user_id
                    LEFT JOIN blog_tag_article AS bta
                    ON ba.article_id = bta.article_id
                    LEFT JOIN blog_tag AS bt
                    ON bta.tag_id = bt.tag_id
                    WHERE ba.`title` LIKE %s OR ba.`content` LIKE %s OR bt.`tag_name` LIKE %s OR bu.`name` LIKE %s
                    GROUP BY ba.article_id
                    ORDER BY ba.created_at DESC
                    '''

          articles = Article.objects.raw(sql, ['%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'])
          return articles

     def get_context_data(self, **kwargs):

          context = super().get_context_data(**kwargs)
          context['MEDIA_URL'] = settings.MEDIA_URL # 手动传递 MEDIA_URL

          return context

#修改文章
class UpdateArticle(LoginRequiredMixin, UpdateView):
     template_name = 'update_article.html'
     model = Article
     fields = ['title', 'content']

     def get_success_url(self):

          user_id = self.request.POST.get('user_id')
          # 根据条件动态生成重定向 URL
          return reverse('article:my_article', kwargs={'user': user_id})






