from django.urls import path
from . import views

app_name = 'examinations'

urlpatterns = [
    path('practice/', views.practice_list_view, name='practice_list'),
    path('practice/start/', views.practice_view, name='practice'),
    path('kora-ikizamini/', views.custom_exam_builder_view, name='custom_exam_builder'),
    path('kora-ikizamini/tangira/', views.custom_exam_take_view, name='custom_exam_take'),
    path('mock-exam/', views.mock_exam_start, name='mock_exam_start'),
    path('mock-exam/take/', views.mock_exam_view, name='mock_exam'),
    path('mock-exam/submit/', views.mock_exam_submit, name='mock_exam_submit'),
    path('result/<int:attempt_id>/', views.exam_result_view, name='exam_result'),
    path('result/<int:attempt_id>/certificate/', views.exam_certificate_view, name='exam_certificate'),
    path('review/<int:attempt_id>/', views.exam_review_view, name='exam_review'),
    path('bookmark/toggle/<int:question_id>/', views.toggle_bookmark_api, name='toggle_bookmark'),
]

