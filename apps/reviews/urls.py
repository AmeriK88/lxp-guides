from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("new/<int:experience_id>/", views.create_review, name="create"),
    path("my/", views.my_reviews, name="my_reviews"),
]
