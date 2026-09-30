from django.urls import path
from . import views

urlpatterns = [
    path("contact/", views.contact_lead, name="contact_lead"),
    path("jobs/", views.job_listings, name="job_listings"),
    path("chat/", views.chat_api, name="chat_api"),
]

