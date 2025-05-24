from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

# Create your views here.
User = get_user_model()

class EmailDuplicateCheckView(APIView):
    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response({"error": "email is required"}, status=status.HTTP_400_BAD_REQUEST)

        is_duplicate = User.objects.filter(email=email).exists()
        return Response({"is_duplicate": is_duplicate})
