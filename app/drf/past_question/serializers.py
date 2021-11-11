from django.shortcuts import get_object_or_404

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


class PastQuestionUserAnswersSerializer(ModelSerializer):
    class Meta:
        model = PastQuestionUserAnswers
        fields = "__all__"

    def validate(self, data):
        if not len(data["questions_answers"]):
            raise serializers.ValidationError({"questions_answers": "No ansers recorded"})
        for question_answer in data["questions_answers"]:
            if not all([("question_id" in  question_answer), ("your_answer" in  question_answer)]):
                raise serializers.ValidationError({"questions_answers": "question_id or/and your_answer field are required"})
        
        return data
    
    def create(self, validated_data, *args, **kwargs):
        questions_answers_array = []
        for data in validated_data["questions_answers"]:
            actual_answer = get_object_or_404(PastQuestion, pk=data["question_id"]).get_correct_answer()
            questions_answers_array.append({
                    **data,
                    "actual_answer": actual_answer,
                    "is_correct": actual_answer == data["your_answer"]
                })
        
        student = self.context["student"]
        score = len([x for x in questions_answers_array if x["is_correct"]])
        search_for = PastQuestion.objects.get(pk=validated_data["questions_answers"][0]["question_id"])
        overall_score = PastQuestion.objects.filter(category__id=search_for.category.id, subject__id=search_for.subject.id).count()
        data = self.Meta.model.objects.create(
            student=student,
            test_type=validated_data["test_type"],
            time_estimate=validated_data["time_estimate"],
            score=score,
            overall_score=overall_score,
            questions_answers=questions_answers_array
        )
        return data


