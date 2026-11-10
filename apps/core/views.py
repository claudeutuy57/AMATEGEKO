from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from apps.curriculum.models import Category, RoadSign, Lesson
from apps.examinations.models import Question, ExamAttempt
from .models import ContactMessage

def home_view(request):
    """Modern homepage with hero, statistics, featured signs, and examination quick-launch."""
    featured_signs = RoadSign.objects.all().order_by('?')[:8]
    categories = Category.objects.all().order_by('order')[:6]
    total_questions = Question.objects.filter(is_active=True).count()
    total_signs = RoadSign.objects.count()
    total_tests_taken = ExamAttempt.objects.count()

    context = {
        'featured_signs': featured_signs,
        'categories': categories,
        'total_questions': total_questions,
        'total_signs': total_signs,
        'total_tests_taken': total_tests_taken,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    """About page explaining the platform, Rwanda traffic safety, and legal foundation."""
    return render(request, 'core/about.html')


def contact_view(request):
    """Contact page with form and official emergency contact numbers."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject or 'General Inquiry',
                message=message_text
            )
            messages.success(request, "Ubutumwa bwanyu bwakiriwe neza! Tuzabuvugisha vuba. (Your message has been received!)")
            return redirect('core:contact')
        else:
            messages.error(request, "Nyamuneka uzuza imyanya yose isabwa. (Please fill in all required fields.)")

    return render(request, 'core/contact.html')


def search_view(request):
    """Global search across Road Signs, Traffic Rules/Lessons, and Questions."""
    query = request.GET.get('q', '').strip()
    sign_results = []
    lesson_results = []
    question_results = []

    if query:
        sign_results = RoadSign.objects.filter(
            Q(code__icontains=query) |
            Q(name_rw__icontains=query) |
            Q(name_en__icontains=query) |
            Q(meaning_rw__icontains=query)
        )[:10]

        lesson_results = Lesson.objects.filter(
            Q(title_rw__icontains=query) |
            Q(title_en__icontains=query) |
            Q(content_rw__icontains=query)
        )[:10]

        question_results = Question.objects.filter(
            Q(question_text_rw__icontains=query) |
            Q(question_text_en__icontains=query) |
            Q(explanation_rw__icontains=query)
        )[:10]

    context = {
        'query': query,
        'sign_results': sign_results,
        'lesson_results': lesson_results,
        'question_results': question_results,
        'total_found': len(sign_results) + len(lesson_results) + len(question_results)
    }
    return render(request, 'core/search.html', context)

