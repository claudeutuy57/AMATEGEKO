from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.curriculum.models import Category, RoadSign
from apps.examinations.models import Question, Choice, ExamAttempt, ExamAnswer, Bookmark
import json

class ExaminationSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='teststudent',
            password='Password123!',
            email='test@amategeko.rw',
            role='LEARNER'
        )
        self.category = Category.objects.create(
            name_rw="Ibyapa byo mu muhanda",
            name_en="Road Traffic Signs",
            order=1
        )
        self.sign = RoadSign.objects.create(
            sign_type='WARNING',
            code='A1_TEST',
            name_rw="Ikoni ry'iburyo",
            name_en="Right curve",
            meaning_rw="Ibisobanuro by'ikoni",
            meaning_en="Curve meaning",
            order=1
        )
        self.question = Question.objects.create(
            category=self.category,
            question_number=999,
            question_text_rw="Iki cyapa gisobanura iki?",
            question_text_en="What does this sign mean?",
            difficulty='EASY',
            road_sign=self.sign,
            explanation_rw="Ibisobanuro nyabyo",
            explanation_en="Accurate explanation",
            legal_reference="Iteka rya Perezida N° 85/01 Ingingo ya 8"
        )
        self.choice_a = Choice.objects.create(
            question=self.question,
            letter='A',
            text_rw="Ikoni ry'iburyo",
            text_en="Right curve",
            is_correct=True
        )
        self.choice_b = Choice.objects.create(
            question=self.question,
            letter='B',
            text_rw="Ikoni ry'ibumoso",
            text_en="Left curve",
            is_correct=False
        )

    def test_question_choices_relationship(self):
        self.assertEqual(self.question.choices.count(), 2)
        self.assertEqual(self.question.correct_choice, self.choice_a)

    def test_exam_attempt_scoring_pass(self):
        attempt = ExamAttempt.objects.create(
            user=self.user,
            exam_type='OFFICIAL_MOCK',
            total_questions=20,
            correct_answers=14
        )
        is_passed = attempt.calculate_result(pass_mark=12)
        self.assertTrue(is_passed)
        self.assertTrue(attempt.is_passed)
        self.assertEqual(attempt.score_percentage, 70.0)

    def test_exam_attempt_scoring_fail(self):
        attempt = ExamAttempt.objects.create(
            user=self.user,
            exam_type='OFFICIAL_MOCK',
            total_questions=20,
            correct_answers=10
        )
        is_passed = attempt.calculate_result(pass_mark=12)
        self.assertFalse(is_passed)
        self.assertFalse(attempt.is_passed)
        self.assertEqual(attempt.score_percentage, 50.0)

    def test_mock_exam_submit_endpoint(self):
        self.client.login(username='teststudent', password='Password123!')
        payload = {
            'answers': {
                str(self.question.id): self.choice_a.id
            },
            'time_spent': 120
        }
        response = self.client.post(
            reverse('examinations:mock_exam_submit'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('attempt_id', data)

        attempt = ExamAttempt.objects.get(id=data['attempt_id'])
        self.assertEqual(attempt.user, self.user)
        self.assertEqual(attempt.correct_answers, 1)

    def test_bookmark_toggle_api(self):
        self.client.login(username='teststudent', password='Password123!')
        
        # Toggle ON
        res = self.client.post(reverse('examinations:toggle_bookmark', kwargs={'question_id': self.question.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['is_bookmarked'])
        self.assertTrue(Bookmark.objects.filter(user=self.user, question=self.question).exists())

        # Toggle OFF
        res2 = self.client.post(reverse('examinations:toggle_bookmark', kwargs={'question_id': self.question.id}))
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()['is_bookmarked'])
        self.assertFalse(Bookmark.objects.filter(user=self.user, question=self.question).exists())

