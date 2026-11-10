from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, RoadSign, Lesson

def road_signs_view(request):
    """Visual library of Rwandan road signs with filtering by type and search."""
    sign_type = request.GET.get('type', '')
    query = request.GET.get('q', '')

    signs = RoadSign.objects.all()

    if sign_type:
        signs = signs.filter(sign_type=sign_type)

    if query:
        signs = signs.filter(
            Q(name_rw__icontains=query) |
            Q(name_en__icontains=query) |
            Q(code__icontains=query) |
            Q(meaning_rw__icontains=query) |
            Q(meaning_en__icontains=query)
        )

    categories = RoadSign.SIGN_TYPES

    context = {
        'signs': signs,
        'categories': categories,
        'selected_type': sign_type,
        'query': query,
        'total_signs': RoadSign.objects.count(),
    }
    return render(request, 'curriculum/road_signs.html', context)


def road_sign_detail_view(request, code):
    """Detailed view for a single road sign."""
    sign = get_object_or_404(RoadSign, code__iexact=code)
    related_signs = RoadSign.objects.filter(sign_type=sign.sign_type).exclude(id=sign.id)[:4]
    return render(request, 'curriculum/road_sign_detail.html', {
        'sign': sign,
        'related_signs': related_signs
    })


def traffic_rules_view(request):
    """List of all traffic rules and syllabus modules."""
    categories = Category.objects.prefetch_related('lessons').all()
    total_lessons = Lesson.objects.count()
    return render(request, 'curriculum/traffic_rules.html', {
        'categories': categories,
        'total_lessons': total_lessons
    })


def lesson_detail_view(request, slug):
    """Display individual lesson with structured learning content."""
    lesson = get_object_or_404(Lesson, slug=slug)
    category_lessons = Lesson.objects.filter(category=lesson.category).order_by('order')
    
    # Next and previous lessons
    lessons_list = list(category_lessons)
    current_idx = lessons_list.index(lesson) if lesson in lessons_list else -1
    prev_lesson = lessons_list[current_idx - 1] if current_idx > 0 else None
    next_lesson = lessons_list[current_idx + 1] if current_idx < len(lessons_list) - 1 else None

    return render(request, 'curriculum/lesson_detail.html', {
        'lesson': lesson,
        'category_lessons': category_lessons,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson
    })

