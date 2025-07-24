from rest_framework.decorators import api_view
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from .models import Note
from .serializers import (
    NoteSerializer,
    UserSerializer,
    RegisterSerializer,
    LoginSerializer
)
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

# API docs tag info (for drf-yasg)
user_tag = ["User"]
note_tag = ["Note"]
auth_tag = ["Auth"]

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """
    Health check endpoint.
    ---
    tags:
      - health
    responses:
      200:
        description: Returns a health message.
    """
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
class RegisterView(APIView):
    """
    Register a new user.
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: ["username", "email", "password"]
            properties:
              username:
                type: string
              email:
                type: string
              password:
                type: string
    responses:
      201:
        description: User registered successfully.
      400:
        description: Error with registration.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
class LoginView(APIView):
    """
    Authenticate an existing user and obtain an auth token.
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: ["username", "password"]
            properties:
              username:
                type: string
              password:
                type: string
    responses:
      200:
        description: User info and token.
      400:
        description: Invalid credentials.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data})
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
class LogoutView(APIView):
    """
    Logout current user.
    ---
    tags:
      - Auth
    requestBody: {}
    responses:
      200:
        description: Logged out.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})

# PUBLIC_INTERFACE
class UserProfileView(APIView):
    """
    Get current user's profile.
    ---
    tags:
      - User
    responses:
      200:
        description: User profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

# PUBLIC_INTERFACE
class NoteListCreateView(generics.ListCreateAPIView):
    """
    List notes or create a note for current user.
    ---
    tags:
      - Note
    parameters:
      - name: q
        in: query
        description: Search string for title/content
        required: false
        schema:
          type: string
    responses:
      200:
        description: List of notes
      201:
        description: Note created
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get("q", None)
        user_notes = Note.objects.filter(owner=self.request.user)
        if query:
            user_notes = user_notes.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        return user_notes.order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# PUBLIC_INTERFACE
class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a note by ID.
    ---
    tags:
      - Note
    parameters:
      - name: pk
        in: path
        required: true
        description: ID of the note
        schema:
          type: integer
    responses:
      200:
        description: Note details
      204:
        description: Deleted note
      403:
        description: Permission denied
      404:
        description: Not found
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can access only their own notes
        return Note.objects.filter(owner=self.request.user)
