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
from rest_framework.response import Response
from rest_framework import status
from .models import TestSubmission, Question, QuestionAnswer
from django.shortcuts import get_object_or_404
import base64
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ImageModel, Scale
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Test, Question, Drawing
from .serializers import ScaleSerializer, TestSerializer, QuestionSerializer,  TestSubmissionSerializer
import jwt
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt
from .models import RecordedVideo

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


 
class UploadImageView(APIView):
    def post(self, request):
        # Skontroluj, či je v požiadavke obrázok
        if 'image' not in request.FILES:
            return Response({"error": "No image uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Získame obrázok
        image_file = request.FILES['image']

        # Uložíme obrázok na server (default_storage môže byť disk alebo cloud)
        file_path = default_storage.save(f'questions/{image_file.name}', ContentFile(image_file.read()))

        # Získame URL obrázka
        image_url = request.build_absolute_uri(f'/media/{file_path}')

        # Vrátime URL obrázka
        return Response({"image_url": image_url}, status=status.HTTP_201_CREATED)

# from rest_framework.parsers import MultiPartParser, FormParser
# from .serializers import ImageSerializer
# class ImageUploadView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         file_serializer = ImageSerializer(data=request.data)

#         if file_serializer.is_valid():
#             file_serializer.save()
#             return Response(file_serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()

class TestListView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        name = request.data.get('name')
        test = Test.objects.create(name=name, created_by=user)

        return Response({'id': test.id, 'name': test.name}, status=status.HTTP_201_CREATED)

    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')
        tests = Test.objects.filter(created_by=user)
        serializer = TestSerializer(tests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class QuestionListView(APIView):
    def post(self, request, test_id):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        try:
            test = Test.objects.get(id=test_id, created_by=user)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found or not authorized!'}, status=status.HTTP_404_NOT_FOUND)

        question_type = request.data.get('question_type', 'boolean')
        text = request.data.get('text')
        options = request.data.get('options', '')  # CSV možnosti
        category = request.data.get('category')  # Pridanie kategórie
        imageURL = request.data.get('image_url')

        if not category:
            return Response({'error': 'Category is required!'}, status=status.HTTP_400_BAD_REQUEST)

        question = Question.objects.create(
            test=test,
            text=text,
            question_type=question_type,
            options=options,
            category=category,
            image_url = imageURL,
        )

        return Response(
            {'id': question.id, 'text': question.text, 'type': question.question_type, 'category': question.category, 'options': question.options, 'image_url': question.image_url},
            status=status.HTTP_201_CREATED
        )

    def put(self, request, question_id):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        question = Question.objects.filter(id=question_id, test__created_by=user).first()
        if not question:
            raise NotFound('Question not found!')

        # Aktualizuj otázku na základe dát z požiadavky
        question.text = request.data.get('text', question.text)
        question.question_type = request.data.get('question_type', question.question_type)
        question.category = request.data.get('category', question.category)  # Pridanie aktualizácie kategórie
        question.options = request.data.get('options', question.options)
        question.save()

        return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)


    def delete(self, request, question_id):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        question = Question.objects.filter(id=question_id).first()
        if not question:
            raise NotFound('Question not found!')

        question.delete()
        return Response({"message": "Question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise NotFound('Question not found')
        return Response({
            "id": question.id,
            "text": question.text,
            "test_id": question.test_id,
            "options": question.options,
            "question_type": question.question_type,
            "category": question.category,
            "image_url": question.image_url
        }, status=status.HTTP_200_OK)


class TestDetailView(APIView):
    def get(self, request, id):
        try:
            # Načítaj test podľa ID
            test = Test.objects.get(id=id)
        except Test.DoesNotExist:
            return Response(
                {'error': 'Test not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Ak je test vytvorený adminom, je prístupný všetkým
        if test.created_by.is_admin:
            serializer = TestSerializer(test)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Ak nie je vytvorený adminom, overíme, či je používateľ autentifikovaný
        token = request.COOKIES.get('jwt')
        if not token:
            return Response(
                {'error': 'Unauthorized access'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user_id = payload['id']
        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'Token has expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Overíme, či je autentifikovaný používateľ autorom testu
        if test.created_by.id != user_id:
            return Response(
                {'error': 'Not authorized to view this test'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ak je používateľ autorom testu, vrátime dáta
        serializer = TestSerializer(test)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        try:
            test = Test.objects.get(id=id) 
            test.delete() 
            return Response({"message": "Test bol úspešne odstránený."}, status=status.HTTP_204_NO_CONTENT)
        except Test.DoesNotExist:
            return Response({"error": "Test s daným ID neexistuje."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        # Token validation
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        try:
            test = Test.objects.get(id=id, created_by=user)
        except Test.DoesNotExist:
            return Response(
                {'error': 'Test not found or not authorized'},
                status=status.HTTP_404_NOT_FOUND
            )

        test_name = request.data.get('name')
        if test_name:
            test.name = test_name
            test.save()

        return Response(
            {'id': test.id, 'name': test.name},
            status=status.HTTP_200_OK
        )


class SubmitTestView(APIView):
    def post(self, request, test_id):
        test_code = request.data.get('test_code')
        if not test_code:
            return Response(
                {'error': 'Test code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            test = Test.objects.get(id=test_id, test_code=test_code)
        except Test.DoesNotExist:
            return Response(
                {'error': 'Test not found or invalid code'},
                status=status.HTTP_404_NOT_FOUND
            )

        submission = TestSubmission.objects.create(test_code=test_code, test=test)

        answers = request.data.get('answers', [])
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer')

            question = get_object_or_404(Question, id=question_id, test=test)

            QuestionAnswer.objects.create(
                submission=submission,
                question=question,
                answer=answer_text
            )

        return Response({"message": "Test submission saved successfully"}, status=status.HTTP_201_CREATED)


class TestResponsesView(APIView):
    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        submissions = TestSubmission.objects.filter(test=test).prefetch_related('answers')  # prefetch pre minimalizáciu dotazov
        #mojimi slovami - django ma akusi funkciu ktorou najde nie len ze table ale aj stlpec v nom ktory je nejako spojeny s danou dabulkou
        #slovami gpt - Django používa relácie medzi modelmi (napríklad ForeignKey), ktoré definujú vzťah medzi dvoma tabuľkami. Keď v kóde použiješ prefetch_related alebo select_related, Django vykoná optimalizované dotazy na získanie údajov z viacerých tabuliek, ktoré sú navzájom prepojené.
        response_data = []
        for submission in submissions:
            answers = submission.answers.all()
            response_data.append({
                "submitted_at": submission.submitted_at,
                "answers": [
                    {   
                        "question_id": answer.question.id,
                        "question": answer.question.text, 
                        "answer": answer.answer, 
                        "answer_id": answer.id  
                    }
                    for answer in answers
                ]
            })

        return Response(response_data, status=status.HTTP_200_OK)
    
class TestSubmissionDetailView(APIView):
    def get(self, request, test_code):
        try:
            submission = TestSubmission.objects.get(test_code=test_code)
            serializer = TestSubmissionSerializer(submission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TestSubmission.DoesNotExist:
            return Response({'error': 'Test submission not found'}, status=status.HTTP_404_NOT_FOUND)
        
class PublicTestView(APIView):
    def post(self, request, test_id, *args, **kwargs):
        print(f"Received request for test ID: {test_id}")
        test_code = request.data.get("test_code")
        try:
            test = Test.objects.get(id=test_id, test_code=test_code)
            return Response({
                "id": test.id,
                "name": test.name,
                "questions": [
                    {"id": q.id, "text": q.text, "question_type": q.question_type, "options": q.options, "category": q.category, "image_url": q.image_url}
                    for q in test.questions.all()
                ]
            })
        except Test.DoesNotExist:
            return Response({"error": "Invalid test code"}, status=status.HTTP_400_BAD_REQUEST)


class ScaleView(APIView):
    def get(self, request, test_id):
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test neexistuje."}, status=status.HTTP_404_NOT_FOUND)

        scales = Scale.objects.filter(test=test)
        serializer = ScaleSerializer(scales, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, test_id):
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test neexistuje."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if not isinstance(data, list):
            return Response(
                {"error": "Údaje musia byť vo forme zoznamu."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for scale_data in data:
            scale_data['test'] = test.id  # Pridanie ID testu do dát
        serializer = ScaleSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, test_id):
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test neexistuje."}, status=status.HTTP_404_NOT_FOUND)

        scales = Scale.objects.filter(test=test)
        scales.delete()
        return Response({"message": "Všetky škály boli odstránené."}, status=status.HTTP_204_NO_CONTENT)
    

class EvaluateTestView(APIView):
    def post(self, request, test_id):
        try:
            # Loguj celý request
            print("Request data:", request.data)
            test = Test.objects.get(pk=test_id)
            scales = Scale.objects.filter(test=test)

            # Získaj odpovede
            user_answers = request.data.get('answers', [])
            print("User answers:", user_answers)

            # Inicializácia výsledkov pre jednotlivé kategórie
            category_scores = {}  # {'category1': total_score, 'category2': total_score, ...}
            
            # Iterácia cez odpovede
            for answer in user_answers:
                if not isinstance(answer, dict):
                    print(f"Invalid answer format: {answer}")
                    continue
                question_id = answer.get('question_id')
                answer_data = answer.get('answer', {})
                if not isinstance(answer_data, dict):
                    print(f"Invalid answer data format for question {question_id}: {answer_data}")
                    continue
                if answer_data.get('hasValue'):
                    value = answer_data.get('value', 0)
                    if isinstance(value, str):
                        if value == 'null':
                            value = 0
                        else:
                            try:
                                value = int(value)
                            except ValueError:
                                value = 0
                    question = Question.objects.get(pk=question_id)

                    # Kategória otázky
                    question_category = (question.category or 'Nezaradená').strip()
                    print(f"\n(Category: {question_category}) has value: {value}")

                    # Pridaj hodnotu do správnej kategórie
                    if question_category not in category_scores:
                        category_scores[question_category] = 0
                    category_scores[question_category] += value

            print(f"Category scores: {category_scores}")

            # Výsledné odpovede na základe škál
            responses = []
            for category, score in category_scores.items():
                matching_scales = scales.filter(category=category)
                print("matching_scales", matching_scales ," category ", category)

                for scale in matching_scales:
                    if scale.min_points <= score <= scale.max_points:
                        responses.append({
                            "category": category,
                            "total_points": score,
                            "response": scale.response
                        })
                        break
                    else:
                        print("category2", category)

            # Ak neexistuje žiadna odpoveď pre danú kategóriu
            if not responses:
                return Response(
                    {"error": "No matching scales found for the provided answers."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Vráť výsledok
            print("9999")
            print({"total_score": responses})
            return Response({"total_score": responses}, status=status.HTTP_200_OK)
        except Test.DoesNotExist:
            return Response({"error": "Test not found."}, status=status.HTTP_404_NOT_FOUND)
        except Question.DoesNotExist:
            return Response({"error": "Invalid question ID provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestListAdmin(APIView):
    def get(self, request, *args, **kwargs):
        # Skontroluj, či používateľ poskytol JWT token
        token = request.COOKIES.get('jwt')
        user = None
        is_admin = False

        if token:
            try:
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
                user_id = payload.get('id')  # Predpokladá sa, že ID je v token payload
                user = User.objects.filter(id=user_id).first()
                if user:
                    is_admin = user.is_admin
            except jwt.ExpiredSignatureError:
                pass  # Token vypršal, pokračujeme ako neprihlásený používateľ
            except jwt.DecodeError:
                pass  # Neplatný token, pokračujeme ako neprihlásený používateľ

        # Logika pre načítanie testov
        if is_admin:
            # Admin vidí všetky testy
            tests = Test.objects.all().values('id', 'name', 'created_by__name')
        else:
            # Neprihlásení aj neadmini vidia len testy vytvorené adminmi
            tests = Test.objects.filter(created_by__is_admin=True).values('id', 'name')

        return Response({"tests": list(tests)}, status=200)

class UloadDrawingView(APIView):
    def post(self,request):
        print("upload drawing post")
        question_id = request.data.get('question_id')
        image_data = request.data.get('image')

        if not question_id or not image_data:
            return Response({'error':'Invalid data'}, status = 400)

        try:
            question = Question.objects.get(id = question_id)
        except Question.DoesNotExist:
            return Response({'error':'Question not found'}, status = 404)
        print(question, image_data)
        Drawing.objects.filter(question_id=question_id).delete()

        Drawing.objects.create(question = question, image = image_data)
        return Response({'message':'Drawing saved successfully'})
    def get(self, request, questionId):
        print("upload drawing get")
        print("request", request)
        print("questionId", questionId)
        drawings = Drawing.objects.filter(question_id=questionId)
        if drawings.exists():
            # Vyberieme prvý obrázok z výsledku, ak existuje viacero
            drawing = drawings.first()
            print("++++++++++++++++++++++",drawing.image)
            return JsonResponse({'drawing': drawing.image})
        else:
            return JsonResponse({'error': 'Obrázok nenájdený'}, status=404)
     

class SaveVideoView(APIView):
    def post(self, request, *args, **kwargs):
        video_file = request.FILES.get('video')  # Získanie súboru z požiadavky
        question_id = request.POST.get('question_id')
        print("question_id", question_id)
        print("video_file", video_file)

        if not video_file or not question_id:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        RecordedVideo.objects.filter(question_id=question_id).delete()

        # Uloženie videa do databázy
        recorded_video = RecordedVideo.objects.create(
            question_id=question_id,
            video_file=video_file
        )
        

        return JsonResponse({'message': 'Video saved successfully', 'id': recorded_video.id})
    
    def get(self, request, video_id):
        print("video_id", video_id)
        video = get_object_or_404(RecordedVideo, question_id=video_id)
        print("video", video)
        return JsonResponse({'video_url': video.video_file.url})
