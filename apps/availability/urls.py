from django.urls import path
from . import views

app_name = "availability"

urlpatterns = [
    path("manage/<int:experience_id>/", views.availability_manage, name="manage"),
    path("manage/<int:experience_id>/block/", views.add_block, name="add_block"),
    path("block/<int:block_id>/delete/", views.delete_block, name="delete_block"),
    path("experience/<int:experience_id>/disabled-dates/", views.experience_disabled_dates, name="experience_disabled_dates"),

]
