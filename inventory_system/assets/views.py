from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Asset, Department
from django.db.models import Q

from users.models import CustomUser

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

import csv

from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from openpyxl import Workbook


class AssetCreateView(CreateView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')

    def form_valid(self, form):
        messages.success(self.request, "Материальная ценность успешно добавлена.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'department_head':
            raise PermissionDenied("У вас нет доступа к добавлению.")
        return super().dispatch(request, *args, **kwargs)

class AssetUpdateView(UpdateView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')

    def form_valid(self, form):
        messages.success(self.request, "Изменения успешно сохранены.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'department_head':
            raise PermissionDenied("У вас нет доступа к редактированию этой материальной ценности.")
        return super().dispatch(request, *args, **kwargs)

class AssetDeleteView(DeleteView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_confirm_delete.html'
    success_url = reverse_lazy('assets:asset_list')

    def form_valid(self, form):
        messages.success(self.request, "Материальная ценность успешно удалена.")
        return super().form_valid(form)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        # 👨‍💼 Руководитель может смотреть только свои ценности
        if user.role == 'department_head':
            raise PermissionDenied("У вас нет доступа к удалению данной материальной ценности.")
        return obj

class AssetDetailView(DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        # --- Проверка прав доступа ---
        if user.is_authenticated:
            if user.role == "department_head" and obj.responsible_user != user:
                raise PermissionDenied("У вас нет доступа к этой материальной ценности.")
        return obj

class AssetListView(ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20

    def get_paginate_by(self, queryset):
        """Определяет, сколько элементов показывать на странице."""
        paginate_by = self.request.GET.get('paginate_by', 20)  # значение по умолчанию — 20
        try:
            paginate_by = int(paginate_by)
        except ValueError:
            paginate_by = 20
        return paginate_by

    def get_queryset(self):
        user = self.request.user

        queryset = Asset.objects.all()
        query = self.request.GET.get('q')
        department_id = self.request.GET.get('department')
        responsible_user_id = self.request.GET.get('responsible')
        warranty_filter = self.request.GET.get('warranty_status')

        if user.is_authenticated and user.role == "department_head":
            queryset = queryset.filter(responsible_user = user)

        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if responsible_user_id:
            queryset = queryset.filter(responsible_user_id=responsible_user_id)
        if warranty_filter:
            today = timezone.now().date()
            if warranty_filter == 'valid':
                queryset = queryset.filter(warranty_expiration__gte=today)
            if warranty_filter == 'expired':
                queryset = queryset.filter(warranty_expiration__lt=today)
            if warranty_filter == 'expiring_this_month':
                queryset = queryset.filter(
                    warranty_expiration__year=today.year,
                    warranty_expiration__month=today.month
                )

        if query:
            return queryset.filter(
                Q(name__icontains=query) |
                Q(inventory_number__icontains=query) |
                Q(serial_number__icontains=query) |
                Q(responsible_user__first_name__icontains=query) |
                Q(responsible_user__last_name__icontains=query) |
                Q(department__name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AssetListView, self).get_context_data(**kwargs)
        context["departments"] = Department.objects.all()
        context["responsibles"] = CustomUser.objects.all()
        context["search_query"] = self.request.GET.get('q', "")
        context["selected_department"] = self.request.GET.get('department', "")
        context["selected_responsible"] = self.request.GET.get('responsible', "")
        return context

class ExportAssetsToExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Получаем данные с учётом фильтров
        list_view = AssetListView()
        list_view.request = request
        queryset = list_view.get_queryset()

        # Создаём Excel-файл
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Материальные ценности"

        # === МЕТАДАННЫЕ ===
        username = request.user.get_full_name() or request.user.username
        export_time = timezone.localtime(timezone.now()).strftime("%d.%m.%Y %H:%M:%S")

        ws["A1"] = f"📦 Выгрузка материальных ценностей"
        ws["A2"] = f"👤 Пользователь: {username}"
        ws["A3"] = f"📅 Дата выгрузки: {export_time}"

        ws["A1"].font = Font(bold=True, size=14)
        ws["A2"].font = Font(italic=True, color="555555")
        ws["A3"].font = Font(italic=True, color="555555")

        ws["A1"].alignment = Alignment(horizontal="left")
        ws["A2"].alignment = Alignment(horizontal="left")
        ws["A3"].alignment = Alignment(horizontal="left")

        # === Заголовки таблицы (начинаются с 5-й строки) ===
        headers = [
            "Наименование",
            "Инвентарный номер",
            "Заводской номер",
            "Ответственный",
            "Подразделение",
            "Гарантия до",
        ]
        ws.append([])  # пустая строка между метаданными и таблицей
        ws.append(headers)

        # Стили заголовков
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")

        for cell in ws[5]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        # === Данные ===
        for asset in queryset:
            ws.append([
                asset.name,
                asset.inventory_number,
                asset.serial_number or "-",
                asset.responsible_user.get_full_name() if asset.responsible_user else "-",
                asset.department.name if asset.department else "-",
                asset.warranty_expiration.strftime("%d.%m.%Y") if asset.warranty_expiration else "-",
            ])

        # Автоширина колонок
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length + 3

        # Выравнивание данных
        for row in ws.iter_rows(min_row=6):
            for cell in row:
                cell.alignment = Alignment(vertical="center")

        # Добавляем рамку
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )
        for row in ws.iter_rows(min_row=5, max_row=ws.max_row, max_col=ws.max_column):
            for cell in row:
                cell.border = thin_border

        # === Ответ пользователю ===
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"assets_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

# Экспорт в CSV
def export_assets_csv(request):
    # Получаем те же фильтры, что и в списке
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    responsible_id = request.GET.get('responsible', '')
    warranty_status = request.GET.get('warranty_status', '')

    # Базовый queryset
    assets = Asset.objects.all()

    if query:
        assets = assets.filter(
            Q(name__icontains=query) |
            Q(inventory_number__icontains=query) |
            Q(serial_number__icontains=query) |
            Q(responsible_user__first_name__icontains=query) |
            Q(responsible_user__last_name__icontains=query) |
            Q(department__name__icontains=query)
        )
    if department_id:
        assets = assets.filter(department_id=department_id)
    if responsible_id:
        assets = assets.filter(responsible_user_id=responsible_id)

    # Фильтрация по гарантии
    today = timezone.now().date()
    if warranty_status == "valid":
        assets = assets.filter(warranty_expiration__gte=today)
    elif warranty_status == "expired":
        assets = assets.filter(warranty_expiration__lt=today)
    elif warranty_status == "expiring_this_month":
        assets = assets.filter(
            warranty_expiration__year=today.year,
            warranty_expiration__month=today.month
        )

    # --- Генерация CSV-файла ---
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="assets.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Наименование", "Инвентарный номер", "Серийный номер",
        "Ответственный", "Подразделение", "Гарантия до"
    ])

    for asset in assets:
        writer.writerow([
            asset.name,
            asset.inventory_number,
            asset.serial_number or "-",
            asset.responsible_user.get_full_name() if asset.responsible_user else "-",
            asset.department.name if asset.department else "-",
            asset.warranty_expiration.strftime("%d.%m.%Y") if asset.warranty_expiration else "-"
        ])

    return response

@login_required
def maintenance_plan_view(request):
    user = request.user
    month = int(request.GET.get('month', date.today().month))
    year = date.today().year

    # Фильтрация по ролям
    if user.role == "department_head":
        assets = Asset.objects.filter(responsible_user=user)
    else:
        assets = Asset.objects.all()

    # Определяем ценности, у которых ТО в выбранном месяце
    maintenance_items = []
    for asset in assets:
        if not asset.date_received:
            continue

        maintenance_date = asset.date_received
        while maintenance_date.year <= year:
            if maintenance_date.year == year and maintenance_date.month == month:
                maintenance_items.append({
                    'asset': asset,
                    'maintenance_date': maintenance_date
                })
            maintenance_date += relativedelta(months=6)

    months = [
        (1, "Январь"), (2, "Февраль"), (3, "Март"), (4, "Апрель"),
        (5, "Май"), (6, "Июнь"), (7, "Июль"), (8, "Август"),
        (9, "Сентябрь"), (10, "Октябрь"), (11, "Ноябрь"), (12, "Декабрь")
    ]

    return render(request, "assets/maintenance_plan.html", {
        'maintenance_items': maintenance_items,
        'months': months,
        'selected_month': month,
    })


@login_required
def export_maintenance_plan_excel(request):
    user = request.user
    month = int(request.GET.get('month', date.today().month))
    year = date.today().year

    # Фильтрация по ролям
    if user.role == "department_head":
        assets = Asset.objects.filter(responsible_user=user)
    else:
        assets = Asset.objects.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "План ТО"

    # Оформление
    bold_font = Font(bold=True)
    center_alignment = Alignment(horizontal="center", vertical="center")
    header_fill = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")
    border = Border(left=Side(style="thin"), right=Side(style="thin"),
                    top=Side(style="thin"), bottom=Side(style="thin"))

    # Заголовки
    headers = [
        "Наименование",
        "Инвентарный номер",
        "Ответственный",
        "Подразделение",
        "Дата поступления",
        "Плановая дата ТО"
    ]
    ws.append(headers)

    for col in ws.iter_cols(min_row=1, max_row=1, min_col=1, max_col=len(headers)):
        for cell in col:
            cell.font = bold_font
            cell.alignment = center_alignment
            cell.fill = header_fill
            cell.border = border

    # Заполнение данных
    for asset in assets:
        if not asset.date_received:
            continue

        maintenance_date = asset.date_received
        while maintenance_date.year <= year:
            if maintenance_date.year == year and maintenance_date.month == month:
                ws.append([
                    asset.name,
                    asset.inventory_number,
                    asset.responsible_user.get_full_name() if asset.responsible_user else "-",
                    asset.department.name if asset.department else "-",
                    asset.date_received.strftime("%d.%m.%Y"),
                    maintenance_date.strftime("%d.%m.%Y"),
                ])
            maintenance_date += relativedelta(months=6)

    # Оформление ячеек
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(headers)):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center")

    # Автоширина столбцов
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="План_ТО_{month}_{year}.xlsx"'
    wb.save(response)
    return response