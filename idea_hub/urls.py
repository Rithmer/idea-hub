"""Маршруты приложений, административной и отладочной панелей."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path


admin.site.site_header = "Администрирование IdeaHub"
admin.site.site_title = "Админ-панель IdeaHub"
admin.site.index_title = "Управление каталогом"

handler404 = "homepage.views.page_not_found"


urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("ideas/", include("catalog.urls")),
    path("categories/", include("taxonomy.urls")),
    path("participants/", include("participants.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
