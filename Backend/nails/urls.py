from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.api_health,
        name="api_root"
    ),
    path(
        "api/health/",
        views.api_health,
        name="api_health"
    ),
    path(
        "api/analyze/",
        views.analyze_hand_api,
        name="api_analyze"
    ),
]