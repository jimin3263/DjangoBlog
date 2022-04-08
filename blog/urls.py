from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()),
    path('category/<str:slug>/', views.show_category_post),
    path('tag/<str:slug>/', views.show_tag_post)
]