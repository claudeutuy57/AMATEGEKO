from django.urls import path
from . import views

app_name = 'curriculum'

urlpatterns = [
    path('road-signs/', views.road_signs_view, name='road_signs'),
    path('road-signs/<str:code>/', views.road_sign_detail_view, name='road_sign_detail'),
    path('traffic-rules/', views.traffic_rules_view, name='traffic_rules'),
    path('lessons/<slug:slug>/', views.lesson_detail_view, name='lesson_detail'),
]

