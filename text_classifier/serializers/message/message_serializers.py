from rest_framework import serializers
from text_classifier.models import Message
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'text', 'toxic_tag', 'created_at', 'updated_at']
        read_only_fields = ['id', 'toxic_tag', 'created_at', 'updated_at', 'sender']

    def validate_receiver(self, value):
        """Receiver is passed as user ID, convert to User object"""
        if isinstance(value, int) or isinstance(value, str):
            try:
                user = User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Receiver does not exist")
            return user
        elif isinstance(value, User):
            return value
        raise serializers.ValidationError("Invalid receiver")

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message text cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Message text is too long (max 1000 characters)")
        return value
