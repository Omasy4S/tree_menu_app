"""
Модели для хранения древовидного меню в БД.

Используем две модели:
1. Menu - для хранения названий меню (например, 'main_menu', 'footer_menu')
2. MenuItem - для хранения пунктов меню с поддержкой вложенности через parent

Почему именно так:
- Разделение Menu и MenuItem позволяет создавать несколько независимых меню
- parent=ForeignKey('self') создает древовидную структуру с неограниченной вложенностью
- named_url позволяет использовать django named urls вместо явных путей
- order для сортировки пунктов меню на одном уровне
"""
from django.db import models
from django.urls import reverse, NoReverseMatch


class Menu(models.Model):
    """
    Модель для хранения меню.
    Каждое меню имеет уникальное название (slug), по которому оно вызывается в шаблоне.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Название меню',
        help_text='Название меню'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Идентификатор',
        help_text='Уникальный идентификатор для вызова в шаблоне, например: main_menu'
    )

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """
    Модель для хранения пунктов меню.
    
    Ключевые поля:
    - menu: связь с меню, к которому относится пункт
    - parent: ссылка на родительский пункт (None для корневых элементов)
    - title: текст, который отображается в меню
    - url: явный URL (например, '/about/')
    - named_url: именованный URL из urls.py (например, 'home')
    - order: порядок сортировки среди элементов одного уровня
    
    Почему parent=ForeignKey('self'):
    - Позволяет создавать иерархию любой глубины
    - related_name='children' дает удобный доступ к дочерним элементам
    - null=True, blank=True означает, что корневые элементы не имеют родителя
    """
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Меню'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский пункт',
        help_text='Оставьте пустым для пункта верхнего уровня'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Название пункта'
    )
    url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='URL',
        help_text='Явный URL, например: /about/'
    )
    named_url = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Именованный URL',
        help_text='Имя URL из urls.py, например: home'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки',
        help_text='Чем меньше число, тем выше в списке'
    )

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order', 'id']  # Сортируем по order, затем по id для стабильности

    def __str__(self):
        return self.title

    def get_url(self):
        """
        Возвращает URL для пункта меню.
        
        Логика:
        1. Если задан named_url, пытаемся получить URL через reverse()
        2. Если named_url не задан или reverse() не сработал, возвращаем url
        3. Если ничего не задано, возвращаем '#'
        
        Почему именно так:
        - named_url имеет приоритет, т.к. это более гибкий подход
        - try/except для NoReverseMatch обрабатывает случай несуществующего named_url
        - Возврат '#' предотвращает битые ссылки
        """
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                pass
        return self.url if self.url else '#'
