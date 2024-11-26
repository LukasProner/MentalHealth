
from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UploadImageView,  TestListView, QuestionListView, TestDetailView, SubmitTestView, TestResponsesView
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('upload-image/', UploadImageView.as_view(), name='upload-image'),
    path('tests/', TestListView.as_view()), # pre vytvorenie testu
    path('tests/<int:test_id>/questions/', QuestionListView.as_view()),
    path('tests/<int:id>/', TestDetailView.as_view(), name='test-detail'),
    path('tests/<int:test_id>/submit/', SubmitTestView.as_view(), name='submit-test'),
    path('tests/<int:test_id>/responses/', TestResponsesView.as_view(), name='test-responses'),
]



