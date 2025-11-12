"""
Скрипт для тестирования REST API endpoints.

Проверяет доступность всех основных маршрутов API.
"""

import requests
from pprint import pprint

BASE_URL = "http://localhost:8000/api"

# Список всех endpoints для проверки
ENDPOINTS = {
    'Customers': f'{BASE_URL}/customers/',
    'SIMs': f'{BASE_URL}/sims/',
    'Tariffs': f'{BASE_URL}/tariffs/',
    'Contracts': f'{BASE_URL}/contracts/',
    'Payments': f'{BASE_URL}/payments/',
    'Tickets': f'{BASE_URL}/tickets/',
}

# Custom actions для проверки
CUSTOM_ACTIONS = {
    'Customer Statistics': f'{BASE_URL}/customers/statistics/',
    'SIM Free List': f'{BASE_URL}/sims/free/',
    'SIM Statistics': f'{BASE_URL}/sims/statistics/',
    'Tariff Active List': f'{BASE_URL}/tariffs/active/',
    'Tariff Statistics': f'{BASE_URL}/tariffs/statistics/',
    'Contract Statistics': f'{BASE_URL}/contracts/statistics/',
    'Payment Pending': f'{BASE_URL}/payments/pending/',
    'Payment Statistics': f'{BASE_URL}/payments/statistics/',
    'Ticket Unassigned': f'{BASE_URL}/tickets/unassigned/',
    'Ticket Statistics': f'{BASE_URL}/tickets/statistics/',
}

def test_endpoint(name, url):
    """Проверка доступности endpoint"""
    try:
        response = requests.get(url, timeout=5)
        status = response.status_code

        if status == 200:
            print(f"✅ {name}: {status} - OK")
            return True
        elif status == 401:
            print(f"🔐 {name}: {status} - Authentication required (expected)")
            return True
        elif status == 403:
            print(f"🔒 {name}: {status} - Permission denied (expected)")
            return True
        else:
            print(f"⚠️  {name}: {status} - Unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection failed - Server not running?")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("REST API Endpoints Test")
    print("=" * 60)
    print()

    print("Testing main endpoints:")
    print("-" * 60)
    success_count = 0
    total_count = 0

    for name, url in ENDPOINTS.items():
        total_count += 1
        if test_endpoint(name, url):
            success_count += 1

    print()
    print("Testing custom actions:")
    print("-" * 60)

    for name, url in CUSTOM_ACTIONS.items():
        total_count += 1
        if test_endpoint(name, url):
            success_count += 1

    print()
    print("=" * 60)
    print(f"Results: {success_count}/{total_count} endpoints accessible")
    print("=" * 60)

    if success_count == total_count:
        print("\n✅ All API endpoints are working correctly!")
    else:
        print(f"\n⚠️  {total_count - success_count} endpoint(s) failed")

if __name__ == "__main__":
    main()
