from rest_framework import serializers
from MentalHealthApp.models import User, Question, Test, TestSubmission, QuestionAnswer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','name','email','password']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    def create(self,validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = '__all__'
    
    def get_options(self, obj):
        if isinstance(obj.options, str):
            return [opt.strip() for opt in obj.options.split(',')]
        return obj.options

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'

class TestSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSubmission
        fields = ['id', 'user', 'test', 'submitted_at']



class QuestionAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text')  # Zahrnutie textu otázky
    question_type = serializers.CharField(source='question.question_type')  # Typ otázky

    class Meta:
        model = QuestionAnswer
        fields = ['question_text', 'question_type', 'answer']
