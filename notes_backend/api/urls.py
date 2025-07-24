from django.urls import path
from .views import (
    health,
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    NoteListCreateView,
    NoteDetailView
)

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register/', RegisterView.as_view(), name="Register"),
    path('auth/login/', LoginView.as_view(), name="Login"),
    path('auth/logout/', LogoutView.as_view(), name="Logout"),
    path('auth/user/', UserProfileView.as_view(), name="UserProfile"),
    path('notes/', NoteListCreateView.as_view(), name="NoteListCreate"),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name="NoteDetail"),
]
