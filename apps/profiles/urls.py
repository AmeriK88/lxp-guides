from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("guides/<int:user_id>/", views.public_guide_profile, name="public_guide"),
]
