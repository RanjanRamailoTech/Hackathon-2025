from django.urls import path
from .views import (
    JobOpeningListCreateView,
    JobOpeningDetailView,
    ApplicantResponseCreateView,
    ApplicantResponseListView,
    ApplicantResponseDetailView,
    # ArchivedJobOpeningsListView
    JobOpeningQuestionsView,
    CompanyDashboardStatsView,
    CompanyApplicantResponsesListView,
    JobOpeningPublicDetailView
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("job-openings/", JobOpeningListCreateView.as_view(), name="job-opening-list-create"),
    path("job-openings/<int:pk>/", JobOpeningDetailView.as_view(), name="job-opening-detail"),
    path("job-openings-public/<int:pk>/", JobOpeningPublicDetailView.as_view(), name="job-opening-public-detail"),
    path("apply/<int:jobId>/", ApplicantResponseCreateView.as_view(), name="applicant-response-create"),
    path("dashboard/job-openings/<int:jobId>/responses/", ApplicantResponseListView.as_view(), name="job-opening-responses-list"),
    path("dashboard/job-openings/<int:jobId>/responses/<int:responseId>/", ApplicantResponseDetailView.as_view(), name="job-opening-response-detail"),
    path("dashboard/", CompanyDashboardStatsView.as_view(), name="company-dashboard"),
    path("dashboard/total-applicant/", CompanyApplicantResponsesListView.as_view(), name="company-total-applicant"),
    # path("dashboard/archived-job-openings/", ArchivedJobOpeningsListView.as_view(), name="archived-job-openings-list"),
    path("questions/<int:jobId>/", JobOpeningQuestionsView.as_view(), name="job-opening-questions"),  # New endpoint
]