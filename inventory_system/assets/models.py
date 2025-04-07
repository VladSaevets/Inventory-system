from django.contrib.auth.admin import UserAdmin
from django.db import models
from users.models import CustomUser


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
