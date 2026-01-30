from django.urls import path
from . import views

app_name = "helpdesk"

urlpatterns = [
    path("", views.helpdesk_view, name="helpdesk"),
    path("a/<slug:slug>/", views.article_detail, name="article_detail"),
]
