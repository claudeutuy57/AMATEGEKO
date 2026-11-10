from django.contrib import admin
from .models import Category, RoadSign, Lesson

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'name_rw', 'name_en', 'slug')
    list_display_links = ('name_rw',)
    list_editable = ('order',)
    search_fields = ('name_rw', 'name_en')
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(RoadSign)
class RoadSignAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_rw', 'name_en', 'sign_type', 'order')
    list_filter = ('sign_type',)
    search_fields = ('code', 'name_rw', 'name_en', 'meaning_rw', 'meaning_en')
    list_editable = ('order',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title_rw', 'category', 'order', 'estimated_read_time', 'created_at')
    list_filter = ('category',)
    search_fields = ('title_rw', 'title_en', 'content_rw')
    prepopulated_fields = {'slug': ('title_en',)}
