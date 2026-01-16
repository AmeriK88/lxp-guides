from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("experiences/", include("apps.experiences.urls")),
    path("", include("apps.profiles.urls")),

]

