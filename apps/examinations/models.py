from django.db import models
from django.conf import settings
from apps.curriculum.models import Category, RoadSign

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('EASY', 'Kworoshye (Easy)'),
        ('MEDIUM', 'Kuringaniye (Medium)'),
        ('HARD', 'Gikomeye (Hard)'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    question_number = models.PositiveIntegerField(unique=True, verbose_name="Question Number")
    question_text_rw = models.TextField(verbose_name="Ikibazo mu Kinyarwanda")
    question_text_en = models.TextField(blank=True, verbose_name="Question in English")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    road_sign = models.ForeignKey(RoadSign, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    explanation_rw = models.TextField(verbose_name="Ibisobanuro mu Kinyarwanda")
    explanation_en = models.TextField(blank=True, verbose_name="Explanation in English")
    legal_reference = models.CharField(
        max_length=255, 
        blank=True, 
        default="Iteka rya Perezida N° 85/01",
        verbose_name="Ingingo y'amategeko (Legal Article)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['question_number']
        verbose_name = "Theory Question"
        verbose_name_plural = "Theory Questions"

    def __str__(self):
        return f"Q{self.question_number}: {self.question_text_rw[:60]}..."

    @property
    def correct_choice(self):
        return self.choices.filter(is_correct=True).first()


class Choice(models.Model):
    LETTERS = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    letter = models.CharField(max_length=1, choices=LETTERS)
    text_rw = models.TextField(verbose_name="Igisubizo mu Kinyarwanda")
    text_en = models.TextField(blank=True, verbose_name="Answer in English")
    is_correct = models.BooleanField(default=False, verbose_name="Is Correct Answer?")

    class Meta:
        ordering = ['letter']
        unique_together = ('question', 'letter')
        verbose_name = "Question Choice"
        verbose_name_plural = "Question Choices"

    def __str__(self):
        marker = " [CORRECT]" if self.is_correct else ""
        return f"{self.letter}: {self.text_rw[:40]}...{marker}"


class ExamAttempt(models.Model):
    EXAM_TYPES = [
        ('OFFICIAL_MOCK', "Ikizamini cya Leta cy'Icyitegererezo (Official Mock Exam)"),
        ('PRACTICE', "Imyitozo (Practice Mode)"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_attempts',
        null=True,
        blank=True
    )
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='OFFICIAL_MOCK')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_attempts'
    )
    total_questions = models.PositiveIntegerField(default=20)
    correct_answers = models.PositiveIntegerField(default=0)
    score_percentage = models.FloatField(default=0.0)
    is_passed = models.BooleanField(default=False)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Exam Attempt"
        verbose_name_plural = "Exam Attempts"

    def __str__(self):
        user_label = self.user.username if self.user else "Guest"
        status = "PASSED (WATSINZE)" if self.is_passed else "FAILED (WATSINZWE)"
        return f"{user_label} - {self.get_exam_type_display()} - {self.correct_answers}/{self.total_questions} ({status})"

    def calculate_result(self, pass_mark=12):
        self.score_percentage = round((self.correct_answers / max(self.total_questions, 1)) * 100, 1)
        self.is_passed = (self.correct_answers >= pass_mark)
        return self.is_passed


class ExamAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Exam Answer"
        verbose_name_plural = "Exam Answers"

    def __str__(self):
        return f"Attempt #{self.attempt_id} - Q{self.question.question_number}: {'Correct' if self.is_correct else 'Wrong'}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'question')
        ordering = ['-created_at']
        verbose_name = "Bookmarked Question"
        verbose_name_plural = "Bookmarked Questions"

    def __str__(self):
        return f"{self.user.username} - Q{self.question.question_number}"

