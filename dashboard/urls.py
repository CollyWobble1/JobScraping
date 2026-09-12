from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("jobs/", views.jobs, name="jobs"),
    path("skill/", views.skill_detail, name="skill_detail"),
]