from django.shortcuts import redirect
from django.urls import reverse

class AdminAccessRestrictionMiddleware:
    """
    Разрешает доступ в /admin/ только admin, accountant, inventory_manager
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем доступ только к /admin/
        if request.path.startswith(reverse('admin:index')):
            user = request.user
            if not user.is_authenticated or user.role not in ['admin', 'accountant', 'inventory_manager']:
                return redirect('login')  # перенаправляем на страницу входа
        return self.get_response(request)
