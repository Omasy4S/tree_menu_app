"""
URL конфигурация приложения tree_menu.

Создаем несколько URL для демонстрации:
1. Корневые страницы (home, about, services, contact)
2. Вложенные страницы (service_detail) для демонстрации иерархии

Почему используем name:
- name позволяет использовать named_url в модели MenuItem
- Это более гибко, чем явные URL (можно менять путь, не меняя меню)
- Пример: {% url 'home' %} или reverse('home')
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('services/<str:service_name>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
