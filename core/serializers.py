import random
import string
from builtins import len

from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import serializers
from django.conf import settings
from .models import (User, Item, Profile, Category, OrderItem, Order, Payment)


def update_code():
    update_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    try:
        id_exist = Order.objects.get(update_code=update_id)
        if id_exist.exits():
            update_code()
    except:
        return update_id


def generate_code():
    ref_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=30))
    try:
        id_exist = Order.objects.get(ref_code=ref_id)
        if id_exist.exits():
            generate_code()
    except:
        return ref_id


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=224, min_length=4, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User(
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance



class ProfileSerializer(serializers.ModelSerializer):
    address =  serializers.CharField(required=True)
    phone =  serializers.CharField(required=True)
    id = serializers.IntegerField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(required=True)

    class Meta:
        model = Profile
        fields = ['id',
                  'email',
                  'phone',
                  'full_name',
                  'address']

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.full_name = validated_data['full_name']
        instance.address = validated_data['address']
        instance.phone = validated_data['phone']

        instance.save()

        return instance

    def get_email(self, obj):
        return obj.user.email

    def get_id(self, obj):
        return obj.user.id

class OrederdUserSerializer(serializers.ModelSerializer):
    address =  serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField()
    full_name = serializers.CharField(required=True)

    class Meta:
        model = Profile
        fields = [
            'email',
            'phone',
            'full_name',
            'address']


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField(read_only=True)
    picture = serializers.SerializerMethodField('get_picture')

    class Meta:
        model = Item
        fields = ['id', 'title', 'price', 'discount_price', 'category', 'description', 'picture']

    def get_category(self, obj):
        return obj.category.choice

    def get_picture(self, obj):
        request = self.context.get('request')
        photo_url = obj.picture.url
        return request.build_absolute_uri(photo_url)


class AllCAtSerializer(serializers.ModelSerializer):
    choice = serializers.CharField(required=False)
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Category
        fields = ['id', 'choice']


class OrderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)

class CartSerializer(serializers.ModelSerializer):
    item = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['item']

class paymentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    tx_ref = serializers.CharField(required=True)
    flw_ref = serializers.CharField(required=True)
    tansaction_id = serializers.IntegerField(required=True)

    class Meta:
        model = Payment
        fields = ['tansaction_id', 'flw_ref', 'tx_ref', 'amount', 'status']


class OrerdSerializer(serializers.Serializer):
    user = OrederdUserSerializer()
    cart = CartSerializer()
    payment = paymentSerializer()

    def create(self, validated_data):
        user = self.context['request'].user
        user_profile = validated_data.get('user', )
        payment_data = validated_data.get('payment')
        cart_data = validated_data.pop('cart')
        if payment_data['status'] == "successful":
            payment = Payment.objects.create(user=user, **payment_data)
            order = Order.objects.create(user=user, payment=payment, ordered=True,
                                         billing_address=user.profile.address,
                                         ref_code=generate_code())
            for single_item in cart_data['item']:
                item = get_object_or_404(Item, id=single_item['id'])
                incart, created = OrderItem.objects.get_or_create(user=user, item=item,
                                                                  quantity=single_item['quantity'],
                                                                  ordered=False)
                order.cart.add(incart)
            order_items = order.cart.all()
            total = order.cart.count()
            order.total = total
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            order.ordered = True
            order.save()
            return order
        raise serializers.ValidationError({"your payment was not successful"})



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['amount', 'status']


class OrderItemSummarySerializer(serializers.Serializer):
    item = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'item']

    def get_item(self, obj):
        return obj.item.title

    def get_quantity(self, obj):
        return obj.quantity


class OrderedQuerySerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    cart = OrderItemSummarySerializer(many=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ['phone', 'full_name', 'packaged', 'received', 'ordered_date', 'ref_code',
                   'cart', 'billing_address', 'payment']

    def get_full_name(self, obj):
        return obj.user.profile.full_name

    def get_phone(self, obj):
        return obj.user.profile.phone
