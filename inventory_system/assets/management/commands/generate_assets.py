from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from assets.models import Asset, Department
from users.models import CustomUser  # если твоя модель пользователя так называется


class Command(BaseCommand):
    help = "Создаёт 100 тестовых материальных ценностей"

    def handle(self, *args, **options):
        departments = list(Department.objects.all())
        managers = list(CustomUser.objects.filter(role="DEPARTMENT_HEAD"))

        if not departments or not managers:
            self.stdout.write(self.style.ERROR("Сначала нужно создать подразделения и менеджеров!"))
            return

        Asset.objects.all().delete()

        sample_names = [
            "Ноутбук", "Принтер", "Сканер", "Монитор", "Клавиатура",
            "Мышь", "Телефон", "Планшет", "Сервер", "Проектор",
            "Маршрутизатор", "Сетевой кабель", "ИБП", "Кофемашина", "Калькулятор",
            "Факс", "МФУ", "Системный блок", "Наушники", "Камера",
            "Часы", "Смарт-колонка", "Модем", "Флешка", "Жесткий диск",
            "SSD накопитель", "Плоттер", "Микрофон", "Кресло", "Стол"
        ]

        created_count = 0

        for i in range(1, 101):
            name = random.choice(sample_names)
            inventory_number = f"INV-{1000 + i}"
            serial_number = f"SN-{random.randint(10000, 99999)}"

            date_received = timezone.now().date() - timedelta(days=random.randint(100, 500))
            date_assigned = date_received + timedelta(days=random.randint(1, 30))
            warranty_expiration = date_received + timedelta(days=random.randint(100, 900))

            department = random.choice(departments)
            responsible_user = random.choice(managers)

            Asset.objects.create(
                name=name,
                inventory_number=inventory_number,
                serial_number=serial_number,
                date_received=date_received,
                date_assigned=date_assigned,
                warranty_expiration=warranty_expiration,
                department=department,
                responsible_user=responsible_user,
            )

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Создано {created_count} материальных ценностей!"))
