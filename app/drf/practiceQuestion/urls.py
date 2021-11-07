from django.urls import path
from rest_framework.routers import DefaultRouter

from practiceQuestion.views import PracticeQuestionView, UsersPracticeQuestionAnswerView

router = DefaultRouter()
router.register('questions', PracticeQuestionView)
router.register('user-answers', UsersPracticeQuestionAnswerView)


app_name = 'practice_question'
urlpatterns = router.urls
