from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import JSONField
from django.utils.crypto import get_random_string
from pydantic import ValidationError

class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    is_admin = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True  
        return False 
    
    def has_module_perms(self, app_label):
        if self.is_admin:
            return True  
        return False 
    

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
        ('drawing','Drawing')
    ]
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    question_type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPES,
        default='boolean'
    )
    options = JSONField(blank=True, null=True)  
    category = models.CharField(max_length=100, blank=True, null=True, default='Nezaradená')
    image_url = models.CharField(max_length=500, blank=True, null=True)  # Uloží URL obrázka
    
    def save(self, *args, **kwargs):
        if self.question_type == 'choice' and isinstance(self.options, str):
            self.options = [{'text': opt.strip(), 'value': 0} for opt in self.options.split(',')]
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
    category = models.CharField(max_length=100, blank=True, null=True, default='Nezaradená')

    def save(self, *args, **kwargs):
        self.category = self.question.category
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.submission.user.email} - {self.question.text}: {self.answer}"

class Scale(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="scales")
    min_points = models.PositiveIntegerField()
    max_points = models.PositiveIntegerField()
    response = models.TextField()
    category = models.CharField(max_length=100, default='Nezaradená')

    def clean(self):
        # Validácia rozpätí bodov
        if self.min_points >= self.max_points:
            raise ValidationError("Minimálne body musia byť menšie ako maximálne body.")

        # Overenie, že rozsahy bodov sa neprekrývajú pre tento test
        overlapping_scales = Scale.objects.filter(
            test=self.test,
            max_points__gte=self.min_points,
            min_points__lte=self.max_points,
        ).exclude(pk=self.pk)
        if overlapping_scales.exists():
            raise ValidationError("Rozpätia bodov sa prekrývajú s existujúcim škálovaním.")

    def __str__(self):
        return f"{self.min_points} - {self.max_points}: {self.response}"
    
# class Drawing(models.Model):
#     question = models.ForeignKey(Question, related_name = 'drawing_answears', on_delete=models.CASCADE)
#     image = models.TextField()

class RecordedVideo(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    