# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Обзор проекта

Это учебный проект CRM-системы для телекоммуникационного оператора связи, разработанный студентами ПИ(англ)-2-23 КГТУ. Система демонстрирует бизнес-процессы оператора: управление абонентами, SIM-картами, тарифами, договорами, платежами и тикетами поддержки.

## Технологический стек

- **Backend**: Django 5.x, Django REST Framework (DRF)
- **Frontend**: HTMX + TailwindCSS
- **База данных**: PostgreSQL 16 (prod), SQLite (dev)
- **Язык**: Python 3.12
- **Deployment**: Docker Compose

## Основные команды разработки

### Локальная разработка

```bash
# Активация виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Миграции базы данных
python manage.py makemigrations
python manage.py migrate

# Заполнение тестовыми данными
python manage.py seed

# Запуск dev сервера
python manage.py runserver
```

### Production/Demo окружение

```bash
# Запуск через Docker Compose
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f
```

### Тестирование

```bash
# Запуск всех тестов
python manage.py test

# Запуск тестов конкретного приложения
python manage.py test <app_name>

# Запуск с покрытием
coverage run --source='.' manage.py test
coverage report
```

## Архитектура системы

### Основные модули (приложения Django)

1. **customers** - Управление абонентами
2. **sims** - Управление SIM-картами и номерами
3. **tariffs** - Тарифные планы и опции
4. **contracts** - Договоры и активация услуг
5. **payments** - Платежи и управление балансом
6. **tickets** - Тикеты поддержки
7. **users** - Аутентификация и роли (ACL)

### Основные сущности и их связи

- **Customer** (Абонент) - 1:N → Contract
- **SIM** - 1:1 → Contract (nullable)
- **Tariff** (Тариф) - 1:N → Contract
- **Contract** (Договор) - N:1 → Customer, 1:1 → SIM, N:1 → Tariff
- **Payment** (Платеж) - N:1 → Contract
- **Ticket** (Тикет) - N:1 → Customer

### Потоки данных (по DFD диаграммам)

**A0 - Контекстная диаграмма:**
- Входы: Raw Data, Confirmations, Documents, Requests, Tickets
- Управление: Polices, Rules, Catalogs, Regulations
- Выходы: Contracts, Statuses, Statements, Notifications, Reports
- Механизмы: Customer, Services, DB, I/E tools

**A1-A5 - Декомпозиция:**
1. **Manage Customers (A1)** → формирует List of Customers
2. **Manage SIM and Tariffs (A2)** → выдаёт Accepted Contract и Statuses
3. **Process Contracts and Activation (A3)** → создаёт Contracts, Statements, Activated Contract
4. **Handle Payments and Balance (A4)** → отправляет Notifications и Bills
5. **Analytics and Reports (A5)** → генерирует Reports

### API структура (DRF endpoints)

```
/api/customers/         - CRUD абонентов
/api/sims/              - CRUD SIM-карт
/api/tariffs/           - CRUD тарифов
/api/contracts/         - CRUD договоров
/api/payments/          - CRUD платежей
/api/tickets/           - CRUD тикетов
/api/auth/              - Аутентификация
```

Все эндпоинты поддерживают:
- Фильтрацию (по статусам, датам, связанным объектам)
- Поиск (по ключевым полям)
- Пагинацию

## Роли и права доступа

- **Admin** - полный доступ ко всем функциям
- **Operator** - работа с абонентами, договорами, SIM
- **Supervisor** - просмотр отчетов и контроль операторов
- **Employee** - базовый доступ к просмотру данных

## Бизнес-логика

### Статусы договоров
- `active` - активный договор
- `suspended` - приостановлен
- `closed` - закрыт

### Статусы SIM
- `free` - свободна, не привязана
- `active` - активна и привязана к договору
- `blocked` - заблокирована

### Статусы тикетов
- `Free` → `Active` → `Suspended` → `Active` → `Blocked` → `Closed`

### Биллинг
- Автоматическое списание абонплаты по расписанию
- Пополнение баланса через платежи
- Транзакции обрабатываются атомарно

## Импорт/Экспорт данных

Система поддерживает массовый импорт/экспорт:
- Формат: CSV (UTF-8, Windows-1251)
- Разделители: запятая, точка с запятой, табуляция
- Проверка уникальности и корректности данных
- Детальные отчеты об ошибках импорта

## Конфигурация через .env

```
SECRET_KEY=<django secret key>
DB_URL=<database connection string>
DEBUG=<True|False>
ALLOWED_HOSTS=<comma-separated hosts>
```

## Особенности разработки

1. **Целостность данных**: используйте транзакции Django для операций с платежами и договорами
2. **Валидация**: все модели имеют встроенную валидацию полей
3. **История изменений**: критические операции логируются с timestamps
4. **Индексация**: ключевые поля (ICCID, MSISDN, phone, email) индексированы для быстрого поиска
5. **Безопасность**: CSRF-защита, хеширование паролей (bcrypt), аудит действий

## Диаграммы процессов

Основные UML диаграммы последовательности:
- **GetSim()** - процесс регистрации абонента и выдачи SIM-карты
- **GetDeposit()** - процесс пополнения счета
- **ManyRegister()** - массовая загрузка абонентов из CSV
- **TicketStatus()** - жизненный цикл тикета поддержки

## Ограничения и риски

- Система является учебной, без реальных телеком-интеграций
- Биллинг упрощен, без сложных алгоритмов тарификации
- Нагрузка эмулируется, не соответствует реальным условиям
- Рассчитана на до 50,000 абонентов и SIM-карт
- Возможны задержки при больших объемах данных без оптимизации

## Структура базы данных

### Customer (Абонент)
- `id` - PK, UUID или int
- `firstname`, `lastname` - ФИО
- `phone` - уникальный телефон
- `document_type`, `document_number` - тип и номер документа
- `email` - для уведомлений
- `status` - статус абонента
- `created_at`, `updated_at` - timestamps

### SIM
- `id` - PK
- `iccid` - уникальный идентификатор SIM
- `imsi` - идентификатор в сети оператора
- `msisdn` - номер SIM (индексируется)
- `status` - free/active/blocked
- `contract_id` - FK на договор (nullable)
- `activated_at`, `deactivated_at` - даты активации/деактивации

### Contract (Договор)
- `id` - PK
- `number` - номер договора
- `customer_id` - FK на абонента
- `sim_id` - FK на SIM
- `tariff_id` - FK на тариф
- `status` - active/suspended/closed
- `start_date`, `end_date` - период действия
- `total_cost` - общая стоимость

### Payment (Платеж)
- `id` - PK
- `contract_id` - FK на договор
- `amount` - сумма
- `method` - метод оплаты
- `date` - дата платежа
- `status` - статус обработки

## Тестирование

Система требует покрытия тестами:
- Юнит-тесты моделей и валидации
- Интеграционные тесты API эндпоинтов
- Тесты бизнес-процессов (создание договора, платеж, привязка SIM)
- Тесты импорта/экспорта данных
- Нагрузочные тесты (50k+ записей)

## Документация

Основные документы:
- `тех-задание.pdf` - техническое задание с полным описанием требований
- `diagrams.pdf` - IDEF0, DFD, UML диаграммы процессов
- API документация генерируется автоматически (Swagger/OpenAPI)
