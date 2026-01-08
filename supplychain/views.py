from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Supplier, Resource
from .serializers import SupplierSerializer, ResourceSerializer
from core.utils import ResponseHandler


# ------------------------------
# SUPPLIER APIs
# ------------------------------

# ------------------------------
# SUPPLIER APIs
# ------------------------------
class SupplierListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only fetch suppliers belonging to the logged-in supervisor
        suppliers = Supplier.objects.filter(supervisor=request.user).order_by("-created_at")
        serializer = SupplierSerializer(suppliers, many=True)
        return ResponseHandler.success(data=serializer.data, message="Suppliers fetched successfully.")

    @transaction.atomic
    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            # Save supervisor as request.user
            serializer.save(supervisor=request.user)
            return ResponseHandler.created(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Supplier creation failed.")


class SupplierDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        # Ensure only the supervisor who owns this supplier can access
        return get_object_or_404(Supplier, pk=pk, supervisor=user)

    def get(self, request, pk):
        supplier = self.get_object(pk, request.user)
        return ResponseHandler.success(data=SupplierSerializer(supplier).data)

    @transaction.atomic
    def patch(self, request, pk):
        supplier = self.get_object(pk, request.user)
        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.updated(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Supplier update failed.")

    @transaction.atomic
    def delete(self, request, pk):
        supplier = self.get_object(pk, request.user)
        supplier.delete()
        return ResponseHandler.deleted(message="Supplier deleted successfully.")


# ------------------------------
# RESOURCE APIs
# ------------------------------
class ResourceListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resources = Resource.objects.filter(supervisor=request.user)
        serializer = ResourceSerializer(resources, many=True)
        return ResponseHandler.success(data=serializer.data, message="Resources fetched successfully.")

    @transaction.atomic
    def post(self, request):
        serializer = ResourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(supervisor=request.user)
            return ResponseHandler.created(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Resource creation failed.")

from django.shortcuts import get_object_or_404
class ResourceDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Resource, pk=pk, supervisor=user)

    def get(self, request, pk):
        resource = self.get_object(pk, request.user)
        return ResponseHandler.success(data=ResourceSerializer(resource).data)

    @transaction.atomic
    def patch(self, request, pk):
        resource = self.get_object(pk, request.user)
        serializer = ResourceSerializer(resource, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.updated(data=serializer.data)
        return ResponseHandler.bad_request(errors=serializer.errors, message="Resource update failed.")

    @transaction.atomic
    def delete(self, request, pk):
        resource = self.get_object(pk, request.user)
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
# from django.utils.dateparse import parse_date
# from rest_framework.views import APIView
# from rest_framework.response import Response
# import json
# from .models import Task
# from .serializers import TaskSerializer

# class TaskByStatusView(APIView):

#     ALLOWED_STATUSES = {"Pending", "Accepted", "Done"}

#     def get(self, request):
#         status_filter = request.query_params.get("status")
#         year = request.query_params.get("year")
#         month = request.query_params.get("month")
#         date_str = request.query_params.get("date")

#         tasks = Task.objects.all()

#         # Filter by status
#         if status_filter:
#             if status_filter not in self.ALLOWED_STATUSES:
#                 return Response({"error": "Invalid status"}, status=400)
#             tasks = tasks.filter(status=status_filter)

#         # Filter by exact date
#         if date_str:
#             parsed_date = parse_date(date_str)
#             if not parsed_date:
#                 return Response({"error": "Invalid date format"}, status=400)
#             tasks = tasks.filter(created_at__date=parsed_date)

#         else:
#             # Filter by year
#             if year:
#                 tasks = tasks.filter(created_at__year=int(year))
#             # Filter by month
#             if month:
#                 tasks = tasks.filter(created_at__month=int(month))

#         serializer = TaskSerializer(tasks, many=True)

#         # Calculate total price
#         total_sum = 0
#         for task in tasks:
#             try:
#                 total_sum += json.loads(task.price).get("Total", 0)
#             except Exception:
#                 pass

#         return Response({
#             "status": status_filter or "All",
#             "total_offers": tasks.count(),
#             "total_price": total_sum,
#             "tasks": serializer.data
#         })


from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

class TaskByStatusView(APIView):

    ALLOWED_STATUSES = {"Pending", "Accepted", "Done"}
    ALLOWED_PERIODS = {"today", "week", "month"}

    def get(self, request):
        status_filter = request.query_params.get("status")
        period = request.query_params.get("period")  # today | week | month
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        date_str = request.query_params.get("date")

        tasks = Task.objects.all()

        # -------------------------
        # Status filter
        # -------------------------
        if status_filter:
            if status_filter not in self.ALLOWED_STATUSES:
                return Response(
                    {"error": "Invalid status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tasks = tasks.filter(status=status_filter)

        # -------------------------
        # Date-based filtering priority
        # date > period > year/month
        # -------------------------
        now = timezone.localdate()

        if date_str:
            parsed_date = parse_date(date_str)
            if not parsed_date:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tasks = tasks.filter(created_at__date=parsed_date)

        elif period:
            if period not in self.ALLOWED_PERIODS:
                return Response(
                    {"error": "Invalid period. Use today, week, or month"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if period == "today":
                tasks = tasks.filter(created_at__date=now)

            elif period == "week":
                start_of_week = now - timedelta(days=now.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                tasks = tasks.filter(
                    created_at__date__range=(start_of_week, end_of_week)
                )

            elif period == "month":
                tasks = tasks.filter(
                    created_at__year=now.year,
                    created_at__month=now.month,
                )

        else:
            if year:
                tasks = tasks.filter(created_at__year=int(year))
            if month:
                tasks = tasks.filter(created_at__month=int(month))

        # -------------------------
        # Serialize
        # -------------------------
        serializer = TaskSerializer(tasks, many=True)

        # -------------------------
        # Total price calculation
        # -------------------------
        total_price = 0
        for task in tasks.only("price"):
            try:
                total_price += json.loads(task.price).get("Total", 0)
            except (TypeError, ValueError):
                continue

        return Response(
            {
                "status": status_filter or "All",
                "period": period,
                "total_offers": tasks.count(),
                "total_price": total_price,
                "tasks": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

        
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
