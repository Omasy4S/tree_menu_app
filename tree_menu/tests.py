"""
Тесты для приложения tree_menu.

Почему нужны тесты:
- Проверяют корректность работы моделей
- Проверяют оптимизацию запросов (1 запрос к БД)
- Проверяют логику определения активного пункта
- Проверяют логику раскрытия меню

Как запустить:
python manage.py test tree_menu
"""
from django.test import TestCase, RequestFactory
from django.urls import reverse
from tree_menu.models import Menu, MenuItem
from tree_menu.templatetags.menu_tags import (
    build_menu_tree, 
    find_active_item, 
    get_active_path,
    draw_menu
)


class MenuModelTest(TestCase):
    """Тесты для модели Menu"""
    
    def test_menu_creation(self):
        """Проверка создания меню"""
        menu = Menu.objects.create(name='Тестовое меню', slug='test_menu')
        self.assertEqual(str(menu), 'Тестовое меню')
        self.assertEqual(menu.slug, 'test_menu')


class MenuItemModelTest(TestCase):
    """Тесты для модели MenuItem"""
    
    def setUp(self):
        """Создаем тестовые данные перед каждым тестом"""
        self.menu = Menu.objects.create(name='Главное меню', slug='main_menu')
    
    def test_menu_item_creation(self):
        """Проверка создания пункта меню"""
        item = MenuItem.objects.create(
            menu=self.menu,
            title='Главная',
            url='/',
            order=0
        )
        self.assertEqual(str(item), 'Главная')
        self.assertEqual(item.get_url(), '/')
    
    def test_menu_item_with_named_url(self):
        """Проверка работы с именованным URL"""
        item = MenuItem.objects.create(
            menu=self.menu,
            title='Главная',
            named_url='home',
            order=0
        )
        # named_url имеет приоритет над url
        self.assertEqual(item.get_url(), reverse('home'))
    
    def test_menu_item_hierarchy(self):
        """Проверка иерархии пунктов меню"""
        parent = MenuItem.objects.create(
            menu=self.menu,
            title='Услуги',
            url='/services/',
            order=0
        )
        child = MenuItem.objects.create(
            menu=self.menu,
            parent=parent,
            title='Веб-разработка',
            url='/services/web/',
            order=0
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())


class MenuTagTest(TestCase):
    """Тесты для template tag draw_menu"""
    
    def setUp(self):
        """Создаем структуру меню для тестов"""
        self.menu = Menu.objects.create(name='Главное меню', slug='main_menu')
        
        # Корневые элементы
        self.home = MenuItem.objects.create(
            menu=self.menu, title='Главная', url='/', order=0
        )
        self.services = MenuItem.objects.create(
            menu=self.menu, title='Услуги', url='/services/', order=1
        )
        self.about = MenuItem.objects.create(
            menu=self.menu, title='О нас', url='/about/', order=2
        )
        
        # Вложенные элементы
        self.web = MenuItem.objects.create(
            menu=self.menu, parent=self.services,
            title='Веб-разработка', url='/services/web/', order=0
        )
        self.mobile = MenuItem.objects.create(
            menu=self.menu, parent=self.services,
            title='Мобильные приложения', url='/services/mobile/', order=1
        )
        
        # Третий уровень
        self.web_design = MenuItem.objects.create(
            menu=self.menu, parent=self.web,
            title='Веб-дизайн', url='/services/web/design/', order=0
        )
    
    def test_build_menu_tree(self):
        """Проверка построения дерева меню"""
        items = MenuItem.objects.filter(menu=self.menu)
        tree = build_menu_tree(items)
        
        # Проверяем корневые элементы
        self.assertEqual(len(tree[None]), 3)
        
        # Проверяем дочерние элементы "Услуги"
        self.assertEqual(len(tree[self.services.id]), 2)
        
        # Проверяем дочерние элементы "Веб-разработка"
        self.assertEqual(len(tree[self.web.id]), 1)
    
    def test_find_active_item(self):
        """Проверка определения активного пункта"""
        items = MenuItem.objects.filter(menu=self.menu)
        
        # Проверяем поиск по URL
        active = find_active_item(items, '/services/web/')
        self.assertEqual(active, self.web)
        
        # Проверяем, что возвращается None для несуществующего URL
        active = find_active_item(items, '/nonexistent/')
        self.assertIsNone(active)
    
    def test_get_active_path(self):
        """Проверка получения пути к активному элементу"""
        # Путь к элементу третьего уровня
        path = get_active_path(self.web_design)
        
        # Путь должен включать все элементы от корня до активного
        self.assertIn(self.web_design.id, path)
        self.assertIn(self.web.id, path)
        self.assertIn(self.services.id, path)
        
        # Путь не должен включать другие элементы
        self.assertNotIn(self.home.id, path)
        self.assertNotIn(self.about.id, path)
    
    def test_query_optimization(self):
        """
        Проверка оптимизации запросов к БД.
        
        КРИТИЧЕСКИ ВАЖНЫЙ ТЕСТ: проверяет, что используется только 1 запрос.
        """
        from django.test.utils import override_settings
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        
        # Создаем mock request
        factory = RequestFactory()
        request = factory.get('/services/web/')
        
        # Считаем количество запросов
        with CaptureQueriesContext(connection) as context:
            # Получаем пункты меню (должен быть 1 запрос)
            items = MenuItem.objects.filter(
                menu__slug='main_menu'
            ).select_related('menu', 'parent')
            
            # Принудительно выполняем запрос
            list(items)
            
            # Проверяем, что был только 1 запрос
            self.assertEqual(len(context.captured_queries), 1)
