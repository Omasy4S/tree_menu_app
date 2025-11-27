# Django Древовидное Меню

Django приложение для создания древовидных меню с оптимизацией запросов к БД.

## Быстрый старт

### Windows (PowerShell)

```powershell
# 1. Создание виртуального окружения
python -m venv venv

# 2. Активация виртуального окружения
venv\Scripts\activate

# 3. Установка зависимостей (выполняйте в активированном окружении!)
pip install -r requirements.txt

# 4. Применение миграций
python manage.py migrate

# 5. Создание суперпользователя (для доступа в админку)
python manage.py createsuperuser

# 6. Создание демо-меню (опционально)
python manage.py create_demo_menu

# 7. Запуск сервера
python manage.py runserver
```

### Windows (без активации venv)

Если не хотите активировать окружение каждый раз, можно запускать напрямую:

```powershell
# Установка зависимостей
venv\Scripts\pip.exe install -r requirements.txt

# Миграции
venv\Scripts\python.exe manage.py migrate

# Создание суперпользователя
venv\Scripts\python.exe manage.py createsuperuser

# Создание демо-меню
venv\Scripts\python.exe manage.py create_demo_menu

# Запуск сервера
venv\Scripts\python.exe manage.py runserver
```

### Linux / macOS

```bash
# 1. Создание виртуального окружения
python3 -m venv venv

# 2. Активация виртуального окружения
source venv/bin/activate

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Применение миграций
python manage.py migrate

# 5. Создание суперпользователя
python manage.py createsuperuser

# 6. Создание демо-меню (опционально)
python manage.py create_demo_menu

# 7. Запуск сервера
python manage.py runserver
```

### Проверка работы

После запуска откройте в браузере:
- **Сайт:** http://127.0.0.1:8000/
- **Админка:** http://127.0.0.1:8000/admin/

> ⚠️ **Важно:** Все команды после `pip install` должны выполняться либо в активированном виртуальном окружении, либо через полный путь к Python (`venv\Scripts\python.exe` на Windows).

## Использование

### В шаблоне

```django
{% load menu_tags %}
{% draw_menu 'main_menu' %}
```

### Создание меню в админке

1. Перейдите в `/admin/` → **Меню** → **Добавить меню**
2. Укажите название и slug (например, `main_menu`)
3. Добавьте пункты меню:
   - **title** - текст пункта
   - **parent** - родительский пункт (пусто для корневых)
   - **url** - явный URL (`/about/`)
   - **named_url** - именованный URL (`about`) - имеет приоритет
   - **order** - порядок сортировки

## Ключевые особенности

### 1. Один запрос к БД

```python
# Все данные загружаются одним запросом через select_related
menu_items = MenuItem.objects.filter(
    menu__slug=menu_slug
).select_related('menu', 'parent')
```

**Почему это работает:**
- `select_related()` делает JOIN с таблицами menu и parent
- Построение дерева происходит в Python без дополнительных запросов
- Нет N+1 проблемы

### 2. Умное раскрытие меню

**Логика:**
- Корневой уровень - всегда развернут
- Путь к активному пункту - развернут
- Первый уровень под активным - развернут
- Остальное - скрыто

**Реализация:**
```python
def get_active_path(item):
    """Строит путь от корня до активного элемента"""
    path = set()
    current = item
    while current:
        path.add(current.id)
        current = current.parent
    return path
```

### 3. Определение активного пункта

Сравнивается `request.path` с URL каждого пункта меню:

```python
def find_active_item(menu_items, current_path):
    for item in menu_items:
        if item.get_url() == current_path:
            return item
    return None
```

## Структура проекта

```
tree_menu_app/
├── config/              # Настройки Django
│   ├── settings.py
│   └── urls.py
├── tree_menu/           # Приложение меню
│   ├── models.py        # Menu, MenuItem
│   ├── admin.py         # Админка
│   ├── templatetags/
│   │   └── menu_tags.py # Template tag draw_menu
│   └── management/
│       └── commands/
│           └── create_demo_menu.py
└── templates/           # Демо-шаблоны
```

## Модели

**Menu** - контейнер для меню
- `name` - название
- `slug` - уникальный идентификатор

**MenuItem** - пункт меню
- `menu` - ForeignKey на Menu
- `parent` - ForeignKey на себя (для иерархии)
- `title` - текст пункта
- `url` / `named_url` - URL пункта
- `order` - порядок сортировки

## Требования задания

✅ Меню реализовано через template tag  
✅ Все, что над выделенным пунктом - развернуто  
✅ Первый уровень вложенности под выделенным пунктом тоже развернут  
✅ Хранится в БД  
✅ Редактируется в стандартной админке Django  
✅ Активный пункт меню определяется исходя из URL текущей страницы  
✅ Меню на одной странице может быть несколько  
✅ При клике на меню происходит переход по заданному URL  
✅ На отрисовку каждого меню требуется ровно 1 запрос к БД  

## Технические детали

### Почему ForeignKey('self')?

Позволяет создавать иерархию любой глубины без дополнительных библиотек:

```python
parent = models.ForeignKey(
    'self',
    null=True,
    blank=True,
    related_name='children'
)
```

### Почему именованные URL имеют приоритет?

```python
def get_url(self):
    if self.named_url:
        try:
            return reverse(self.named_url)
        except NoReverseMatch:
            pass
    return self.url if self.url else '#'
```

Если изменить путь в `urls.py`, меню обновится автоматически.

## Тестирование

```bash
# Запуск тестов
python manage.py test tree_menu

# Проверка оптимизации запросов
python manage.py test tree_menu.MenuTagTest.test_query_optimization
```

## Зависимости

- Python 3.8+
- Django 4.2+

Только Django, без сторонних библиотек.
