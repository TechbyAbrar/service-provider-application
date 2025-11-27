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