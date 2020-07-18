from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.urls import get_callable

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('', TemplateView.as_view(template_name='login.html')),
    path('portfolio/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
]
