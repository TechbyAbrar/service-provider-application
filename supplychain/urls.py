from django.urls import path
from .views import (SupplierListCreateAPI, SupplierDetailAPI,ResourceListCreateAPI, ResourceDetailAPI, TaskDetailAPIView, TaskListAPIView, TaskByStatusView, NotificationListView)

urlpatterns = [
    path('suppliers/', SupplierListCreateAPI.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailAPI.as_view(), name='supplier-detail'),
    path('suppliers/<int:pk>/update/', SupplierDetailAPI.as_view(), name='supplier-detail'),
    path('suppliers/<int:pk>/delete/', SupplierDetailAPI.as_view(), name='supplier-detail'),
    path('resources/', ResourceListCreateAPI.as_view(), name='resource-list-create'),
    path('resources/<int:pk>/', ResourceDetailAPI.as_view(), name='resource-detail'),
    path('resources/<int:pk>/update/', ResourceDetailAPI.as_view(), name='resource-detail'),
    path('resources/<int:pk>/delete/', ResourceDetailAPI.as_view(), name='resource-detail'),
    
    # task management
    path('tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('tasks/<str:pk>/', TaskDetailAPIView.as_view(), name='task-detail'),
    
    # check status
    path('task/status/', TaskByStatusView.as_view(), name='task-by-status'),
    # notifications
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]
