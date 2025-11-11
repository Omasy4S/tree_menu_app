"""
URL конфигурация проекта.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tree_menu.urls')),  # Подключаем URLs нашего приложения
]
