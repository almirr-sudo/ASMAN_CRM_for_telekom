# REST API Endpoints Documentation

## Базовый URL
```
http://localhost:8000/api
```

## Аутентификация

Все API endpoints требуют JWT аутентификацию (кроме `/api/auth/login/`).

### Получить токен:
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Использование токена:
```bash
Authorization: Bearer <access_token>
```

### Обновить токен:
```bash
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

---

## 1. Customers API (`/api/customers/`)

### Базовые операции:
- `GET /api/customers/` - Список клиентов
- `POST /api/customers/` - Создать клиента
- `GET /api/customers/{id}/` - Детали клиента
- `PUT /api/customers/{id}/` - Обновить клиента
- `PATCH /api/customers/{id}/` - Частично обновить клиента
- `DELETE /api/customers/{id}/` - Удалить клиента

### Дополнительные actions:
- `POST /api/customers/{id}/activate/` - Активировать клиента
- `POST /api/customers/{id}/suspend/` - Приостановить обслуживание
- `POST /api/customers/{id}/block/` - Заблокировать клиента
- `GET /api/customers/{id}/contracts/` - Договоры клиента
- `GET /api/customers/{id}/tickets/` - Тикеты клиента
- `GET /api/customers/statistics/` - Статистика по клиентам

### Фильтрация:
- `?status=active` - По статусу
- `?document_type=passport` - По типу документа
- `?search=Иван` - Поиск по имени, телефону, email
- `?ordering=-created_at` - Сортировка

---

## 2. SIMs API (`/api/sims/`)

### Базовые операции:
- `GET /api/sims/` - Список SIM-карт
- `POST /api/sims/` - Создать SIM
- `GET /api/sims/{id}/` - Детали SIM
- `PUT /api/sims/{id}/` - Обновить SIM
- `DELETE /api/sims/{id}/` - Удалить SIM

### Дополнительные actions:
- `POST /api/sims/{id}/activate/` - Активировать SIM
  ```json
  {"contract_id": 1}
  ```
- `POST /api/sims/{id}/deactivate/` - Деактивировать SIM
- `POST /api/sims/{id}/block/` - Заблокировать SIM
- `GET /api/sims/free/` - Список свободных SIM
- `GET /api/sims/statistics/` - Статистика по SIM

### Фильтрация:
- `?status=free` - По статусу
- `?contract=1` - По договору
- `?search=+996550` - Поиск по ICCID, IMSI, MSISDN

---

## 3. Tariffs API (`/api/tariffs/`)

### Базовые операции:
- `GET /api/tariffs/` - Список тарифов
- `POST /api/tariffs/` - Создать тариф
- `GET /api/tariffs/{id}/` - Детали тарифа
- `PUT /api/tariffs/{id}/` - Обновить тариф
- `DELETE /api/tariffs/{id}/` - Удалить тариф

### Дополнительные actions:
- `POST /api/tariffs/{id}/activate/` - Активировать тариф
- `POST /api/tariffs/{id}/deactivate/` - Деактивировать тариф
- `GET /api/tariffs/active/` - Список активных тарифов
- `GET /api/tariffs/{id}/contracts/` - Договоры с этим тарифом
- `GET /api/tariffs/statistics/` - Статистика по тарифам

### Фильтрация:
- `?is_active=true` - Только активные
- `?tariff_type=prepaid` - По типу
- `?search=Безлимит` - Поиск по названию и описанию
- `?ordering=priority` - Сортировка по приоритету

---

## 4. Contracts API (`/api/contracts/`)

### Базовые операции:
- `GET /api/contracts/` - Список договоров
- `POST /api/contracts/` - Создать договор
- `GET /api/contracts/{id}/` - Детали договора
- `PUT /api/contracts/{id}/` - Обновить договор
- `DELETE /api/contracts/{id}/` - Удалить договор

### Дополнительные actions:
- `POST /api/contracts/{id}/activate/` - Активировать договор
  ```json
  {"sim_id": 1}
  ```
- `POST /api/contracts/{id}/suspend/` - Приостановить договор
- `POST /api/contracts/{id}/resume/` - Возобновить договор
- `POST /api/contracts/{id}/terminate/` - Закрыть договор
- `POST /api/contracts/{id}/add_balance/` - Пополнить баланс
  ```json
  {"amount": 1000.00}
  ```
- `POST /api/contracts/{id}/deduct_balance/` - Списать с баланса
  ```json
  {"amount": 500.00}
  ```
- `GET /api/contracts/{id}/payments/` - Платежи по договору
- `GET /api/contracts/{id}/tickets/` - Тикеты по договору
- `GET /api/contracts/statistics/` - Статистика по договорам

### Фильтрация:
- `?status=active` - По статусу
- `?customer=1` - По клиенту
- `?tariff=1` - По тарифу
- `?search=CTR-2024` - Поиск по номеру договора

---

## 5. Payments API (`/api/payments/`)

### Базовые операции:
- `GET /api/payments/` - Список платежей
- `POST /api/payments/` - Создать платеж
- `GET /api/payments/{id}/` - Детали платежа
- `PUT /api/payments/{id}/` - Обновить платеж
- `DELETE /api/payments/{id}/` - Удалить платеж

### Дополнительные actions:
- `POST /api/payments/{id}/process/` - Обработать платеж
- `POST /api/payments/{id}/cancel/` - Отменить платеж
- `POST /api/payments/{id}/fail/` - Отметить как неуспешный
- `GET /api/payments/pending/` - Платежи в обработке
- `GET /api/payments/statistics/` - Статистика по платежам

### Фильтрация:
- `?transaction_type=payment` - Пополнения
- `?transaction_type=charge` - Списания
- `?status=success` - По успешным платежам (поддерживаются также pending, processing, failed, refunded)
- `?payment_method=cash` - По методу оплаты
- `?contract=1` - По договору
- `?search=TXN-123` - Поиск по transaction_id

---

## 6. Tickets API (`/api/tickets/`)

### Базовые операции:
- `GET /api/tickets/` - Список тикетов
- `POST /api/tickets/` - Создать тикет
- `GET /api/tickets/{id}/` - Детали тикета
- `PUT /api/tickets/{id}/` - Обновить тикет
- `DELETE /api/tickets/{id}/` - Удалить тикет

### Дополнительные actions:
- `POST /api/tickets/{id}/assign/` - Назначить сотруднику
  ```json
  {"user_id": 1}
  ```
- `POST /api/tickets/{id}/start_work/` - Начать работу над тикетом
- `POST /api/tickets/{id}/resolve/` - Решить тикет
  ```json
  {"resolution": "Проблема решена путем..."}
  ```
- `POST /api/tickets/{id}/close/` - Закрыть тикет
- `POST /api/tickets/{id}/reopen/` - Переоткрыть тикет
- `GET /api/tickets/my_tickets/` - Мои тикеты (текущего пользователя)
- `GET /api/tickets/unassigned/` - Неназначенные тикеты
- `GET /api/tickets/overdue/` - Просроченные тикеты
- `GET /api/tickets/statistics/` - Статистика по тикетам

### Фильтрация:
- `?status=new` - По статусу
- `?category=technical` - По категории
- `?priority=high` - По приоритету
- `?customer=1` - По клиенту
- `?assigned_to=1` - По исполнителю
- `?search=интернет` - Поиск по теме и описанию

---

## Общие параметры

### Пагинация:
```
?page=2&page_size=50
```

По умолчанию: 100 записей на страницу

### Сортировка:
```
?ordering=-created_at  # По убыванию даты создания
?ordering=name         # По возрастанию имени
```

### Поиск:
```
?search=текст_для_поиска
```

---

## Примеры использования

### 1. Получить список активных клиентов:
```bash
GET /api/customers/?status=active
Authorization: Bearer <token>
```

### 2. Создать нового клиента:
```bash
POST /api/customers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Иван",
  "last_name": "Иванов",
  "middle_name": "Иванович",
  "phone": "+996550123456",
  "email": "ivan@example.com",
  "document_type": "passport",
  "document_number": "ID1234567",
  "passport_issued_by": "МВД КР",
  "passport_issue_date": "2020-01-01",
  "address": "г. Бишкек, ул. Ленина 1"
}
```

### 3. Активировать договор с SIM-картой:
```bash
POST /api/contracts/1/activate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "sim_id": 5
}
```

### 4. Обработать платеж:
```bash
POST /api/payments/10/process/
Authorization: Bearer <token>
```

### 5. Получить статистику по всем тикетам:
```bash
GET /api/tickets/statistics/
Authorization: Bearer <token>
```

---

## Коды ответов HTTP

- `200 OK` - Успешный запрос
- `201 Created` - Объект создан
- `204 No Content` - Успешное удаление
- `400 Bad Request` - Ошибка валидации данных
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Недостаточно прав
- `404 Not Found` - Объект не найден
- `500 Internal Server Error` - Ошибка сервера

---

## Формат ошибок

```json
{
  "status": "error",
  "message": "Описание ошибки"
}
```

Или для валидационных ошибок:
```json
{
  "field_name": ["Сообщение об ошибке"]
}
```
