"""
Настройка админ-панели для управления меню.

Почему используется TabularInline:
- Позволяет редактировать пункты меню прямо на странице меню
- Удобнее, чем переходить на отдельную страницу для каждого пункта
- Видно всю структуру меню сразу

Почему list_display включает parent и menu:
- parent показывает иерархию (какой элемент является дочерним)
- menu позволяет видеть, к какому меню относится пункт
- order показывает порядок сортировки

Почему list_filter по menu:
- Удобно фильтровать пункты по конкретному меню
- Особенно полезно, когда меню много
"""
from django.contrib import admin
from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    """
    Inline для редактирования пунктов меню прямо на странице меню.
    
    TabularInline отображает элементы в виде таблицы.
    extra=1 означает, что будет показана одна пустая форма для добавления нового пункта.
    """
    model = MenuItem
    extra = 1
    fields = ('title', 'parent', 'url', 'named_url', 'order')
    # Показываем подсказки для полей
    autocomplete_fields = []


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    """
    Админка для модели Menu.
    
    prepopulated_fields автоматически заполняет slug на основе name
    (работает через JavaScript в админке).
    """
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MenuItemInline]  # Встраиваем форму для пунктов меню


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Админка для модели MenuItem.
    
    Почему нужна отдельная админка, если есть inline:
    - Inline удобен для быстрого добавления пунктов
    - Отдельная админка нужна для детального редактирования
    - Позволяет искать и фильтровать пункты меню
    
    list_display показывает основные поля в списке:
    - menu: к какому меню относится
    - title: название пункта
    - parent: родительский элемент (для понимания иерархии)
    - order: порядок сортировки
    - get_url: фактический URL (метод из модели)
    """
    list_display = ('title', 'menu', 'parent', 'order', 'get_url')
    list_filter = ('menu',)  # Фильтр по меню
    search_fields = ('title',)  # Поиск по названию
    list_editable = ('order',)  # Можно менять order прямо в списке
    
    # Группировка полей в форме редактирования для удобства
    fieldsets = (
        ('Основная информация', {
            'fields': ('menu', 'title', 'parent', 'order')
        }),
        ('URL настройки', {
            'fields': ('url', 'named_url'),
            'description': 'Укажите либо явный URL, либо именованный URL. '
                          'Именованный URL имеет приоритет.'
        }),
    )
