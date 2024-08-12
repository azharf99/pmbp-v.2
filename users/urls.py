from django.urls import path
from users.views import TeacherCreateView, TeacherUpdateView, TeacherDeleteView, TeacherListView, TeacherDetailView, MyLoginView,\
                        MyLogoutView, MyProfileView, MyProfileUpdateView, UserCreateView, UserListView, UserUpdateView, UserDeleteView,\
                        UserDetailView, UserPasswordChangeView, UserPasswordChangeDoneView

urlpatterns = [
    path('', UserListView.as_view(), name="user-list"),
    path('<int:pk>/password/', UserPasswordChangeView.as_view(), name="user-change-password"),
    path('password/done', UserPasswordChangeDoneView.as_view(), name="user-change-password-done"),
    
    path('create/', UserCreateView.as_view(), name="user-create"),
    path('detail/<int:pk>/', UserDetailView.as_view(), name="user-detail"),
    path('update/<int:pk>/', UserUpdateView.as_view(), name="user-update"),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name="user-delete"),

    path('login/', MyLoginView.as_view(), name="login"),
    path('logout/', MyLogoutView.as_view(), name="logout"),

    path('profile/', MyProfileView.as_view(), name="profile"),
    path('profile/<int:pk>/', MyProfileUpdateView.as_view(), name="profile-update"),

    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
    path('teacher/create/', TeacherCreateView.as_view(), name='teacher-create'),
    path('teacher/<int:pk>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('teacher/update/<int:pk>/', TeacherUpdateView.as_view(), name='teacher-update'),
    path('teacher/delete/<int:pk>/', TeacherDeleteView.as_view(), name='teacher-delete'),
]