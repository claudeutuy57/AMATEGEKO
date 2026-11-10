from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/questions/', views.admin_questions, name='admin_questions'),
    path('admin/questions/add/', views.admin_question_create, name='admin_question_create'),
    path('admin/questions/<int:pk>/edit/', views.admin_question_edit, name='admin_question_edit'),
    path('admin/questions/<int:pk>/delete/', views.admin_question_delete, name='admin_question_delete'),
    path('admin/road-signs/', views.admin_road_signs, name='admin_road_signs'),
    path('admin/road-signs/add/', views.admin_road_sign_create, name='admin_road_sign_create'),
    path('admin/road-signs/<int:pk>/edit/', views.admin_road_sign_edit, name='admin_road_sign_edit'),
    path('admin/road-signs/<int:pk>/delete/', views.admin_road_sign_delete, name='admin_road_sign_delete'),
]

