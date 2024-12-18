
from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UploadImageView,  TestListView, QuestionListView, TestDetailView, SubmitTestView, TestResponsesView
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('upload-image/', UploadImageView.as_view()),
    path('tests/', TestListView.as_view()), 
    path('tests/<int:test_id>/questions/', QuestionListView.as_view()),
    path('tests/<int:id>/', TestDetailView.as_view()),
    path('tests/<int:test_id>/submit/', SubmitTestView.as_view()),
    path('tests/<int:test_id>/responses/', TestResponsesView.as_view()),
    path('questions/', QuestionListView.as_view()), 
    path('questions/<int:question_id>/', QuestionListView.as_view()),
]



