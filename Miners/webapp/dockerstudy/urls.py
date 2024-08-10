from django.urls import path, re_path

from . import views

app_name = 'dockerstudy'

urlpatterns = [
    path('image/', views.request_image, name='post_image'),
    path('create_image/', views.create_image, name='create_image'),
    path('dockerhub_user/', views.request_dockerhub_user, name='dockerhub_user'),
    path('image_name_crawler_task/', views.request_image_name_crawler, name='image_name_crawler_task'),
    path('authtoken/github', views.request_github_authtoken, name='request_github_authtoken'),
    path('authtoken/bitbucket', views.request_bitbucket_authtoken, name='request_bitbucket_authtoken'),
    path('authtoken/', views.request_update_authtoken, name='request_update_authtoken'),
    path('image_and_repo_info_crawler_task/', views.request_image_and_repo_info_crawler, name='image_and_repo_info_crawler_task'),
    path('repository/', views.request_repository, name='request_repository'),
    path('query_repository/<str:repo_location>/<str:repo_owner>/<str:repo_name>/', views.query_repository, name='query_repository'),
]