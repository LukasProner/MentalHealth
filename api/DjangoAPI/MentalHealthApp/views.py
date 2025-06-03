from django.http.response import JsonResponse
from rest_framework.response import Response
from MentalHealthApp.models import User, TestSubmission, Question, QuestionAnswer,  Scale, Test,  RecordedVideo, Documentation
from MentalHealthApp.serializers import UserSerializer
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.views import APIView
import jwt,datetime
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from .serializers import ScaleSerializer, TestSerializer, QuestionSerializer,  TestSubmissionSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed, NotFound
from django.core.files.images import get_image_dimensions
import uuid
import os
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class RegisterView(APIView):
    def post(self,request):
        serializer=UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self,request):
        email=request.data['email']
        password=request.data['password']

        user=User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('neautentifikovany pouzivatel')

        if not user.check_password(password):
            raise AuthenticationFailed('zle heslo')
        
        payload={
            'id':user.id,
            'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=60),
            'iat':datetime.datetime.utcnow()
        }

        token=jwt.encode(payload, 'secret',algorithm='HS256')

        response=Response() #vytvorenie nového objektu odpovede (response), ktorý bude použitý na vrátenie odpovede zo servera.

        response.set_cookie(key='jwt',value=token, httponly = True) #ukladá token ako cookie s názvom jwt

        response.data={
            'jwt':token
        }

        return response

