from django.urls import path

from frontend.views.home_page import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home_page"),
]
