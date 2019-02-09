from rest_framework import serializers
from phones.models import Phone, Company

class PhoneSerializer(serializers.ModelSerializer):
    ''' Phone Serializer '''
    manufacturer = serializers.ReadOnlyField(source='manufacturer.name')

    class Meta:
        model = Phone
        fields = ['id', 'model', 'image', 'manufacturer', 'price', \
                  'description', 'specs', 'stock']