class UserView(APIView):
    def get(self,request):
        token=request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        try:
            payload = jwt.decode(token,'secret',algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('neautentifikovany pouzivatel')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class LogoutView(APIView):
    def post(self,request):
        response=Response()
        response.delete_cookie('jwt')
        response.data={
            'message':'success'
        }
        return response

class UploadImageView(APIView):
    
    def post(self,request):
        if 'image' not in request.FILES:
            return Response({"error":"nebol poslany obrazok"},status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        file_extension=os.path.splitext(image_file.name)[1].lower() #získava príponu súboru z názvu súboru, prevádza ju na malé písmená 
        if file_extension not in ALLOWED_EXTENSIONS:
            return Response({"error": "nespravny typ suboru"}, status=status.HTTP_400_BAD_REQUEST)

        if image_file.size > MAX_FILE_SIZE:
            return Response({"error": "subor ma viac ako 5MB"}, status=status.HTTP_400_BAD_REQUEST)

        # kontrola rozmerov
        try:
            width,height=get_image_dimensions(image_file)
        except Exception:
            return Response({"error": "zle rozmery suboru"},status=status.HTTP_400_BAD_REQUEST)

        # Generovanie bezpečného názvu súboru (pomocou UUID)
        safe_filename=f"{uuid.uuid4().hex}{file_extension}"

        file_path=default_storage.save(f'questions/{safe_filename}', ContentFile(image_file.read()))

        image_url=request.build_absolute_uri(f'/media/{file_path}')

        return Response({"image_url": image_url}, status=status.HTTP_201_CREATED)


# User = get_user_model()

class TestListView(APIView):
    def post(self, request):
        token=request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        try:
            payload = jwt.decode(token,'secret',algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token vyprsal')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('neautentifikovany pouzivatel')

        name=request.data.get('name')
        test=Test.objects.create(name=name, created_by=user)

        return Response({'id': test.id,'name': test.name}, status=status.HTTP_201_CREATED)

    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token vyprsal')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        tests = Test.objects.filter(created_by=user)
        serializer = TestSerializer(tests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class QuestionListView(APIView):
    def post(self,request,test_id):
        token=request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('neautentifikovany pouzivatel')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token vyprsal')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('neautentifikovany pouzivatel')

        try:
            test = Test.objects.get(id=test_id, created_by=user)
        except Test.DoesNotExist:
            return Response({'error': 'test neexistuje/nie si autentifikovany'}, status=status.HTTP_404_NOT_FOUND)

        question_type=request.data.get('question_type','boolean')
        text = request.data.get('text')
        options=request.data.get('options', '') 
        category=request.data.get('category') 
        imageURL=request.data.get('image_url')

        if not category:
            return Response({'error': 'chyba category'}, status=status.HTTP_400_BAD_REQUEST)

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

    def put(self,request,question_id):
        token=request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token vyprsal')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('neautentifikovany pouzivatel')

        question = Question.objects.filter(id=question_id, test__created_by=user).first()
        if not question:
            raise NotFound('nenajdena otazka!')

        # Aktualizuj otázku na základe dát z požiadavky
        question.text = request.data.get('text', question.text)
        question.question_type = request.data.get('question_type', question.question_type)
        question.category = request.data.get('category', question.category)  
        question.options = request.data.get('options', question.options)
        question.save()

        return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)


    def delete(self, request, question_id):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        try:
            payload = jwt.decode(token,'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token vyprsal')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('neautentifikovany pouzivatel')

        question = Question.objects.filter(id=question_id).first()
        if not question:
            raise NotFound('nenajdena otazka')

        question.delete()
        return Response({"message": "otazka odstranena"}, status=status.HTTP_204_NO_CONTENT)
    
    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise NotFound('nenajdena otazka')
        # return Response({
        #     "id": question.id,
        #     "text": question.text,
        #     "test_id": question.test_id,
        #     "options": question.options,
        #     "question_type": question.question_type,
        #     "category": question.category,
        #     "image_url": question.image_url
        # }, status=status.HTTP_200_OK)
        return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)


class TestDetailView(APIView):
    def get(self, request, id):
        try:
            test = Test.objects.get(id=id)
        except Test.DoesNotExist:
            return Response({'error':'chyba test'},status=status.HTTP_404_NOT_FOUND)
        
        if test.created_by.is_admin:
            serializer = TestSerializer(test)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        token = request.COOKIES.get('jwt')
        if not token:
            return Response({'error':'neautentifikovany pouzivatel'},status=status.HTTP_401_UNAUTHORIZED)
        try:
            payload=jwt.decode(token,'secret', algorithms=['HS256'])
            user_id=payload['id']
        except jwt.ExpiredSignatureError:
            return Response({'error':'token vyprsal'},status=status.HTTP_401_UNAUTHORIZED)
        
        if test.created_by.id != user_id:
            return Response({'error':'neautentifikovany pouzivatel'},status=status.HTTP_403_FORBIDDEN)
        
        serializer = TestSerializer(test)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def delete(self, request, id):
        try:
            test = Test.objects.get(id=id) 
            questions = Question.objects.filter(test=test)
            for question in questions:
                videos = RecordedVideo.objects.filter(question_id=question.id)
                for video in videos:
                    if video.video_file:
                        video.video_file.delete(save=False)  

                if question.image_url:
                    # Získaj relatívnu cestu z úplnej URL
                    media_url = request.build_absolute_uri('/media/')
                    if question.image_url.startswith(media_url):
                        relative_path = question.image_url.replace(media_url, '')
                        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                        if os.path.exists(file_path):
                            os.remove(file_path)

            test.delete() 
            return Response({"message":"test odstraneny"}, status=status.HTTP_204_NO_CONTENT)
        except Test.DoesNotExist:
            return Response({"error":"test neexistuje"}, status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        token=request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token vyprsal')
        
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('neautentifikovany pouzivatel')
        try:
            test=Test.objects.get(id=id, created_by=user)
        except Test.DoesNotExist:
            return Response({'error':'chyba test'},status=status.HTTP_404_NOT_FOUND)

        test_name=request.data.get('name')
        if test_name:
            test.name=test_name
            test.save()

        return Response(
            {'id': test.id,'name': test.name},
            status=status.HTTP_200_OK
        )

class SubmitTestView(APIView):
    def post(self, request, test_id):
        test_code = request.data.get('test_code')
        if not test_code:
            return Response({'error':'zly code'},status=status.HTTP_400_BAD_REQUEST)
        try:
            test = Test.objects.get(id=test_id, test_code=test_code)
        except Test.DoesNotExist:
            return Response(
                {'error': 'chyba test'},
                status=status.HTTP_404_NOT_FOUND
            )

        submission=TestSubmission.objects.create(test_code=test_code, test=test)
        answers=request.data.get('answers', [])
        for answer_data in answers:
            question_id=answer_data.get('question_id')
            answer_text=answer_data.get('answer')

            question=get_object_or_404(Question,id=question_id,test=test)

            QuestionAnswer.objects.create(
                submission=submission,
                question=question,
                answer=answer_text
            )

        return Response({"message": "submit correct"}, status=status.HTTP_201_CREATED)

import ast
class TestResponsesView(APIView):
    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        submissions = TestSubmission.objects.filter(test=test)
        response_data = []
        for submission in submissions:
            answers = submission.answers.all()
            # zatial bez serializera
            response_data.append({
                "submitted_at": submission.submitted_at,
                "answers": [
                    {   
                        "question_id":answer.question.id,
                        "question":answer.question.text, 
                        "answer": self.extract_answer_text(answer.answer),
                        "answer_id":answer.id  
                    }
                    for answer in answers
                ]
            })

        return Response(response_data, status=status.HTTP_200_OK)
    
    def extract_answer_text(self,  answer):
        try:
            parsed = ast.literal_eval( answer) #Premení textový reťazec, ktorý vyzerá ako Python objekt, na skutočný objekt. - cize odsstani vonkajsie uvodzovky
            if isinstance(parsed, dict) and 'text' in parsed:
                return parsed['text']
        except (ValueError, SyntaxError):
            # Ak odpoveď nie je validný Python objekt, vrátime pôvodný reťazec
            return answer
 
    
    
class PublicTestView(APIView):
    def post(self,request,test_id,*args,**kwargs):
        # print(f"Received request for test ID: {test_id}")
        test_code=request.data.get("test_code")
        try:
            test = Test.objects.get(id=test_id, test_code=test_code)
            #asi lepsie potom pridat serializer ale kym neopravim 
            return Response({
                "id": test.id,
                "name": test.name,
                "questions":[
                    {"id": q.id, "text": q.text, "question_type": q.question_type, "options": q.options, "category": q.category, "image_url": q.image_url}
                    for q in test.questions.all()
                ]
            })
        except Test.DoesNotExist:
            return Response({"error": "neplatny kod/chyba test"},status=status.HTTP_400_BAD_REQUEST)


class ScaleView(APIView):
    def get(self,request,test_id):
        try:
            test=Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"error":"chyba test"}, status=status.HTTP_404_NOT_FOUND)

        scales=Scale.objects.filter(test=test)
        serializer=ScaleSerializer(scales,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,test_id):
        try:
            test=Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"error":"chyba test"},status=status.HTTP_404_NOT_FOUND)

        data=request.data
        if not isinstance(data, list):
            return Response({"error": "udaje niesu vo forme zoznamu"},status=status.HTTP_400_BAD_REQUEST)

        for scale_data in data:
            scale_data['test']=test.id 
        serializer=ScaleSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,test_id):
        try:
            test=Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"error":"chyba test"}, status=status.HTTP_404_NOT_FOUND)

        scales=Scale.objects.filter(test=test)
        scales.delete()
        return Response({"message":"skaly boli odstranene"}, status=status.HTTP_204_NO_CONTENT)
    

