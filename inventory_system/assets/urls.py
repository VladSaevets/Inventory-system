from django.urls import path

from . import views
from .views import (AssetDetailView, AssetListView, AssetCreateView, AssetUpdateView, AssetDeleteView,
                    ExportAssetsToExcelView, export_assets_csv, export_maintenance_plan_excel)

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('asset/<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('asset/add/', AssetCreateView.as_view(), name='asset_add'),
    path('asset/<int:pk>/edit/', AssetUpdateView.as_view(), name='asset_edit'),
    path('asset/<int:pk>/delete/', AssetDeleteView.as_view(), name='asset_delete'),
    path('export/excel', ExportAssetsToExcelView.as_view(), name='export_excel'),
    path('export/csv/', export_assets_csv, name='export_csv'),
    path('maintenance-plan/', views.maintenance_plan_view, name='maintenance_plan'),
    path('maintenance-plan/export/', views.export_maintenance_plan_excel, name='export_maintenance_plan_excel'),

]