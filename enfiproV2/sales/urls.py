from django.urls import path
from . import views


app_name = "sales"
urlpatterns = [
    # List sales
    path('', views.sales_list_view, name='sales_list'),
    # Add sale
    path('add', views.sales_add_view, name='sales_add'),
    # Details sale
    path('details/<str:sale_id>',
         views.sales_details_view, name='sales_details'),
    # Sale receipt PDF
    path("pdf/<str:sale_id>",
         views.receipt_pdf_view, name="sales_receipt_pdf"),

    path('print/', views.print_file, name='print_file'),
    path('label/', views.print_label, name='print_label'),
    path('get_products/', views.get_products_by_customer, name='get_products'),
]
