from django.contrib import admin
from django.urls import include, path

api_urlpatterns = [
    path("users/", include("users.urls", namespace="users")),
    path("", include("books.urls", namespace="books")),
    path("", include("borrowings.urls", namespace="borrowings")),
    path("", include("payments.urls", namespace="payments")),
]
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]
