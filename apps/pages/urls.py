from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("dashboard/profile/", views.profile_view, name="profile"),
    path("dashboard/guide/", views.guide_dashboard, name="guide_dashboard"),
    path("dashboard/traveler/", views.traveler_dashboard, name="traveler_dashboard"),
]
