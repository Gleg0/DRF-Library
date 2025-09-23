from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

docs_urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
]

api_urlpatterns = [
    path("users/", include("users.urls", namespace="users")),
    path("", include("books.urls", namespace="books")),
    path("", include("borrowings.urls", namespace="borrowings")),
    path("", include("payments.urls", namespace="payments")),
    path("docs/", include(docs_urlpatterns)),
]
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
