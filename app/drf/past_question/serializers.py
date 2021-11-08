from rest_framework.serializers import ModelSerializer

from .models import *


class QuestionCategorySerializer(ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = "__all__"


class PastQuestionAnswerSerializer(ModelSerializer):
    class Meta:
        model = PastQuestionsAnswer
        fields = "__all__"

class PastQuestionsSerializer(ModelSerializer):
    answers = PastQuestionAnswerSerializer(many=True)
    class Meta:
        model = PastQuestion
        fields = "__all__"

    def create(self, validated_data):
        answers = validated_data.pop("answers")
        question = self.Meta.model.objects.create(**validated_data)
        for answer in answers:
            answer = PastQuestionsAnswer.objects.create(**answer)
            answer_question_connect = PastQuestionAnswerConnector.objects.create(question=question, answer=answer)
        return question
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["subject_name"] = instance.subject.name
        data["category_name"] = instance.category.category
        return data
