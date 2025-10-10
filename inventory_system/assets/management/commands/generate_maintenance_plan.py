from django.core.management.base import BaseCommand
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook
from assets.models import Asset

class Command(BaseCommand):
    help = "Создает план ТО на год и экспортирует его в Excel"

    def handle(self, *args, **options):
        assets = Asset.objects.all()
        wb = Workbook()
        ws = wb.active
        ws.title = "План ТО"

        ws.append(["Наименование", "Инвентарный номер", "Ответственный", "Подразделение", "Месяц ТО", "Дата последнего ТО"])

        for asset in assets:
            if not asset.last_maintenance:
                continue

            # добавляем 6 месяцев вперед пока не превысим 12 месяцев
            next_maintenance = asset.last_maintenance
            for _ in range(2):  # два ТО в год
                next_maintenance += relativedelta(months=6)
                if next_maintenance.year == datetime.now().year:
                    ws.append([
                        asset.name,
                        asset.inventory_number,
                        asset.responsible_user.get_full_name() if asset.responsible_user else "-",
                        asset.department.name if asset.department else "-",
                        next_maintenance.strftime("%B %Y"),
                        asset.last_maintenance.strftime("%d.%m.%Y"),
                    ])

        wb.save("План_ТО.xlsx")
        self.stdout.write(self.style.SUCCESS("План ТО успешно создан: План_ТО.xlsx"))
