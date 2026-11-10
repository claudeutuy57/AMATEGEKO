from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Q
from apps.examinations.models import ExamAttempt, Question, Choice, Bookmark
from apps.curriculum.models import RoadSign, Category, Lesson
from apps.accounts.models import CustomUser
from .forms import QuestionForm, RoadSignForm

def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.role == 'ADMIN')


@login_required
def student_dashboard(request):
    """Personalized student dashboard with metrics, history, and readiness charts."""
    user = request.user
    attempts = ExamAttempt.objects.filter(user=user).order_by('-started_at')
    
    total_attempts = attempts.count()
    passed_attempts = attempts.filter(is_passed=True).count()
    pass_rate = round((passed_attempts / total_attempts) * 100) if total_attempts > 0 else 0
    avg_score = round(attempts.aggregate(Avg('score_percentage'))['score_percentage__avg'] or 0, 1)
    best_score = attempts.aggregate(Max('correct_answers'))['correct_answers__max'] or 0

    recent_attempts = attempts[:10]

    # Category performance breakdown
    categories = Category.objects.annotate(
        total_q=Count('questions', filter=Q(questions__is_active=True))
    ).filter(total_q__gt=0).order_by('order')

    # Bookmarks
    bookmarks = Bookmark.objects.filter(user=user).select_related('question__category')[:8]
    total_bookmarks = Bookmark.objects.filter(user=user).count()

    # Chart data: last 10 attempts
    chart_labels = []
    chart_scores = []
    for att in reversed(recent_attempts[:7]):
        chart_labels.append(att.started_at.strftime('%d/%m'))
        chart_scores.append(att.score_percentage)

    context = {
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'pass_rate': pass_rate,
        'avg_score': avg_score,
        'best_score': best_score,
        'recent_attempts': recent_attempts,
        'categories': categories,
        'bookmarks': bookmarks,
        'total_bookmarks': total_bookmarks,
        'chart_labels': chart_labels,
        'chart_scores': chart_scores,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@user_passes_test(is_admin_or_staff)
def admin_dashboard(request):
    """Admin dashboard overview."""
    total_users = CustomUser.objects.count()
    total_questions = Question.objects.count()
    total_signs = RoadSign.objects.count()
    total_lessons = Lesson.objects.count()
    total_attempts = ExamAttempt.objects.count()
    overall_pass_rate = 0
    if total_attempts > 0:
        passed = ExamAttempt.objects.filter(is_passed=True).count()
        overall_pass_rate = round((passed / total_attempts) * 100, 1)

    recent_attempts = ExamAttempt.objects.select_related('user').order_by('-started_at')[:8]
    recent_users = CustomUser.objects.order_by('-date_joined')[:6]

    context = {
        'total_users': total_users,
        'total_questions': total_questions,
        'total_signs': total_signs,
        'total_lessons': total_lessons,
        'total_attempts': total_attempts,
        'overall_pass_rate': overall_pass_rate,
        'recent_attempts': recent_attempts,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@user_passes_test(is_admin_or_staff)
def admin_questions(request):
    """Question management with filtering, searching, and pagination."""
    query = request.GET.get('q', '')
    cat_id = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')

    questions = Question.objects.select_related('category', 'road_sign').prefetch_related('choices').all()

    if query:
        questions = questions.filter(
            Q(question_text_rw__icontains=query) |
            Q(question_text_en__icontains=query) |
            Q(question_number__icontains=query)
        )
    if cat_id:
        questions = questions.filter(category_id=cat_id)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    paginator = Paginator(questions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'dashboard/admin_questions.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': cat_id,
        'selected_difficulty': difficulty,
        'total_count': paginator.count,
    })


@user_passes_test(is_admin_or_staff)
def admin_question_create(request):
    """Add a new question with choices."""
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            correct_letter = form.cleaned_data['correct_choice']
            
            # Save the 4 choices
            for letter in ['A', 'B', 'C', 'D']:
                low = letter.lower()
                text_rw = form.cleaned_data[f'choice_{low}']
                text_en = form.cleaned_data.get(f'choice_{low}_en', '')
                Choice.objects.create(
                    question=question,
                    letter=letter,
                    text_rw=text_rw,
                    text_en=text_en,
                    is_correct=(letter == correct_letter)
                )

            messages.success(request, f"Ikibazo #{question.question_number} cyongewemo neza! (Question added successfully!)")
            return redirect('dashboard:admin_questions')
    else:
        # Suggest next question number
        last_num = Question.objects.aggregate(Max('question_number'))['question_number__max'] or 0
        form = QuestionForm(initial={'question_number': last_num + 1})

    return render(request, 'dashboard/question_form.html', {'form': form, 'title': 'Ongeraho Ikibazo Gishyashya (Add New Question)'})


@user_passes_test(is_admin_or_staff)
def admin_question_edit(request, pk):
    """Edit an existing question and its choices."""
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            correct_letter = form.cleaned_data['correct_choice']

            for letter in ['A', 'B', 'C', 'D']:
                low = letter.lower()
                text_rw = form.cleaned_data[f'choice_{low}']
                text_en = form.cleaned_data.get(f'choice_{low}_en', '')
                Choice.objects.update_or_create(
                    question=question,
                    letter=letter,
                    defaults={
                        'text_rw': text_rw,
                        'text_en': text_en,
                        'is_correct': (letter == correct_letter)
                    }
                )

            messages.success(request, f"Ikibazo #{question.question_number} cyavuguruwe neza! (Question updated!)")
            return redirect('dashboard:admin_questions')
    else:
        form = QuestionForm(instance=question)

    return render(request, 'dashboard/question_form.html', {
        'form': form,
        'question': question,
        'title': f'Hindura Ikibazo #{question.question_number} (Edit Question)'
    })


@user_passes_test(is_admin_or_staff)
def admin_question_delete(request, pk):
    """Delete a question."""
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        q_num = question.question_number
        question.delete()
        messages.success(request, f"Ikibazo #{q_num} cyasibwe neza. (Question deleted.)")
        return redirect('dashboard:admin_questions')
    return render(request, 'dashboard/confirm_delete.html', {
        'item': f"Ikibazo #{question.question_number}: {question.question_text_rw[:80]}",
        'cancel_url': 'dashboard:admin_questions'
    })


@user_passes_test(is_admin_or_staff)
def admin_road_signs(request):
    """Road signs management view."""
    query = request.GET.get('q', '')
    sign_type = request.GET.get('type', '')

    signs = RoadSign.objects.all()
    if query:
        signs = signs.filter(
            Q(code__icontains=query) |
            Q(name_rw__icontains=query) |
            Q(name_en__icontains=query)
        )
    if sign_type:
        signs = signs.filter(sign_type=sign_type)

    paginator = Paginator(signs, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/admin_road_signs.html', {
        'page_obj': page_obj,
        'sign_types': RoadSign.SIGN_TYPES,
        'selected_type': sign_type,
        'query': query,
    })


