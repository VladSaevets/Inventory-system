from django.contrib import admin
from .models import Asset, Department
from django.utils.translation import gettext_lazy as _

from django.utils import timezone
from datetime import date
from django.contrib.admin import SimpleListFilter

class WarrantyStatusFilter(SimpleListFilter):
    title = _("Статус гарантии")
    parameter_name = 'warranty_status'

    def lookups(self, request, model_admin):
        return [
            ('active', _('Действует')),
            ('expired', _('Истекла')),
            ('this_month', _("Истекает в этом месяце")),
        ]

    def queryset(self, request, queryset):
        today = date.today()
        if self.value() == 'active':
            return queryset.filter(warranty_expiration_date__gte=today)
        if self.value() == 'expired':
            return queryset.filter(warranty_expiration_date__lt=today)
        if self.value() == 'this_month':
            first_day = today.replace(day=1)
            if today.month == 12:
                last_day = date(today.year + 1, 1, 1)
            else:
                last_day = date(today.year - 1, 1, 1)
            return queryset.filter(warranty_expiration__gte=first_day, warranty_expiration__lte=last_day)



@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "inventory_number", "responsible_user", "department", "warranty_expiration")
    search_fields = ("name", "inventory_number", "serial_number")
    list_filter = ("department", WarrantyStatusFilter)