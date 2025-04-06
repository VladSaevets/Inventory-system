from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    ACCOUNTANT = 'accountant', 'Бухгалтер'
    INVENTORY_MANAGER = 'inventory_manager', 'Учётчик'
    DEPARTMENT_HEAD = 'department_head', 'Руоводитель подразделения'

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.DEPARTMENT_HEAD,
        verbose_name='Роль'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'