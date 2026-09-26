from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
	path("login/", include("dashboard.auth_urls")),
	path("logout/", auth_views.LogoutView.as_view(), name="logout"),
	path("", include("dashboard.urls")),
]
