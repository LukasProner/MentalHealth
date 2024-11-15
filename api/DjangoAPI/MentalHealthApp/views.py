from django.shortcuts import  render, redirect
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.response import Response
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from MentalHealthApp.models import User
from MentalHealthApp.serializers import UserSerializer
from django.core.files.storage import default_storage
# from .forms import RegistrationForm
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
import json
import jwt,datetime

class RegisterView(APIView):
    def post(self,request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self,request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        payload = {
            'id':user.id,
            'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat':datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm = 'HS256')

        response = Response()

        response.set_cookie(key='jwt',value=token, httponly = True)

        response.data = {
            'jwt':token
        }

        return response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')
        try:
            payload = jwt.decode(token,'secret',algorithms = ['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id = payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class LogoutView(APIView):
    def post(self,request):
        response = Response()
        response.delete_cookie('jwt')
        response.data= {
            'message':'success'
        }
        return response

@csrf_exempt
def userApi(request,id=0):
    if request.method=='GET':
        users = User.objects.all()
        user_serializer=UserSerializer(users,many=True)# Serializuje získané dáta do JSON formátu pomocou UserSerializer
        return JsonResponse(user_serializer.data,safe=False)
    elif request.method=='POST':
        user_data=JSONParser().parse(request)
        user_serializer=UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("Added Successfully",safe=False)
        return JsonResponse("Failed to Add",safe=False)
    elif request.method=='PUT':
        user_data=JSONParser().parse(request)
        user=User.objects.get(UserId=user_data['UserId'])
        user_serializer=UserSerializer(user,data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("Updated Successfully",safe=False)
        return JsonResponse("Failed to Update")
    elif request.method == 'DELETE':
        try:
            user = User.objects.get(UserId=id)
        except User.DoesNotExist:
            return JsonResponse("User not found", status=404, safe=False)

        user.delete()
        return JsonResponse("Deleted Successfully", safe=False)

@csrf_exempt
def SaveFile(request):
    file=request.FILES['file']
    file_name=default_storage.save(file.name,file)
    return JsonResponse(file_name,safe=False)



# @api_view(['POST'])
# @csrf_exempt
# def logout_user(request):
#     logout(request)
#     return Response({'message': 'Successfully logged out!'}, status=status.HTTP_200_OK)

# @api_view(['GET'])
# @csrf_exempt
# def check_login_status(request):
#     if request.user.is_authenticated:
#         return Response({'is_authenticated': True, 'username': request.user.username})
#     else:
#         return Response({'is_authenticated': False})

# def user_profile(request):
#     if request.user.is_authenticated:
#         return JsonResponse({'username': request.user.username, 'email': request.user.email})
#     else:
#         return JsonResponse({'message': 'User is not logged in'}, status=401)


# def login_user(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             username = data.get('username')
#             password = data.get('password')

#             try:
#                 user = User.objects.get(username=username)
#                 if user.check_password(password):
#                     login(request, user)
#                     # Vráť údaje o používateľovi
#                     return JsonResponse({
#                         'status': 'success',
#                         'username': user.username,
#                         'email': user.email,
#                         'is_authenticated': True
#                     }, status=200)
#                 else:
#                     return JsonResponse({'status': 'error', 'message': 'Invalid password'}, status=400)
#             except User.DoesNotExist:
#                 return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# def current_user(request):
#     if request.user.is_authenticated:
#         return JsonResponse({
#             'status': 'success',
#             'username': request.user.username,
#             'email': request.user.email
#         })
#     else:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'No user is currently logged in'
#         }, status=401)


import base64
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ImageModel

class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        image_data = data.get('image')
        if image_data:
            # Decode the Base64 image
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name=f"uploaded.{ext}")

            # Save the image to the database
            image_instance = ImageModel.objects.create(image=image)
            return Response({"message": "Obrázok bol uložený."})
        return Response({"error": "Žiadny obrázok nebol odoslaný."}, status=400)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Test, Question
from .serializers import TestSerializer, QuestionSerializer

class TestListView(APIView):
    def post(self, request):
        name = request.data.get('name')
        test = Test.objects.create(name=name)
        return Response({'id': test.id, 'name': test.name}, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        tests = Test.objects.all()  # Načítanie všetkých testov
        serializer = TestSerializer(tests, many=True)  # Serializácia testov
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuestionListView(APIView):
    def post(self, request, test_id):
        text = request.data.get('text')
        answer = request.data.get('answer')
        test = Test.objects.get(id=test_id)
        question = Question.objects.create(test=test, text=text, answer=answer)
        return Response({'id': question.id, 'text': question.text, 'answer': question.answer}, status=status.HTTP_201_CREATED)

class TestDetailView(APIView):
    def get(self, request, id):
        try:
            test = Test.objects.get(id=id)
            serializer = TestSerializer(test)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)