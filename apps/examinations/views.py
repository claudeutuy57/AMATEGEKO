import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.conf import settings
from .models import Question, Choice, ExamAttempt, ExamAnswer, Bookmark
from apps.curriculum.models import Category

def practice_list_view(request):
    """Practice overview: select category or start full mixed practice."""
    categories = Category.objects.annotate(
        total_q=Count('questions', filter=Q(questions__is_active=True))
    ).filter(total_q__gt=0).order_by('order')

    total_questions = Question.objects.filter(is_active=True).count()
    user_bookmarks_count = 0
    if request.user.is_authenticated:
        user_bookmarks_count = Bookmark.objects.filter(user=request.user).count()

    context = {
        'categories': categories,
        'total_questions': total_questions,
        'user_bookmarks_count': user_bookmarks_count,
    }
    return render(request, 'examinations/practice_list.html', context)


def practice_view(request):
    """
    Interactive practice mode: displays one question at a time,
    allows instant answer checking, explanation display, and bookmarking.
    """
    category_slug = request.GET.get('category', '')
    only_bookmarks = request.GET.get('bookmarks', '') == 'true'
    difficulty = request.GET.get('difficulty', '')

    questions = Question.objects.filter(is_active=True).select_related('category', 'road_sign').prefetch_related('choices')

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        questions = questions.filter(category=selected_category)

    if only_bookmarks and request.user.is_authenticated:
        bookmarked_ids = Bookmark.objects.filter(user=request.user).values_list('question_id', flat=True)
        questions = questions.filter(id__in=bookmarked_ids)

    if difficulty in ['EASY', 'MEDIUM', 'HARD']:
        questions = questions.filter(difficulty=difficulty)

    total_count = questions.count()
    if total_count == 0:
        messages.warning(request, "Nta bibazo bibonetse muri iki cyiciro. (No questions found in this filter.)")
        return redirect('examinations:practice_list')

    # Page/index through questions
    try:
        current_index = int(request.GET.get('page', 1))
    except ValueError:
        current_index = 1

    if current_index < 1:
        current_index = 1
    elif current_index > total_count:
        current_index = total_count

    question = questions[current_index - 1]

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, question=question).exists()

    context = {
        'question': question,
        'choices': question.choices.all(),
        'current_index': current_index,
        'total_count': total_count,
        'progress_pct': round((current_index / total_count) * 100),
        'selected_category': selected_category,
        'has_prev': current_index > 1,
        'prev_page': current_index - 1,
        'has_next': current_index < total_count,
        'next_page': current_index + 1,
        'is_bookmarked': is_bookmarked,
        'only_bookmarks': only_bookmarks,
        'difficulty': difficulty,
    }
    return render(request, 'examinations/practice.html', context)


def custom_exam_builder_view(request):
    """
    Kora Ikizamini Cyawe (Make Custom Exam):
    Allows students to configure their own custom examination.
    """
    categories = Category.objects.all().order_by('order')
    total_active_q = Question.objects.filter(is_active=True).count()
    return render(request, 'examinations/custom_exam_builder.html', {
        'categories': categories,
        'total_active_q': total_active_q
    })


def custom_exam_take_view(request):
    """
    Takes parameters from GET/POST and starts a customized live examination
    with a balanced mix of road signs/images and text-based traffic rules.
    """
    cat_id = request.GET.get('category', '')
    q_count = int(request.GET.get('count', 20))
    duration_min = int(request.GET.get('duration', q_count)) # default 1 min per question
    difficulty = request.GET.get('difficulty', '')

    questions = get_mixed_exam_questions(
        total_count=q_count,
        cat_id=cat_id if cat_id else None,
        difficulty=difficulty if difficulty else None
    )

    questions_data = []
    for idx, q in enumerate(questions, 1):
        choices_data = []
        for c in q.choices.all():
            choices_data.append({
                'id': c.id,
                'letter': c.letter,
                'text_rw': c.text_rw,
                'text_en': c.text_en
            })
        
        sign_info = None
        if q.road_sign:
            sign_info = {
                'code': q.road_sign.code,
                'name_rw': q.road_sign.name_rw,
                'svg_content': q.road_sign.svg_content,
            }

        image_url = q.image.url if q.image else None

        questions_data.append({
            'index': idx,
            'id': q.id,
            'number': q.question_number,
            'text_rw': q.question_text_rw,
            'text_en': q.question_text_en,
            'category': q.category.name_rw,
            'road_sign': sign_info,
            'image_url': image_url,
            'choices': choices_data,
        })

    pass_mark = round(len(questions_data) * 0.6)

    context = {
        'questions_json': json.dumps(questions_data),
        'total_questions': len(questions_data),
        'duration_seconds': duration_min * 60,
        'pass_mark': pass_mark,
        'is_custom': True,
    }
    return render(request, 'examinations/mock_exam.html', context)


