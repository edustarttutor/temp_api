from django.db import models

from subject_related.models import Subject

# Create your models here.


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


class PastQuestionAnswerConnector(models.Model):
    question = models.ForeignKey(PastQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(PastQuestionsAnswer, on_delete=models.CASCADE)

    def __str__(self):
        return f"({self.answer}) - {self.question}"
