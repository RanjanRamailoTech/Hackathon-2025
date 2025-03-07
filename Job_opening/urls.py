from django.urls import path
from .views import (
    JobOpeningListCreateView,
    JobOpeningDetailView,
    ApplicantResponseCreateView,
    JobOpeningResponsesListView,
    JobOpeningResponseDetailView,
    ArchivedJobOpeningsListView
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("job-openings/", JobOpeningListCreateView.as_view(), name="job-opening-list-create"),
    path("job-openings/<int:pk>/", JobOpeningDetailView.as_view(), name="job-opening-detail"),
    path("apply/<int:job_id>/", ApplicantResponseCreateView.as_view(), name="applicant-response-create"),
    path("dashboard/job-openings/<int:job_id>/responses/", JobOpeningResponsesListView.as_view(), name="job-opening-responses-list"),
    path("dashboard/job-openings/<int:job_id>/responses/<int:response_id>/", JobOpeningResponseDetailView.as_view(), name="job-opening-response-detail"),
    path("dashboard/archived-job-openings/", ArchivedJobOpeningsListView.as_view(), name="archived-job-openings-list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)