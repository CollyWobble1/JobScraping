from django.contrib import admin
from django.urls import path

from dashboard.views import home, skill_detail


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("skill-details/", skill_detail, name="skill_detail"),
]
