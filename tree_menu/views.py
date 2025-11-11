"""
Views для демонстрации работы меню.

Создаем несколько простых страниц, чтобы показать:
1. Как меню отображается на разных страницах
2. Как определяется активный пункт
3. Как работает раскрытие/скрытие уровней

Почему используем TemplateView:
- Простые страницы без сложной логики
- Нужно только отобразить шаблон
- TemplateView - стандартный Django подход для таких случаев
"""
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'pages/home.html'


class AboutView(TemplateView):
    """Страница "О нас" """
    template_name = 'pages/about.html'


class ServicesView(TemplateView):
    """Страница "Услуги" """
    template_name = 'pages/services.html'


class ServiceDetailView(TemplateView):
    """Страница конкретной услуги"""
    template_name = 'pages/service_detail.html'
    
    def get_context_data(self, **kwargs):
        """Добавляем название услуги в контекст"""
        context = super().get_context_data(**kwargs)
        context['service_name'] = kwargs.get('service_name', 'Услуга')
        return context


class ContactView(TemplateView):
    """Страница контактов"""
    template_name = 'pages/contact.html'
