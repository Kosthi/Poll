import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# 从代码角度测试
class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """在未来时间的条件下，应返回False"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """在多于一天的条件下返回False"""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """在过去一天内的条件下返回true"""
        time = timezone.now() - datetime.timedelta(hours=1, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

# 从视图角度测试
class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """如果question不存在"""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_questions_list'], [])

    def test_past_question(self):
        """只显示过去的question"""
        question = create_question('Past Question', -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_questions_list'], [question])

    def test_future_question(self):
        """未来的问题不显示"""
        question = create_question('Future Question', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_questions_list'], [])

    def test_two_past_questions(self):
        """多个question"""
        question1 = create_question('Past question 1.', -30)
        question2 = create_question('Past question 2.', -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_questions_list'], [question2, question1])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """未来的question返回404"""
        future_question = create_question('Future question', days=5)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """过去的question显示出来"""
        past_question = create_question('Past question', days=-5)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)