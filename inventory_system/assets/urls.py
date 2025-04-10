from django.urls import path
from .views import AssetDetailView, AssetListView, AssetCreateView, AssetUpdateView, AssetDeleteView

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('asset/<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('asset/add/', AssetCreateView.as_view(), name='asset_add'),
    path('asset/<int:pk>/edit/', AssetUpdateView.as_view(), name='asset_edit'),
    path('asset/<int:pk>/delete/', AssetDeleteView.as_view(), name='asset_delete'),
]