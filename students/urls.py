from django.urls import path
from students.views import StudentIndexView, StudentCreateView, StudentPrivateView, StudentUpdateView, StudentDetailView, StudentDeleteView, StudentQuickUploadView,\
                            StudentQuickCSVUploadView, ActiveStudentListView, NonActiveStudentListView, \
                            DownloadExcelActiveStudent, DownloadExcelInactiveStudent
from students_humas.views import DownloadPrivateListView


urlpatterns = [
    path('', StudentIndexView.as_view(), name='student-list'),
    path('create/', StudentCreateView.as_view(), name='student-create'),
    path('quick-create/', StudentQuickUploadView.as_view(), name='student-quick-create'),
    path('quick-create-csv/', StudentQuickCSVUploadView.as_view(), name='student-quick-create-csv'),
    path('detail/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('update/<int:pk>/', StudentUpdateView.as_view(), name='student-update'),
    path('delete/<int:pk>/', StudentDeleteView.as_view(), name='student-delete'),

    path('active/', ActiveStudentListView.as_view(), name='student-active'),
    path('active/download/', DownloadExcelActiveStudent.as_view(), name='student-active-download'),
    path('nonactive/', NonActiveStudentListView.as_view(), name='student-nonactive'),
    path('nonactive/download/', DownloadExcelInactiveStudent.as_view(), name='student-nonactive-download'),
    path('nonactive/download/', DownloadExcelInactiveStudent.as_view(), name='student-nonactive-download'),
    
    path("private/", StudentPrivateView.as_view(), name="student-private"),
    path("download/", DownloadPrivateListView.as_view(), name="student-private-download"),
]