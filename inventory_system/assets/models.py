from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.conf import settings
from users.models import CustomUser

from django.db.models.signals import post_save
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta
from datetime import date


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название подразделения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Подразделение"
        verbose_name_plural="Подразделения"

class Asset(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    inventory_number = models.CharField(max_length=50, unique=True,verbose_name="Инвентарный номер")
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Заводской номер")
    date_received = models.DateField(verbose_name="Дата поступления в организацию")
    date_assigned = models.DateField(verbose_name="Дата передачи ответственному")
    warranty_expiration = models.DateField(verbose_name="Гарантия до")
    last_maintenance = models.DateField(blank=True, null=True, verbose_name="Дата последнего ТО")

    responsible_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Материально-ответственное лицо",
        related_name="assets"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Подразделение"
    )

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"

    class Meta:
        verbose_name = "Материальная ценность"
        verbose_name_plural = "Материальные ценности"


class MaintenanceRecord(models.Model):
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name='Материальная ценность'
    )
    date = models.DateField(verbose_name='Дата проведения ТО')
    description = models.TextField(blank=True, verbose_name='Описание работ')
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Исполнитель'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')

    class Meta:
        verbose_name = 'Запись о ТО'
        verbose_name_plural = 'Записи о ТО'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.asset.name} — {self.date}"

@receiver(post_save, sender=MaintenanceRecord)
def update_asset_last_maintenance(sender, instance, created, **kwargs):
    """
    При создании/обновлении записи ТО обновляем поле asset.last_maintenance,
    если дата записи новее текущего last_maintenance (или если last_maintenance пустое).
    """
    asset = instance.asset
    if not asset:
        return

    record_date = instance.date
    # если у asset нет last_maintenance или запись новее — обновляем
    if not asset.last_maintenance or (record_date and record_date > asset.last_maintenance):
        asset.last_maintenance = record_date
        asset.save(update_fields=['last_maintenance'])