from rest_framework import serializers
from phones.models import Phone

class PhoneSerializer(serializers.ModelSerializer):
    ''' Phone Serializer '''
    class Meta:
        model = Phone
        fields = '__all__'
