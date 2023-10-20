from rest_framework import generics


class UserSerializer:
    pass


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