@user_passes_test(is_admin_or_staff)
def admin_road_sign_create(request):
    """Add a new road sign."""
    if request.method == 'POST':
        form = RoadSignForm(request.POST, request.FILES)
        if form.is_valid():
            sign = form.save()
            messages.success(request, f"Icyapa [{sign.code}] cyongewemo neza! (Road sign added!)")
            return redirect('dashboard:admin_road_signs')
    else:
        form = RoadSignForm()
    return render(request, 'dashboard/road_sign_form.html', {
        'form': form,
        'title': 'Ongeraho Icyapa Gishyashya (Add New Road Sign)'
    })


@user_passes_test(is_admin_or_staff)
def admin_road_sign_edit(request, pk):
    """Edit road sign."""
    sign = get_object_or_404(RoadSign, pk=pk)
    if request.method == 'POST':
        form = RoadSignForm(request.POST, request.FILES, instance=sign)
        if form.is_valid():
            sign = form.save()
            messages.success(request, f"Icyapa [{sign.code}] cyavuguruwe neza! (Road sign updated!)")
            return redirect('dashboard:admin_road_signs')
    else:
        form = RoadSignForm(instance=sign)
    return render(request, 'dashboard/road_sign_form.html', {
        'form': form,
        'sign': sign,
        'title': f'Hindura Icyapa [{sign.code}] (Edit Road Sign)'
    })


@user_passes_test(is_admin_or_staff)
def admin_road_sign_delete(request, pk):
    """Delete a road sign."""
    sign = get_object_or_404(RoadSign, pk=pk)
    if request.method == 'POST':
        code = sign.code
        sign.delete()
        messages.success(request, f"Icyapa [{code}] cyasibwe neza. (Road sign deleted.)")
        return redirect('dashboard:admin_road_signs')
    return render(request, 'dashboard/confirm_delete.html', {
        'item': f"Icyapa [{sign.code}] {sign.name_rw}",
        'cancel_url': 'dashboard:admin_road_signs'
    })

