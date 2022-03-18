from django.contrib import admin
from django.urls import path, include

from single_pages import views

urlpatterns = [
    path('about_me/', views.about_me),
    path('', views.landing),
]
