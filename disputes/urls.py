from django.urls import path
from . import views

from core import views as core_views

urlpatterns = [
    path('', core_views.home, name='landing'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('ops/', views.ops_dashboard, name='ops_dashboard'),
    path('analyze/', views.analyze_dispute, name='analyze_dispute'),
    path('result/<int:case_id>/', views.dispute_result, name='dispute_result'),
    path('insights/', views.insights_dashboard, name='insights_dashboard'),
]
