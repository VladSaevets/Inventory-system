from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Asset
from django.db.models import Q

class AssetCreateView(CreateView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')

class AssetUpdateView(UpdateView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')

class AssetDeleteView(DeleteView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_confirm_delete.html'
    success_url = reverse_lazy('assets:asset_list')

class AssetDetailView(DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'

class AssetListView(ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Asset.objects.filter(
                Q(name__icontains=query) |
                Q(inventory_number__icontains=query) |
                Q(serial_number__icontains=query) |
                Q(responsible_user__first_name__icontains=query) |
                Q(responsible_user__last_name__icontains=query) |
                Q(department__name__icontains=query)
            )
        return Asset.objects.all()