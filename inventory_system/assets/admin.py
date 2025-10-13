from django.contrib import admin
from .models import Asset, Department, MaintenanceRecord
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

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('asset', 'date', 'performed_by', 'short_description', 'created_at')
    list_filter = ('date', 'performed_by', 'asset__department')
    search_fields = ('asset__name', 'asset__inventory_number', 'performed_by__username', 'description')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
    actions = ['mark_asset_last_maintenance']

    def short_description(self, obj):
        return (obj.description[:75] + '...') if obj.description and len(obj.description) > 75 else obj.description
    short_description.short_description = 'Описание'

    def mark_asset_last_maintenance(self, request, queryset):
        """
        Админ-экшн: поставить у связанных assets last_maintenance = запись.date (если новее).
        Полезно при массовом импорте/правке.
        """
        updated = 0
        for rec in queryset:
            asset = rec.asset
            if not asset.last_maintenance or rec.date > asset.last_maintenance:
                asset.last_maintenance = rec.date
                asset.save(update_fields=['last_maintenance'])
                updated += 1
        self.message_user(request, f'Обновлено last_maintenance для {updated} ценностей.')
    mark_asset_last_maintenance.short_description = 'Обновить дату последнего ТО для связанных ценностей'