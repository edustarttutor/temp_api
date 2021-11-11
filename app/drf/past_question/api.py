from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import *
from .serializers import *
from .permissions import *




class QuestionCategoryApi(ModelViewSet):
    serializer_class = QuestionCategorySerializer
    queryset = QuestionCategory.objects.all()
    permission_classes = (IsAdminUser, )


class PastQuestionsApi(ModelViewSet):
    serializer_class = PastQuestionsSerializer
    queryset = PastQuestion.objects.all()
    permission_classes = (IsAuthenticated, LimitedPermission)

    def get_queryset(self):
        data = self.queryset
        if "category" in self.request.query_params:
            data = data.filter(category__pk=self.request.query_params["category"])
        return data



class PastQuestionUserAnswersApi(ModelViewSet):
    serializer_class = PastQuestionUserAnswersSerializer
    queryset = PastQuestionUserAnswers.objects.all()
    permission_classes = (IsAuthenticated, LimitedPermission)

    def get_queryset(self):
        data = self.queryset
        if not self.request.user.is_superuser:
            data = data.filter(student=self.request.user)
        return data

    
    def create(self, request, *args, **kwargs):
        """Endpoint to take a past question test
        sample request:
            {
                "student": 32,
                "time_estimate": "05:00",
                "test_type": "obj",
                "questions_answers": [
                    {"question_id": 2, "your_answer": 5},
                    {"question_id": 3, "your_answer": 10}
                ]
            }

        sample response:
            {
                "id": 2,
                "test_taken_on": "2021-11-09",
                "test_type": "obj",
                "time_estimate": "05:00:00",
                "score": 1,
                "overall_score": 2,
                "questions_answers": [
                    {
                        "question_id": 2,
                        "your_answer": 5,
                        "actual_answer": 6,
                        "is_correct": false
                    },
                    {
                        "question_id": 3,
                        "your_answer": 10,
                        "actual_answer": 10,
                        "is_correct": true
                    }
                ],
                "student": 32
            }
        """
        serializer = self.serializer_class(data=request.data, context={"student": request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=202)



