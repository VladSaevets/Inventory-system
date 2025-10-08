from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from assets.models import Department

User = get_user_model()

class Command(BaseCommand):
    help = "Создаёт 5 подразделений и 5 менеджеров"

    def handle(self, *args, **options):
        Department.objects.all().delete()
        User.objects.filter(role='DEPARTMENT_HEAD').delete()

        names = [
            "Отдел разработки", "Отдел продаж", "Бухгалтерия",
            "Отдел снабжения", "Отдел обслуживания"
        ]
        managers = [
            ("manager1","Иван","Петров"),
            ("manager2","Анна","Сидорова"),
            ("manager3","Дмитрий","Ковалев"),
            ("manager4","Мария","Смирнова"),
            ("manager5","Алексей","Ильин"),
        ]

        for i, dept_name in enumerate(names):
            dept = Department.objects.create(name=dept_name)
            username, first, last = managers[i]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "role": "DEPARTMENT_HEAD",
                    "email": f"{username}@example.com",
                }
            )
            if created:
                user.set_password("manager123")
                user.save()
            self.stdout.write(self.style.SUCCESS(f"Created {user.username} for {dept.name}"))
        self.stdout.write(self.style.SUCCESS("Done"))
