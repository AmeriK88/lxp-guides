from django.urls import path
from . import views

app_name = "experiences"

urlpatterns = [
    path("", views.experience_list, name="list"),
    path("new/", views.experience_create, name="create"),
    path("<int:pk>/", views.experience_detail, name="detail"),
    path("<int:pk>/edit/", views.experience_edit, name="edit"),
    path("<int:pk>/delete/", views.experience_delete, name="delete"),
]
