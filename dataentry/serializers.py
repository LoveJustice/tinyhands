from rest_framework import serializers

from dataentry.models import District, VDC, Interceptee, Person, Age, Phone, Name


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District


class VDCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDC
        exclude = ['district']


class AgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Age


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone


class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Name


class PersonSerializer(serializers.ModelSerializer):
    ages = AgeSerializer(many=True)
    phone_numbers = PhoneSerializer(many=True)
    names = NameSerializer(many=True)

    class Meta:
        model = Person


class IntercepteeSerializer(serializers.ModelSerializer):
    ages = AgeSerializer(many=True)
    phone_numbers = PhoneSerializer(many=True)
    names = NameSerializer(many=True)
    districts = DistrictSerializer(many=True)
    vdcs = VDCSerializer(many=True)

    class Meta:
        model = Interceptee