def mock_exam_start(request):
    """Official Examination instructions page."""
    total_q = settings.RWANDA_EXAM_TOTAL_QUESTIONS
    duration = settings.RWANDA_EXAM_DURATION_MINUTES
    pass_mark = settings.RWANDA_EXAM_PASS_MARK

    return render(request, 'examinations/mock_exam_start.html', {
        'total_questions': total_q,
        'duration_minutes': duration,
        'pass_mark': pass_mark,
        'pass_percentage': round((pass_mark / total_q) * 100)
    })


def get_mixed_exam_questions(total_count=20, cat_id=None, difficulty=None):
    """
    Selects a balanced mix of road signs/images and text-based traffic rule questions.
    Typical ratio: ~45% visual/signs, ~55% text/words.
    """
    base_qs = Question.objects.filter(is_active=True).select_related('category', 'road_sign').prefetch_related('choices')
    if cat_id:
        base_qs = base_qs.filter(category_id=cat_id)
    if difficulty in ['EASY', 'MEDIUM', 'HARD']:
        base_qs = base_qs.filter(difficulty=difficulty)

    # 1. Sign / visual questions (has road_sign or image)
    sign_qs = base_qs.filter(
        Q(road_sign__isnull=False) | (Q(image__isnull=False) & ~Q(image=''))
    )

    # 2. Text / word questions (no road_sign and no image)
    word_qs = base_qs.filter(
        road_sign__isnull=True,
        image__in=['', None]
    )

    desired_signs = max(1, round(total_count * 0.45)) # ~9 for 20 questions
    desired_words = total_count - desired_signs       # ~11 for 20 questions

    signs_list = list(sign_qs.order_by('?')[:desired_signs])
    words_list = list(word_qs.order_by('?')[:desired_words])

    # If not enough in one pool, top up from the other
    if len(signs_list) < desired_signs:
        needed = desired_signs - len(signs_list)
        extra_words = list(word_qs.exclude(id__in=[q.id for q in words_list]).order_by('?')[:needed])
        words_list.extend(extra_words)

    if len(words_list) < desired_words:
        needed = desired_words - len(words_list)
        extra_signs = list(sign_qs.exclude(id__in=[q.id for q in signs_list]).order_by('?')[:needed])
        signs_list.extend(extra_signs)

    combined = signs_list + words_list
    import random
    random.shuffle(combined)
    return combined[:total_count]


def mock_exam_view(request):
    """
    Renders the live 20-question mock official exam with a balanced mix
    of road signs/images and text-based traffic rules questions.
    """
    total_questions = settings.RWANDA_EXAM_TOTAL_QUESTIONS
    questions = get_mixed_exam_questions(total_count=total_questions)

    # Structure questions for frontend
    questions_data = []
    for idx, q in enumerate(questions, 1):
        choices_data = []
        for c in q.choices.all():
            choices_data.append({
                'id': c.id,
                'letter': c.letter,
                'text_rw': c.text_rw,
                'text_en': c.text_en
            })
        
        sign_info = None
        if q.road_sign:
            sign_info = {
                'code': q.road_sign.code,
                'name_rw': q.road_sign.name_rw,
                'svg_content': q.road_sign.svg_content,
            }

        image_url = q.image.url if q.image else None

        questions_data.append({
            'index': idx,
            'id': q.id,
            'number': q.question_number,
            'text_rw': q.question_text_rw,
            'text_en': q.question_text_en,
            'category': q.category.name_rw,
            'road_sign': sign_info,
            'image_url': image_url,
            'choices': choices_data,
        })

    context = {
        'questions_json': json.dumps(questions_data),
        'total_questions': len(questions_data),
        'duration_seconds': settings.RWANDA_EXAM_DURATION_MINUTES * 60,
        'pass_mark': settings.RWANDA_EXAM_PASS_MARK,
    }
    return render(request, 'examinations/mock_exam.html', context)


