from rest_framework import serializers
from phones.models import Phone, Company

class PhoneListSerializer(serializers.ModelSerializer):
    ''' Phone Serializer - list view '''

    class Meta:
        model = Phone
        fields = ['model', 'image', 'price']


class PhoneDetailSerializer(serializers.ModelSerializer):
    ''' Phone Serializer - detail view '''
    manufacturer = serializers.ReadOnlyField(source='manufacturer.name')

    class Meta:
        model = Phone
        fields = '__all__'      
        