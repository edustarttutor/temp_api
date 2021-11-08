from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import *
from .serializers import *


"""
QuestionCategory
PastQuestionsAnswer
PastQuestions
PastQuestionAnswerConnector


QuestionCategorySerializer
PastQuestionsAnswerSerializer
PastQuestionSerializer
PastQuestionAnswerConnectorSerializer
"""

class QuestionCategoryApi(ModelViewSet):
    serializer_class = QuestionCategorySerializer
    queryset = QuestionCategory.objects.all()
    permission_classes = (IsAdminUser, )


class PastQuestionsApi(ModelViewSet):
    serializer_class = PastQuestionsSerializer
    queryset = PastQuestion.objects.all()
    permission_classes = (IsAdminUser, )
