from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from text_classifier.models import Message
from text_classifier.serializers.message.message_serializers import MessageSerializer
from text_classifier.machine_learning.predict import predict_new_text
from utils.decorators import jwt_required
from utils.response import api_response


class MessageCreateAPIView(APIView):
    authentication_classes = []
    
    @jwt_required
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            predictions = predict_new_text(serializer.validated_data['text'])
            toxic_tag = (
                'toxic' if predictions.get('toxic') == 'Yes' or predictions.get('severe_toxic') == 'Yes'
                else 'insult' if predictions.get('insult') == 'Yes'
                else 'threat' if predictions.get('threat') == 'Yes'
                else 'identity_hate' if predictions.get('identity_hate') == 'Yes'
                else 'none'
            )
            message = serializer.save(sender=request.user, toxic_tag=toxic_tag)

            response_serializer = MessageSerializer(message)
            return api_response(
                status_code=201,
                status='success',
                message='Message sent successfully',
                data=response_serializer.data
            )

        errors = {k: v[0] for k, v in serializer.errors.items()}
        return api_response(
            status_code=400,
            status='fail',
            message='Invalid data',
            data=errors
        )


class MessageListAPIView(APIView):
    authentication_classes = []

    @jwt_required
    def get(self, request):
        receiver_id = request.query_params.get('receiver_id')

        if receiver_id:
            messages = Message.objects.filter(
                (Q(sender=request.user) & Q(receiver__id=receiver_id)) |
                (Q(sender__id=receiver_id) & Q(receiver=request.user))
            ).order_by('-created_at')
        else:
            messages = Message.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user)
            ).order_by('-created_at')

        serializer = MessageSerializer(messages, many=True)
        return api_response(
            status_code=status.HTTP_200_OK,
            status='success',
            message='Messages retrieved',
            data=serializer.data
        )



class MessageDetailAPIView(APIView):
    authentication_classes = []
    def get_object(self, pk, user):
        try:
            return Message.objects.get(Q(id=pk) & (Q(sender=user) | Q(receiver=user)))
        except Message.DoesNotExist:
            return None

    @jwt_required
    def get(self, request, pk):
        message = self.get_object(pk, request.user)
        if not message:
            return api_response(status_code=404, status='fail', message='Message not found')

        serializer = MessageSerializer(message)
        return api_response(
            status_code=200,
            status='success',
            message='Message retrieved',
            data=serializer.data
        )

    @jwt_required
    def delete(self, request, pk):
        message = self.get_object(pk, request.user)
        if not message:
            return api_response(status_code=404, status='fail', message='Message not found')
        message.delete()
        return api_response(status_code=200, status='success', message='Message deleted')
