from rest_framework.routers import DefaultRouter

from .api import *


"""
QuestionCategoryApi
PastQuestionsApi
"""
app_name = "past_question"

router = DefaultRouter()
router.register("category", QuestionCategoryApi)
router.register("", PastQuestionsApi)


urlpatterns = router.urls
