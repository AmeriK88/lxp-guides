from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("new/<int:experience_id>/", views.create_booking, name="create"),
    path("my/", views.traveler_bookings, name="traveler_list"),
    path("received/", views.guide_bookings, name="guide_list"),
    path("<int:pk>/accept/", views.accept_booking, name="accept"),
    path("<int:pk>/reject/", views.reject_booking, name="reject"),
]
