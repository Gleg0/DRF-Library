from django.contrib import admin
from django.urls import include, path

api_urlpatterns = [
    path("users/", include("users.urls", namespace="users")),
]
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]
