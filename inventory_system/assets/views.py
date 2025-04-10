from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from .models import Asset, Department
from django.db.models import Q

from users.models import CustomUser


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

        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if responsible_user_id:
            queryset = queryset.filter(responsible_user_id=responsible_user_id)

        if query:
            return queryset.filter(
                Q(name__icontains=query) |
                Q(inventory_number__icontains=query) |
                Q(serial_number__icontains=query)
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