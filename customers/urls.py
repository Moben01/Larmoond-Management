from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('<int:pk>/toggle-status/', views.toggle_status, name='toggle_status'),
    path('<int:pk>/add-note/', views.add_note, name='add_note'),
    path('export/', views.export_customers, name='export_customers'),
]