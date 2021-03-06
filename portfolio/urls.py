from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import DownloadPDF
from django.views.generic import TemplateView
from django.urls import reverse

app_name = 'portfolio'
urlpatterns = [
    path('', views.home, name='home'),
    url(r'^home/$', views.home, name='home'),
    path('customer_list', views.customer_list, name='customer_list'),
    path('customer/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('stock_list', views.stock_list, name='stock_list'),
    path('stock/create/', views.stock_new, name='stock_new'),
    path('stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('investment_list', views.investment_list, name='investment_list'),
    path('investment/create/', views.investment_new, name='investment_new'),
    path('investment/<int:pk>/edit/', views.investment_edit, name='investment_edit'),
    path('investment/<int:pk>/delete/', views.investment_delete, name='investment_delete'),
    path('customer/<int:pk>/portfolio/', views.portfolio, name='portfolio'),
    path('customer/<int:pk>/portfolio/portfolioINR/', views.portfolioINR, name='portfolioINR'),
    path('customer/<int:pk>/portfolio/pdf_download/', views.DownloadPDF.as_view(), name='pdf_download'),
    path('customer/<int:pk>/portfolio/pdf_view/', views.ViewPDF.as_view(), name='pdf_view'),
    path('customer/<int:pk>/portfolio/pdf_email/', views.EmailPDF.as_view(), name='pdf_email'),
    path('customer/<int:pk>/portfolio/graph/', views.Graphimage.as_view(), name='graph'),
    url(r'^customers_json/', views.CustomerList.as_view()),
    url(r'^investments_json/', views.InvestmentList.as_view()),
    url(r'^stocks_json/', views.StockList.as_view()),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html')),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html')),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

urlpatterns = format_suffix_patterns(urlpatterns)