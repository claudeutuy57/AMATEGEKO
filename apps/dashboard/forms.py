from django import forms
from apps.examinations.models import Question, Choice
from apps.curriculum.models import RoadSign, Category

class QuestionForm(forms.ModelForm):
    # Form fields for the 4 choices
    choice_a = forms.CharField(label="Igisubizo A (Answer A - Kinyarwanda)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    choice_a_en = forms.CharField(label="Answer A (English)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    choice_b = forms.CharField(label="Igisubizo B (Answer B - Kinyarwanda)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    choice_b_en = forms.CharField(label="Answer B (English)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    choice_c = forms.CharField(label="Igisubizo C (Answer C - Kinyarwanda)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    choice_c_en = forms.CharField(label="Answer C (English)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    choice_d = forms.CharField(label="Igisubizo D (Answer D - Kinyarwanda)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    choice_d_en = forms.CharField(label="Answer D (English)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    correct_choice = forms.ChoiceField(
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        label="Igisubizo Nyacyo (Correct Answer Letter)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Question
        fields = [
            'question_number', 'category', 'difficulty', 'road_sign',
            'question_text_rw', 'question_text_en', 'explanation_rw',
            'explanation_en', 'legal_reference', 'is_active'
        ]
        widgets = {
            'question_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'road_sign': forms.Select(attrs={'class': 'form-select'}),
            'question_text_rw': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_text_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'explanation_rw': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'explanation_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'legal_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            choices = self.instance.choices.all()
            for c in choices:
                letter = c.letter.lower()
                if letter in ['a', 'b', 'c', 'd']:
                    self.fields[f'choice_{letter}'].initial = c.text_rw
                    self.fields[f'choice_{letter}_en'].initial = c.text_en
                    if c.is_correct:
                        self.fields['correct_choice'].initial = c.letter


class RoadSignForm(forms.ModelForm):
    class Meta:
        model = RoadSign
        fields = [
            'code', 'sign_type', 'name_rw', 'name_en', 'meaning_rw',
            'meaning_en', 'explanation_rw', 'explanation_en',
            'legal_reference', 'svg_content', 'image', 'order'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'sign_type': forms.Select(attrs={'class': 'form-select'}),
            'name_rw': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'meaning_rw': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'meaning_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'explanation_rw': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'explanation_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'legal_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'svg_content': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

