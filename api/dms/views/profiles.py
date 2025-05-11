from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from dms.permissions import IsDriver
from dms.serializers import ProfileSerializer
from users.serializers import UserSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated, ~IsDriver]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        return Response({"data": ProfileSerializer(instance=request.user).data, "success": True})

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(
            data=request.data,
            instance=request.user,
            fields=("username", "email", "first_name", "last_name", "contact_number"),
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "data": ProfileSerializer(instance=user).data,
                    "success": True,
                    "message": "Profile details updated successfully.",
                }
            )
        return Response(
            {"errors": serializer.errors, "success": False}, status=HTTP_400_BAD_REQUEST
        )