def mock_exam_submit(request):
    """
    Handles submission of the mock examination, calculates score,
    records results, and returns redirect or JSON.
    """
    if request.method != 'POST':
        return redirect('examinations:mock_exam_start')

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        # Form POST fallback
        payload = request.POST

    answers_dict = payload.get('answers', {})
    time_spent = int(payload.get('time_spent', 0))

    # Create ExamAttempt
    user = request.user if request.user.is_authenticated else None
    attempt = ExamAttempt.objects.create(
        user=user,
        exam_type='OFFICIAL_MOCK',
        total_questions=len(answers_dict) if answers_dict else settings.RWANDA_EXAM_TOTAL_QUESTIONS,
        time_spent_seconds=time_spent,
        completed_at=timezone.now()
    )

    correct_count = 0
    for q_id_str, choice_id in answers_dict.items():
        try:
            q_id = int(q_id_str)
            question = Question.objects.get(id=q_id)
            selected_choice = Choice.objects.filter(id=choice_id, question=question).first() if choice_id else None
            is_correct = selected_choice.is_correct if selected_choice else False
            
            if is_correct:
                correct_count += 1

            ExamAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice,
                is_correct=is_correct,
            )
        except (ValueError, Question.DoesNotExist):
            continue

    attempt.correct_answers = correct_count
    attempt.total_questions = max(len(answers_dict), settings.RWANDA_EXAM_TOTAL_QUESTIONS)
    attempt.calculate_result(pass_mark=settings.RWANDA_EXAM_PASS_MARK)
    attempt.save()

    return JsonResponse({
        'status': 'success',
        'attempt_id': attempt.id,
        'redirect_url': f'/examinations/result/{attempt.id}/'
    })


def exam_result_view(request, attempt_id):
    """Displays official exam results with PASS or FAIL badge and score statistics."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    
    # Category performance
    answers = attempt.answers.select_related('question__category', 'selected_choice', 'question')
    category_stats = {}
    for a in answers:
        cat_name = a.question.category.name_rw
        if cat_name not in category_stats:
            category_stats[cat_name] = {'total': 0, 'correct': 0}
        category_stats[cat_name]['total'] += 1
        if a.is_correct:
            category_stats[cat_name]['correct'] += 1

    for cat, data in category_stats.items():
        data['percentage'] = round((data['correct'] / data['total']) * 100) if data['total'] > 0 else 0

    minutes = attempt.time_spent_seconds // 60
    seconds = attempt.time_spent_seconds % 60
    formatted_time = f"{minutes:02d}:{seconds:02d}"

    context = {
        'attempt': attempt,
        'category_stats': category_stats,
        'formatted_time': formatted_time,
        'pass_mark': settings.RWANDA_EXAM_PASS_MARK,
        'wrong_count': attempt.total_questions - attempt.correct_answers,
    }
    return render(request, 'examinations/exam_result.html', context)


def exam_review_view(request, attempt_id):
    """Allows student to review every question, chosen answer, correct answer, and explanation."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    filter_type = request.GET.get('filter', 'all')  # all, wrong, correct

    answers = attempt.answers.select_related(
        'question__category', 'question__road_sign', 'selected_choice'
    ).prefetch_related('question__choices').all()

    if filter_type == 'wrong':
        answers = answers.filter(is_correct=False)
    elif filter_type == 'correct':
        answers = answers.filter(is_correct=True)

    context = {
        'attempt': attempt,
        'answers': answers,
        'filter_type': filter_type,
        'total_wrong': attempt.answers.filter(is_correct=False).count(),
        'total_correct': attempt.answers.filter(is_correct=True).count(),
    }
    return render(request, 'examinations/exam_review.html', context)


def exam_certificate_view(request, attempt_id):
    """Printable official readiness certificate for students who passed."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    if not attempt.is_passed:
        messages.warning(request, "Icyemezo gitangwa gusa ku batsinze ikizamini (Amanota >= 12/20).")
        return redirect('examinations:exam_result', attempt_id=attempt.id)

    cert_serial = f"RNP-MOCK-2026-{attempt.id:06d}"
    candidate_name = attempt.user.display_name if attempt.user else "Umunyeshuri (Candidate)"

    return render(request, 'examinations/exam_certificate.html', {
        'attempt': attempt,
        'cert_serial': cert_serial,
        'candidate_name': candidate_name,
    })


@login_required
def toggle_bookmark_api(request, question_id):
    """Toggle bookmark on a question for the authenticated student."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    question = get_object_or_404(Question, id=question_id)
    bookmark = Bookmark.objects.filter(user=request.user, question=question).first()

    if bookmark:
        bookmark.delete()
        is_bookmarked = False
        msg = "Ikibazo cyakuwe mu byo wazirikanye. (Removed from bookmarks)"
    else:
        Bookmark.objects.create(user=request.user, question=question)
        is_bookmarked = True
        msg = "Ikibazo cyashyizwe mu byo wazirikanye. (Added to bookmarks)"

    return JsonResponse({
        'status': 'success',
        'is_bookmarked': is_bookmarked,
        'message': msg,
        'total_bookmarks': Bookmark.objects.filter(user=request.user).count()
    })