class EvaluateTestView(APIView):
    def post(self, request,test_id):
        try:
            # print("Request data:", request.data)
            test=Test.objects.get(pk=test_id)
            scales=Scale.objects.filter(test=test)

            user_answers=request.data.get('answers',[])
            # print("User answers:", user_answers)

            category_scores={} 
            
            for answer in user_answers:
                if not isinstance(answer,dict):
                    # print(f"invaldi format: {answer}")
                    continue
                question_id=answer.get('question_id')
                answer_data=answer.get('answer', {})
                if not isinstance(answer_data, dict):
                    # print(f"invalid answer format{question_id},{answer_data}")
                    continue
                if answer_data.get('hasValue'):
                    value = answer_data.get('value',0)
                    if isinstance(value, str):
                        if value=='null':
                            value=0
                        else:
                            try:
                                value=int(value)
                            except ValueError:
                                value=0
                    question=Question.objects.get(pk=question_id)
                    question_category=(question.category or 'Nezaradená').strip()
                    # print(f"\n(category:{question_category}) value: {value}")

                    if question_category not in category_scores:
                        category_scores[question_category]=0
                    category_scores[question_category]+=value

            # print(f"cat scores: {category_scores}")

            responses=[]
            for category,score in category_scores.items():
                matching_scales=scales.filter(category=category)
                # print("matching_scales",matching_scales ," category ", category)

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

            if not responses:
                return Response({"error": "no scales match"},status=status.HTTP_400_BAD_REQUEST)

            # print({"total_score": responses})
            return Response({"total_score": responses}, status=status.HTTP_200_OK)
        # except Test.DoesNotExist:
        #     return Response({"error": "chyba test."}, status=status.HTTP_404_NOT_FOUND)
        # except Question.DoesNotExist:
        #     return Response({"error": "Invalid question ID provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # print(f"Error: {str(e)}")
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestListAdmin(APIView):
    def get(self,request,*args,**kwargs):
        token = request.COOKIES.get('jwt')
        user = None
        is_admin = False

        if token:
            try:
                payload=jwt.decode(token, 'secret', algorithms=['HS256'])
                user_id=payload.get('id')  
                user=User.objects.filter(id=user_id).first()
                if user:
                    is_admin=user.is_admin
            except Exception as e:
                return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
        if is_admin:
            tests=Test.objects.all().values('id','name','created_by__name')
        else:
            tests=Test.objects.filter(created_by__is_admin=True).values('id', 'name')

        return Response({"tests":list(tests)}, status=200)

