from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('LEARNER', 'Learner / Umunyeshuri'),
        ('INSTRUCTOR', 'Instructor / Umwigisha'),
        ('ADMIN', 'Administrator / Umuyobozi'),
    ]

    LANGUAGE_CHOICES = [
        ('rw', 'Ikinyarwanda'),
        ('en', 'English'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='LEARNER',
        verbose_name="User Role"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Phone Number (e.g. +250 788...)"
    )
    national_id = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name="National ID (Indangamuntu - 16 digits)"
    )
    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='rw',
        verbose_name="Preferred Exam Language"
    )
    target_exam_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Target Exam Date"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Short Bio"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_learner(self):
        return self.role == 'LEARNER'

    @property
    def is_instructor(self):
        return self.role == 'INSTRUCTOR' or self.is_staff or self.is_superuser

    @property
    def is_administrator(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

