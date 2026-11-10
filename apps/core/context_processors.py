from apps.curriculum.models import Category, RoadSign
from apps.examinations.models import Question

def global_context(request):
    """Provides common data to all templates."""
    return {
        'site_categories': Category.objects.all().order_by('order'),
        'total_questions_count': Question.objects.filter(is_active=True).count(),
        'total_road_signs_count': RoadSign.objects.count(),
        'official_exam_questions': 20,
        'official_exam_duration': 20,
        'official_exam_pass_mark': 12,
    }

