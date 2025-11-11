"""
Management команда для создания демонстрационного меню.

Использование:
python manage.py create_demo_menu

Почему это полезно:
- Быстрое создание тестовых данных
- Демонстрация структуры меню с несколькими уровнями вложенности
- Удобно для проверяющих тестовое задание

Что создается:
Главное меню (main_menu) с трехуровневой иерархией
"""
from django.core.management.base import BaseCommand
from tree_menu.models import Menu, MenuItem


class Command(BaseCommand):
    help = 'Создает демонстрационное меню для тестирования'

    def handle(self, *args, **options):
        """
        Основная логика команды.
        
        Почему используется get_or_create:
        - Позволяет запускать команду многократно без ошибок
        - Не создает дубликаты, если меню уже существует
        """
        self.stdout.write('Создание демонстрационного меню...')
        
        # Создаем главное меню
        main_menu, created = Menu.objects.get_or_create(
            slug='main_menu',
            defaults={'name': 'Главное меню'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Создано меню "Главное меню"'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Меню "Главное меню" уже существует'))
            # Удаляем старые пункты для пересоздания
            MenuItem.objects.filter(menu=main_menu).delete()
            self.stdout.write('  Старые пункты меню удалены')
        
        # Создаем корневые пункты главного меню
        home = MenuItem.objects.create(
            menu=main_menu,
            title='Главная',
            named_url='home',
            order=0
        )
        self.stdout.write('  ✓ Создан пункт "Главная"')
        
        about = MenuItem.objects.create(
            menu=main_menu,
            title='О нас',
            named_url='about',
            order=1
        )
        self.stdout.write('  ✓ Создан пункт "О нас"')
        
        services = MenuItem.objects.create(
            menu=main_menu,
            title='Услуги',
            named_url='services',
            order=2
        )
        self.stdout.write('  ✓ Создан пункт "Услуги"')
        
        contact = MenuItem.objects.create(
            menu=main_menu,
            title='Контакты',
            named_url='contact',
            order=3
        )
        self.stdout.write('  ✓ Создан пункт "Контакты"')
        
        # Создаем вложенные пункты под "Услуги"
        web_dev = MenuItem.objects.create(
            menu=main_menu,
            parent=services,
            title='Веб-разработка',
            url='/services/web-development/',
            order=0
        )
        self.stdout.write('    ✓ Создан подпункт "Веб-разработка"')
        
        mobile_dev = MenuItem.objects.create(
            menu=main_menu,
            parent=services,
            title='Мобильные приложения',
            url='/services/mobile-apps/',
            order=1
        )
        self.stdout.write('    ✓ Создан подпункт "Мобильные приложения"')
        
        consulting = MenuItem.objects.create(
            menu=main_menu,
            parent=services,
            title='Консалтинг',
            url='/services/consulting/',
            order=2
        )
        self.stdout.write('    ✓ Создан подпункт "Консалтинг"')
        
        support = MenuItem.objects.create(
            menu=main_menu,
            parent=services,
            title='Поддержка',
            url='/services/support/',
            order=3
        )
        self.stdout.write('    ✓ Создан подпункт "Поддержка"')
        
        # Создаем третий уровень вложенности под "Веб-разработка"
        frontend = MenuItem.objects.create(
            menu=main_menu,
            parent=web_dev,
            title='Frontend разработка',
            url='/services/frontend/',
            order=0
        )
        self.stdout.write('      ✓ Создан подпункт 3-го уровня "Frontend разработка"')
        
        backend = MenuItem.objects.create(
            menu=main_menu,
            parent=web_dev,
            title='Backend разработка',
            url='/services/backend/',
            order=1
        )
        self.stdout.write('      ✓ Создан подпункт 3-го уровня "Backend разработка"')
        
        # Итоговая статистика
        main_count = MenuItem.objects.filter(menu=main_menu).count()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Демонстрационное меню успешно создано!'
        ))
        self.stdout.write(f'   Создано пунктов: {main_count}')
        self.stdout.write('\nТеперь откройте http://127.0.0.1:8000/ для просмотра')