class UloadDrawingView(APIView):
    def post(self,request):
        image_file = request.FILES.get('image')
        question_id = request.POST.get('question_id')

        if not image_file or not question_id:
            return Response({"error": "Chýbajúci obrázok alebo question_id"},status=status.HTTP_400_BAD_REQUEST)

        # Validácia a uloženie obrázku
        file_extension=os.path.splitext(image_file.name)[1].lower()
        safe_filename=f"{uuid.uuid4().hex}{file_extension}"
        file_path=default_storage.save(f'questions/{safe_filename}', ContentFile(image_file.read()))
        image_url=request.build_absolute_uri(f'/media/{file_path}')

        try:
            question=Question.objects.get(id=question_id)
            question.image_url=image_url
            question.save()
        except Question.DoesNotExist:
            return Response({"error": "chyba otazka"},status=status.HTTP_404_NOT_FOUND)

        return Response({"image_url": image_url},status=status.HTTP_201_CREATED)
        
    def get(self,request,questionId):
        try:
            question = Question.objects.get(id=questionId)
            if question.image_url:
                return Response({"image_url":question.image_url},status=status.HTTP_200_OK)
            else:
                return Response({"message":"otzka nema obr"}, status=status.HTTP_204_NO_CONTENT)
        except Question.DoesNotExist:
            return Response({"error": "chyba otazka."}, status=status.HTTP_404_NOT_FOUND)


class SaveVideoView(APIView):
    def post(self,request,*args,**kwargs):
        video_file=request.FILES.get('video')  
        question_id=request.POST.get('question_id')
        # print("question_id",question_id)
        # print("video_file",video_file)

        if not video_file or not question_id:
            return JsonResponse({'error': 'invalid data'},status=status.HTTP_400_BAD_REQUEST)

        RecordedVideo.objects.filter(question_id=question_id).delete()
        recorded_video = RecordedVideo.objects.create(
            question_id=question_id,
            video_file=video_file
        )
        return JsonResponse({'message':'video ulozene','id':recorded_video.id})
    
    def get(self,request,video_id):
        print("video_id",video_id)
        video=get_object_or_404(RecordedVideo, question_id=video_id)
        print("video", video)
        return JsonResponse({'video_url': video.video_file.url})



class DocumentationView(APIView):
    def get(self,request,test_id):
        try:
            testDoc = Documentation.objects.get(testId = test_id)
            print("content = ", testDoc.content)
            return JsonResponse({'content':testDoc.content, "title":testDoc.name})
        except:
            return JsonResponse({'error':'documentations error'}, status= status.HTTP_400_BAD_REQUEST)
        
    def post(self,request,test_id):
        content = request.data.get('content')
        name = request.data.get('name')
        test = Test.objects.get(pk=test_id)

        Documentation.objects.create(name = name, content = content, testId = test)
        return Response({"message": "submit correct"}, status=status.HTTP_201_CREATED)


