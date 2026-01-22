from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    # Crear y listar
    path("new/<int:experience_id>/", views.create_booking, name="create"),
    path("my/", views.traveler_bookings, name="traveler_list"),
    path("received/", views.guide_bookings, name="guide_list"),

    # Detalle
    path("<int:pk>/", views.booking_detail, name="detail"),

    # Decisiones iniciales del guía
    path("<int:pk>/accept/", views.accept_booking, name="accept"),
    path("<int:pk>/reject/", views.reject_booking, name="reject"),

    # --- NUEVO: Solicitudes del viajero ---
    path("<int:pk>/request-change/", views.request_booking_change, name="request_change"),
    path("<int:pk>/request-cancel/", views.request_booking_cancel, name="request_cancel"),

    # --- NUEVO: Decisión del guía sobre cambios / cancelaciones ---
    path("<int:pk>/change/<str:decision>/", views.decide_change_request, name="guide_change_decide"),
    path("<int:pk>/cancel/<str:decision>/", views.decide_cancel_request, name="guide_cancel_decide"),
]
