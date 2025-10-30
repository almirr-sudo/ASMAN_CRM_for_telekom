# Telecom CRM - Система управления оператора связи

CRM-система для управления абонентами, SIM-картами, тарифами, договорами и платежами телекоммуникационного оператора.

## Технологический стек

- **Backend**: Django 5.0, Django REST Framework
- **Frontend**: HTMX + TailwindCSS
- **База данных**: PostgreSQL 16 (prod), SQLite (dev)
- **Задачи**: Celery + Redis
- **Аутентификация**: JWT (djangorestframework-simplejwt)

## Структура проекта

```
telecom_crm/
├── apps/                      # Django приложения
│   ├── customers/            # Управление абонентами
│   ├── sims/                 # Управление SIM-картами
│   ├── tariffs/              # Управление тарифами
│   ├── contracts/            # Управление договорами
│   ├── payments/             # Управление платежами
│   ├── tickets/              # Техподдержка
│   └── users/                # Пользователи и права доступа
├── telecom_crm/              # Основной проект
│   ├── settings.py           # Настройки Django
│   ├── urls.py               # Маршруты
│   ├── wsgi.py               # WSGI
│   └── celery.py             # Celery конфигурация
├── templates/                # HTML шаблоны
├── static/                   # Статические файлы
├── media/                    # Загружаемые файлы
├── requirements.txt          # Зависимости Python
├── manage.py                 # Django CLI
└── .env                      # Переменные окружения
```

## Установка и запуск (разработка)

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd "PROCESSES Asman"
```

### 2. Создание виртуального окружения

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте параметры:

```bash
cp .env.example .env
```

Для разработки можно использовать значения по умолчанию (SQLite).

### 5. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера разработки

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

Админ-панель: http://127.0.0.1:8000/admin/

API: http://127.0.0.1:8000/api/

## Работа с API

### Получение JWT токена

```bash
POST /api/auth/login/
{
  "username": "your_username",
  "password": "your_password"
}
```

Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Использование токена

Добавьте заголовок в запросы:
```
Authorization: Bearer <access_token>
```

### Основные эндпоинты

- `GET /api/customers/` - Список абонентов
- `POST /api/customers/` - Создание абонента
- `GET /api/sims/` - Список SIM-карт
- `GET /api/tariffs/` - Список тарифов
- `GET /api/contracts/` - Список договоров
- `GET /api/payments/` - Список платежей
- `GET /api/tickets/` - Список заявок

## Разработка

### Запуск Celery (для асинхронных задач)

**Windows:**
```bash
celery -A telecom_crm worker -l info --pool=solo
```

**Linux/Mac:**
```bash
celery -A telecom_crm worker -l info
```

### Запуск тестов

```bash
pytest
```

### Форматирование кода

```bash
black .
flake8
```

## Развертывание (Production)

### Docker Compose

1. Настройте `.env` для production:
```bash
DEBUG=False
DATABASE_ENGINE=postgresql
DB_NAME=telecom_crm_prod
DB_USER=postgres
DB_PASSWORD=<strong_password>
```

2. Запустите контейнеры:
```bash
docker-compose up -d
```

3. Примените миграции:
```bash
docker-compose exec web python manage.py migrate
```

4. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Документация

- **CLAUDE.md** - Руководство для работы с Claude Code
- **TODO.md** - Список задач для реализации
- **Техническое задание** - `тех-задание.pdf`
- **Диаграммы** - `diagrams.pdf`

## Роли пользователей

- **Admin** - Полный доступ ко всем функциям
- **Supervisor** - Просмотр отчетов и аналитики
- **Operator** - Управление абонентами, SIM, договорами
- **Employee** - Ограниченный доступ к базовым функциям

## Лицензия

Проект разработан для внутреннего использования.

## Контакты

Для вопросов и предложений создавайте issues в репозитории.
