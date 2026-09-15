from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "result/<int:pk>/",
        views.result,
        name="result"
    ),

    path(
        "api/analyze/",
        views.analyze_hand_api,
        name="api_analyze"
    ),

]