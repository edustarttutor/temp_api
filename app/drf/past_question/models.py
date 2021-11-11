from django.db import models

from subject_related.models import Subject
from accounts.models import User


TEST_TYPES = [("obj", "obj"), ("theory", "theory"), ("alternative-theory", "alternative-theory")]


class QuestionCategory(models.Model):
    category = models.CharField(max_length=250, help_text="e.g Waec, Neco, GCE")

    def __str__(self):
        return self.category
    


class PastQuestionsAnswer(models.Model):
    text = models.CharField(max_length=250)
    is_answer = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class PastQuestion(models.Model):
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    answers = models.ManyToManyField(PastQuestionsAnswer, through="PastQuestionAnswerConnector", through_fields=("question", "answer"))
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"({self.category}) - ({self.subject}) - {self.question}"

    def get_correct_answer(self):
        return self.answers.filter(is_answer=True).first().pk


class PastQuestionAnswerConnector(models.Model):
    question = models.ForeignKey(PastQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(PastQuestionsAnswer, on_delete=models.CASCADE)

    def __str__(self):
        return f"({self.answer}) - {self.question}"


class PastQuestionUserAnswers(models.Model):
    """
    "student_id": 1,
        "test_taken_on": "2021-11-09",
        "time_estimate": "50:00",
        "score": "2",
        "test_type":"obj",
        "overall_score": "3",
        "questions_answers": [
            {"question_id": 1, "is_correct": true, "your_answer": 1, "actual_answer": 1},
            {"question_id": 2, "is_correct": false, "your_answer": 2, "actual_answer": 3},
            {"question_id": 3, "is_correct": true, "your_answer": 2, "actual_answer": 2},
        ]
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test_taken_on = models.DateField(auto_now_add=True)
    test_type = models.CharField(max_length=250, choices=TEST_TYPES)
    time_estimate = models.TimeField()
    score = models.IntegerField(blank=True, null=True, default=0)
    overall_score = models.IntegerField(blank=True, null=True)
    questions_answers = models.JSONField()

    def __str__(self):
        return f"({self.student}) - {self.score}"


