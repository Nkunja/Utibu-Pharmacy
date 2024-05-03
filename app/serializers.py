from rest_framework import serializers
from .models import  UserProfile, Medication, Order, Invoice, Payment
from django.conf import settings
import base64



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        return data


class MedicationSerializer(serializers.ModelSerializer):
    image_data = serializers.SerializerMethodField()

    class Meta:
        model = Medication
        fields = ['id', 'name', 'description', 'price', 'quantity_available', 'category', 'image_data']

    def get_image_data(self, obj):
        if obj.image_url:
            return obj.image_url
        return None

    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):    
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserProfile.objects.create_user(password=password, **validated_data)
        return user
    
class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        validated_data['role'] = 'patient'  
        user = UserProfile.objects.create_user(**validated_data)
        return user


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['title', 'image', 'cta']