"""react URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework import routers
from .views import (registeration_view, UpdateProfileView,
                    ItemListView, product_detail_view, search_item_view, category_view,
                     order_view,
                    single_order_review, all_order_review,  CustomAuthToken, ChangePasswordView)

router = routers.DefaultRouter()

app_name = 'core'
urlpatterns = [
    path('register', registeration_view, name="register"),
    path('login', CustomAuthToken.as_view()),
    path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name="profile"),
    path('products-list', ItemListView.as_view(), name="product"),
    path('product/<int:id>/', product_detail_view, name='product-detail'),
    path('search/custom/', search_item_view.as_view(), name="search-item-view"),
    path('category', category_view.as_view(), name="category"),
    path('ordered', order_view, name="order"),
    path('single-order-summary', single_order_review, name="single-order"),
    path('all-order-summary', all_order_review, name="all-order-review"),
]
