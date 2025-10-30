"""
Скрипт для создания суперпользователя
"""
import os
import sys
import django

# Установка кодировки UTF-8 для вывода
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telecom_crm.settings')
django.setup()

from apps.users.models import User

# Параметры суперпользователя
username = 'admin'
email = 'admin@telecom-crm.local'
password = 'admin123'

# Проверяем, существует ли уже пользователь
if User.objects.filter(username=username).exists():
    print(f'[!] Пользователь "{username}" уже существует!')
    user = User.objects.get(username=username)
    print(f'    Email: {user.email}')
    print(f'    Роль: {user.get_role_display()}')
else:
    # Создаем суперпользователя
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='admin'
    )
    print('[OK] Суперпользователь успешно создан!')
    print(f'    Имя пользователя: {username}')
    print(f'    Email: {email}')
    print(f'    Пароль: {password}')
    print(f'    Роль: {user.get_role_display()}')
    print()
    print('Теперь вы можете войти в админ-панель:')
    print('http://127.0.0.1:8000/admin/')
