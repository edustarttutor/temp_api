from django.contrib import admin

from .models import *

# Register your models here.


"""
QuestionCategory
PastQuestionsAnswer
PastQuestions
PastQuestionAnswerConnector
"""
@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ("category",)


@admin.register(PastQuestionsAnswer)
class PastQuestionsAnswerAdmin(admin.ModelAdmin):
    list_display = ("text", "is_answer")


@admin.register(PastQuestion)
class PastQuestionsAdmin(admin.ModelAdmin):
    list_display = ("category", "subject", "question")


@admin.register(PastQuestionAnswerConnector)
class PastQuestionAnswerConnectorAdmin(admin.ModelAdmin):
    list_display = ("question", "answer")
