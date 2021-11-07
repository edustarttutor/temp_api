from rest_framework.serializers import ModelSerializer

from practiceQuestion.models import Questions, UserAnswers


class QuestionSerializer(ModelSerializer):
	class Meta:
		model = Questions
		fields = '__all__'


class UserAnswersSerializer(ModelSerializer):
	class Meta:
		model = UserAnswers
		fields = '__all__'
		read_only_fields = ['user']
