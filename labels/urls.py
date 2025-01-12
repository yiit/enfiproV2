from django.urls import path
from . import views

app_name = "labels"
urlpatterns = [
    # List sales
    path('', views.labels_list_view, name='label_list'),
]
