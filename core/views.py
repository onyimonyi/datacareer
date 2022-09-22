from django.http import Http404
from django.shortcuts import render

# Create your views here.

from rest_framework import filters
from rest_framework.views import APIView
import json
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from rest_framework import mixins
from django.shortcuts import render, redirect, get_object_or_404
from .models import (Item, Category, Order,
                     User,
                     Profile)
from .serializers import (RegistrationSerializer, ProfileSerializer, OrderedQuerySerializer,
                          ItemSerializer,
                          AllCAtSerializer, OrerdSerializer,
                          ChangePasswordSerializer)
from rest_framework import generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description="token",
                                       type=openapi.TYPE_STRING)


@api_view(['POST'])
def registeration_view(request, *args, **kwargs):
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        account = serializer.save()
        data['message'] = "Account created successfully"
        data['email'] = account.email
        token = Token.objects.get(user=account).key
        data['token'] = token
        return Response(data, status=201)
    data = serializer.errors
    return Response(data, status=400)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
        })


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Item.objects.all()
        type = self.request.query_params.get('q')
        if type is not None:
            queryset = queryset.filter(category=type)
            return queryset
        return queryset


@api_view(['GET'])
def product_detail_view(request, id):
    obj = get_object_or_404(Item, id=id)
    serializer = ItemSerializer(obj, context={'request': request})
    return Response(serializer.data, status=200)


class category_view(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = AllCAtSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['id']


class search_item_view(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = StandardResultsSetPagination
    search_fields = ['title', 'category__choice', 'description']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_view(request, *args, **kwargs):
    serializer = OrerdSerializer(data=request.data, context={'request': request})
    data = {}
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        data['message'] = "Your item is on the way, please check your mail for your ordered item"
        data['code'] = 1
        order = Order.objects.filter(user=request.user, ordered=True).first()
        data['reciept'] = order.ref_code
        return Response(data, status=201)
    data = serializer.errors
    return Response(data, status=400)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def single_order_review(request, *args, **kwargs):
    data = {}
    qparam = request.GET.get('ref_code')
    if qparam:
        try:
            obj = Order.objects.get(user=request.user, ordered=True, ref_code=qparam)
            serializer = OrderedQuerySerializer(obj)
            return Response(serializer.data, status=200)
        except ObjectDoesNotExist:
            data['message'] = "This order does not exist"
            data['code'] = 2
            return Response({}, status=404)
    return Response({}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_order_review(request, *args, **kwargs):
    data = {}
    try:
        obj = Order.objects.filter(user=request.user, ordered=True)
        serializer = OrderedQuerySerializer(obj, many=True)
        return Response(serializer.data, status=200)
    except ObjectDoesNotExist:
        data['message'] = "You have not made a purchase yet"
        data['code'] = 2
        return Response({}, status=404)
