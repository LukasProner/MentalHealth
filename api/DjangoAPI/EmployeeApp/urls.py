
from django.urls import path, re_path
from EmployeeApp import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('department/', views.departmentApi),
    path('department/<int:id>/', views.departmentApi),
    path('employee/', views.employeeApi),
    path('employee/<int:id>/', views.employeeApi),
    re_path(r'^employee/savefile$', views.SaveFile),  # použitie re_path na regex
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

