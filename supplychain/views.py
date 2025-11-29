from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Supplier, Resource
from .serializers import SupplierSerializer, ResourceSerializer
from core.utils import ResponseHandler


# ------------------------------
# SUPPLIER APIs
# ------------------------------

class SupplierListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suppliers = Supplier.objects.all().order_by("-created_at")
        serializer = SupplierSerializer(suppliers, many=True)
        return ResponseHandler.success(data=serializer.data, message="Suppliers fetched successfully.")

    @transaction.atomic
    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.created(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Supplier creation failed.")


class SupplierDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return None

    def get(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return ResponseHandler.not_found(message="Supplier not found.")
        return ResponseHandler.success(data=SupplierSerializer(supplier).data)

    @transaction.atomic
    def patch(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return ResponseHandler.not_found(message="Supplier not found.")

        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.updated(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Supplier update failed.")

    @transaction.atomic
    def delete(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return ResponseHandler.not_found(message="Supplier not found.")

        supplier.delete()
        return ResponseHandler.deleted(message="Supplier deleted successfully.")


# ------------------------------
# RESOURCE APIs
# ------------------------------

class ResourceListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return ResponseHandler.success(data=serializer.data, message="Resources fetched successfully.")

    @transaction.atomic
    def post(self, request):
        serializer = ResourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.created(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Resource creation failed.")


class ResourceDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Resource.objects.get(pk=pk)
        except Resource.DoesNotExist:
            return None

    def get(self, request, pk):
        resource = self.get_object(pk)
        if not resource:
            return ResponseHandler.not_found(message="Resource not found.")
        return ResponseHandler.success(data=ResourceSerializer(resource).data)

    @transaction.atomic
    def patch(self, request, pk):
        resource = self.get_object(pk)
        if not resource:
            return ResponseHandler.not_found(message="Resource not found.")

        serializer = ResourceSerializer(resource, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.updated(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Resource update failed.")

    @transaction.atomic
    def delete(self, request, pk):
        resource = self.get_object(pk)
        if not resource:
            return ResponseHandler.not_found(message="Resource not found.")

        resource.delete()
        return ResponseHandler.deleted(message="Resource deleted successfully.")
    
    


# task management
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer

class TaskListAPIView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaskDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            task = Task.objects.get(id=str(pk))  # Convert pk to string
        except Task.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

import json
class TaskByStatusView(APIView):

    def get(self, request):
        status_filter = request.query_params.get("status")  # e.g., ?status=Pending
        if status_filter not in ["Pending", "Accepted", "Done", None]:
            return Response({"error": "Invalid status"}, status=400)

        tasks = Task.objects.all()
        if status_filter:
            tasks = tasks.filter(status=status_filter)

        # Serialize tasks
        serializer = TaskSerializer(tasks, many=True)

        # Sum total from price JSON
        total_sum = sum(
            json.loads(task.price).get("Total", 0) for task in tasks
        )

        return Response({
            "status": status_filter or "All",
            "total_offers": tasks.count(),
            "total_price": total_sum,
            "tasks": serializer.data
        })
        
        
# notification
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(APIView):
    def get(self, request):
        notifications = Notification.objects.all().order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
