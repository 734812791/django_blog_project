from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import ArticleList, MyArticle, ArticleDetail, CreateArticle, CreateArticleSuccess, DeleteArticle, \
    CreateComment, create_comment, SearchArticle, search_article_by_keyword, search_article_by_tag, delete_comment, \
    UpdateArticle

app_name = 'article'

urlpatterns = [
    path('article_list/', ArticleList.as_view(), name='article_list'),
    path('my_article/<str:user>/', MyArticle.as_view(), name='my_article'),
    path('article_detail/<str:article>/', ArticleDetail.as_view(), name='article_detail'),
    path('create_article/', CreateArticle.as_view(), name='create_article'),
    path('create_article_success/', CreateArticleSuccess.as_view(), name='create_article_success'),
    path('delete_article/<str:pk>/', DeleteArticle.as_view(), name='delete_article'),
    path('create_comment/<str:article>/', create_comment, name='create_comment'),
    path('search_article/<str:keyword>/', SearchArticle.as_view(), name='search_article'),
    path('search_article_by_keyword/', search_article_by_keyword, name='search_article_by_keyword'),
    path('search_article_by_tag/<str:tag_name>/', search_article_by_tag, name='search_article_by_tag'),
    path('delete_comment/<str:comment_id>/<str:article_id>/', delete_comment, name='delete_comment'),
    path('update_article/<str:pk>/', UpdateArticle.as_view(), name='update_article'),
]

