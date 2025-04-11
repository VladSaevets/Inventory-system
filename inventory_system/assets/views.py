from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Asset, Department
from django.db.models import Q

from users.models import CustomUser


class AssetCreateView(CreateView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')

    def form_valid(self, form):
        messages.success(self.request, "Материальная ценность успешно добавлена.")
        return super().form_valid(form)

class AssetUpdateView(UpdateView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')

    def form_valid(self, form):
        messages.success(self.request, "Изменения успешно сохранены.")
        return super().form_valid(form)

class AssetDeleteView(DeleteView):
    model = Asset
    fields = '__all__'
    template_name = 'assets/asset_confirm_delete.html'
    success_url = reverse_lazy('assets:asset_list')

    def form_valid(self, form):
        messages.success(self.request, "Материальная ценность успешно удалена.")
        return super().form_valid(form)

class AssetDetailView(DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'

class AssetListView(ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'

    def get_queryset(self):
        queryset = Asset.objects.all()
        query = self.request.GET.get('q')
        department_id = self.request.GET.get('department')
        responsible_user_id = self.request.GET.get('responsible')
        warranty_filter = self.request.GET.get('warranty_status')

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