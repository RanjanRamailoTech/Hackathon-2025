from django.urls import path, include

from .views import (
    StartInterview,
    InterviewProcessingAPI,
)



urlpatterns = [
    ### Candidate login via linkedin
    # path('start-interview/', StartInterview.as_view(), name='start-interview'),
    path('process/', InterviewProcessingAPI.as_view(), name='interview_process'),
]