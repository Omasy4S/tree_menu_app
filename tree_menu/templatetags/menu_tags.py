"""
Template tags для отрисовки древовидного меню.

КЛЮЧЕВОЕ ТРЕБОВАНИЕ: Ровно 1 запрос к БД на каждое меню.

Как это достигается:
1. select_related('menu', 'parent') - подгружает связанные объекты в одном запросе
2. Все пункты меню загружаются сразу одним запросом
3. Построение дерева происходит в Python, без дополнительных запросов к БД

Почему именно так:
- Без select_related каждое обращение к item.menu или item.parent вызывало бы отдельный запрос
- Загрузка всех пунктов сразу позволяет построить дерево в памяти
- Это эффективнее, чем делать запросы для каждого уровня вложенности
"""
from django import template
from django.utils.safestring import mark_safe
from tree_menu.models import MenuItem

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_slug):
    """
    Template tag для отрисовки меню.
    
    Использование в шаблоне:
    {% load menu_tags %}
    {% draw_menu 'main_menu' %}
    
    Параметры:
    - context: контекст шаблона (автоматически передается Django)
    - menu_slug: идентификатор меню (slug из модели Menu)
    
    Возвращает:
    - HTML-код меню в виде вложенных <ul>/<li>
    
    Почему takes_context=True:
    - Нужен доступ к request для определения текущего URL
    - request.path используется для определения активного пункта меню
    """
    # Получаем текущий путь из request
    request = context.get('request')
    current_path = request.path if request else ''
    
    # ЕДИНСТВЕННЫЙ ЗАПРОС К БД
    # select_related подгружает связанные menu и parent в одном запросе
    # filter по menu__slug выбирает только нужное меню
    menu_items = MenuItem.objects.filter(
        menu__slug=menu_slug
    ).select_related('menu', 'parent')
    
    # Если меню не найдено, возвращаем пустую строку
    if not menu_items:
        return ''
    
    # Строим дерево из плоского списка пунктов меню
    # Это делается в Python, без дополнительных запросов к БД
    menu_dict = build_menu_tree(menu_items)
    
    # Определяем активный пункт и путь к нему
    active_item = find_active_item(menu_items, current_path)
    active_path = get_active_path(active_item) if active_item else set()
    
    # Генерируем HTML
    html = render_menu_level(menu_dict, None, active_item, active_path)
    
    return mark_safe(html)


def build_menu_tree(menu_items):
    """
    Строит словарь для быстрого доступа к дочерним элементам.
    
    Структура: {parent_id: [child1, child2, ...]}
    None в качестве ключа означает корневые элементы (без родителя)
    
    Почему словарь:
    - O(1) доступ к дочерним элементам по parent_id
    - Не нужны дополнительные запросы к БД
    - Удобно для рекурсивной отрисовки
    
    """
    menu_dict = {}
    for item in menu_items:
        parent_id = item.parent_id
        if parent_id not in menu_dict:
            menu_dict[parent_id] = []
        menu_dict[parent_id].append(item)
    return menu_dict


def find_active_item(menu_items, current_path):
    """
    Находит активный пункт меню на основе текущего URL.
    
    Логика:
    1. Проходим по всем пунктам меню
    2. Сравниваем get_url() каждого пункта с current_path
    3. Возвращаем первый совпавший пункт
    
    Почему именно так:
    - get_url() обрабатывает и named_url, и явный url
    - Сравнение с current_path определяет, на какой странице мы находимся
    - Первое совпадение достаточно (обычно URL уникальны)
    """
    for item in menu_items:
        if item.get_url() == current_path:
            return item
    return None


def get_active_path(item):
    """
    Получает путь от корня до активного элемента.
    
    Возвращает set с ID всех элементов от корня до активного.
    
    Почему set:
    - Быстрая проверка принадлежности (O(1))
    - Используется для определения, какие элементы нужно развернуть
    
    Почему нужен путь:
    - По требованию: "Все, что над выделенным пунктом - развернуто"
    - Путь показывает, какие родительские элементы нужно показать
    
    Пример:
    Если активен item5, а иерархия: item1 -> item3 -> item5
    Вернет: {item1.id, item3.id, item5.id}
    """
    path = set()
    current = item
    while current:
        path.add(current.id)
        current = current.parent
    return path


def render_menu_level(menu_dict, parent_id, active_item, active_path, level=0):
    """
    Рекурсивно отрисовывает уровень меню.
    
    Параметры:
    - menu_dict: словарь с деревом меню
    - parent_id: ID родительского элемента (None для корня)
    - active_item: активный пункт меню
    - active_path: set с ID элементов от корня до активного
    - level: текущий уровень вложенности (для отладки/стилизации)
    
    Логика раскрытия:
    1. Корневой уровень (level=0) - всегда показываем
    2. Элемент в active_path - показываем (путь к активному элементу)
    3. Прямой потомок активного элемента - показываем (первый уровень под активным)
    4. Остальное - скрываем
    
    Почему именно так:
    - Требование: "Все, что над выделенным пунктом - развернуто" -> active_path
    - Требование: "Первый уровень вложенности под выделенным пунктом тоже развернут" -> is_child_of_active
    - display:none для скрытых элементов (можно заменить на CSS классы)
    """
    # Получаем дочерние элементы текущего уровня
    items = menu_dict.get(parent_id, [])
    if not items:
        return ''
    
    html = '<ul class="menu-level-{}">\n'.format(level)
    
    for item in items:
        # Проверяем, является ли элемент активным
        is_active = active_item and item.id == active_item.id
        
        # Проверяем, находится ли элемент на пути к активному
        is_in_path = item.id in active_path
        
        # Проверяем, является ли элемент прямым потомком активного
        is_child_of_active = active_item and item.parent_id == active_item.id
        
        # CSS класс для активного элемента
        css_class = 'active' if is_active else ''
        
        # Начало элемента списка
        html += '  <li class="{}">\n'.format(css_class)
        html += '    <a href="{}">{}</a>\n'.format(item.get_url(), item.title)
        
        # Рекурсивно отрисовываем дочерние элементы
        children_html = render_menu_level(
            menu_dict, 
            item.id, 
            active_item, 
            active_path, 
            level + 1
        )
        
        if children_html:
            # Определяем, нужно ли показывать дочерние элементы
            # Показываем если:
            # 1. Элемент на пути к активному (is_in_path)
            # 2. Элемент - прямой потомок активного (is_child_of_active)
            should_show = is_in_path or is_child_of_active
            
            if should_show:
                html += children_html
            else:
                # Скрываем через inline style (в продакшене лучше использовать CSS классы)
                html += '<div style="display:none;">\n' + children_html + '</div>\n'
        
        html += '  </li>\n'
    
    html += '</ul>\n'
    return html
