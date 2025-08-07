from django.urls import path
from . import views


urlpatterns = [
    path("search/", views.search, name="search"),
    path("create/", views.create_advert, name="create_advert"),
    path("<uuid:advert_id>/", views.get_advert, name="get_advert"),
    path("<uuid:advert_id>/apply/", views.apply, name="apply"),
    path("<uuid:advert_id>/update/", views.update_advert, name="update_advert"),
    path("<uuid:advert_id>/delete/", views.delete_advert, name="delete_advert"),
    path("<uuid:advert_id>/applications/", views.advert_applications, name="advert_applications"),
    path("<uuid:application_id>/decide/", views.decide, name="decide"),
    path("my_applications/", views.my_application, name="my_applications"),
    path("my_jobs/", views.my_jobs, name="my_jobs"),
]