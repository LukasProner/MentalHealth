
from django.urls import path
from .views import DocumentationView, EvaluateTestView, SaveVideoView,RegisterView, LoginView, ScaleView, TestListAdmin, UserView, LogoutView, UploadImageView,  TestListView, UloadDrawingView,QuestionListView, TestDetailView, SubmitTestView, TestResponsesView, PublicTestView
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
    # path('submissions/<str:test_code>/', TestSubmissionDetailView.as_view()),
    path('tests/<int:test_id>/public/', PublicTestView.as_view()),
    path('tests/<int:test_id>/scales/', ScaleView.as_view()),
    path('tests/<int:test_id>/evaluate/', EvaluateTestView.as_view()),
    path('tests/default/', TestListAdmin.as_view()),
    path('save_drawing/',UloadDrawingView.as_view()),
    path('save_drawing/<int:questionId>/',UloadDrawingView.as_view()),
    path('save_video/', SaveVideoView.as_view()),
    path('save_video/<int:video_id>/', SaveVideoView.as_view()),
    path('documentation/<int:test_id>/', DocumentationView.as_view())
]



