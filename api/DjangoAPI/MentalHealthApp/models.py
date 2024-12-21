from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import JSONField
from django.utils.crypto import get_random_string

class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255,unique=True )  # Povinné
    password = models.CharField(max_length=255)  # Django už zahŕňa šifrovanie hesiel
    username = None
   
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = []

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images/')


class Test(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='tests', on_delete=models.CASCADE)
    test_code = models.CharField(max_length=10, unique=True, blank=True)  # Unikátny kód

    def save(self, *args, **kwargs):
        # Automaticky generovať test_code, ak ešte neexistuje
        if not self.test_code:
            self.test_code = get_random_string(10)  # 10 náhodných znakov
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Question(models.Model):
    QUESTION_TYPES = [
        ('boolean', 'Yes/No'),
        ('choice', 'Multiple Choice'),
        ('text', 'Text Response'),
    ]
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    question_type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPES,
        default='boolean'
    )
    options = JSONField(blank=True, null=True)  # CSV pre možnosti, ak je question_type "choice"
    correct_answer = models.TextField(blank=True, null=True)  # Správna odpoveď (voliteľná)
    
    def save(self, *args, **kwargs):
        if self.question_type == 'choice' and isinstance(self.options, str):
            self.options = [opt.strip() for opt in self.options.split(',')]
        super().save(*args, **kwargs)
        

class TestSubmission(models.Model):
    test_code = models.CharField(max_length=255, unique=True)  
    test = models.ForeignKey(Test, related_name='submissions', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test: {self.test.name} - Code: {self.test_code}"

    
class QuestionAnswer(models.Model):
    submission = models.ForeignKey(TestSubmission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    answer = models.TextField()  

    def __str__(self):
        return f"{self.submission.user.email} - {self.question.text}: {self.answer}"