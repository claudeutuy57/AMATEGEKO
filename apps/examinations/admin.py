from django.contrib import admin
from .models import Question, Choice, ExamAttempt, ExamAnswer, Bookmark

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_number', 'category', 'difficulty', 'question_text_rw_short', 'is_active', 'created_at')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('question_number', 'question_text_rw', 'question_text_en', 'explanation_rw')
    inlines = [ChoiceInline]

    def question_text_rw_short(self, obj):
        return obj.question_text_rw[:80] + '...' if len(obj.question_text_rw) > 80 else obj.question_text_rw
    question_text_rw_short.short_description = "Question (Kinyarwanda)"


class ExamAnswerInline(admin.TabularInline):
    model = ExamAnswer
    extra = 0
    readonly_fields = ('question', 'selected_choice', 'is_correct', 'time_spent_seconds')
    can_delete = False


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'exam_type', 'score_display', 'is_passed', 'time_spent_seconds', 'started_at')
    list_filter = ('exam_type', 'is_passed', 'started_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('started_at', 'completed_at')
    inlines = [ExamAnswerInline]

    def score_display(self, obj):
        return f"{obj.correct_answers}/{obj.total_questions} ({obj.score_percentage}%)"
    score_display.short_description = "Score"


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'question__question_text_rw')

