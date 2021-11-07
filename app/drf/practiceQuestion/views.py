from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from practiceQuestion.models import Questions, UserAnswers
from practiceQuestion.serializer import QuestionSerializer, UserAnswersSerializer


class PracticeQuestionView(ModelViewSet):
	permission_classes = [IsAuthenticated]
	queryset = Questions.objects.all()
	serializer_class = QuestionSerializer

	def retrieve(self, request, pk):
		queryset = get_object_or_404(Questions, topic__id=pk)
		serialized_obj = self.serializer_class(instance=queryset)
		return Response(serialized_obj.data)


class UsersPracticeQuestionAnswerView(ModelViewSet):
	permission_classes = [IsAuthenticated]
	queryset = UserAnswers.objects.all()
	serializer_class = UserAnswersSerializer

	def get_queryset(self):
		queryset = UserAnswers.objects.filter(user=self.request.user)
		return queryset

	def create(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save(user=request.user)
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)


