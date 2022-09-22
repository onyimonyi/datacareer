from __future__ import unicode_literals
from PIL import Image
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.utils.html import mark_safe

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)
# Create your models here.
from django.utils.safestring import mark_safe


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True,
                    is_staff=False, is_admin=False):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")

        user_obj = self.model(
            email=self.normalize_email(email),
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.active = is_active
        user_obj.admin = is_admin
        user_obj.save(using=self._db)
        return user_obj

    def create_staff_user(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_staff=True,
        )
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_email(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_active(self):
        return self.active


    @property
    def is_admin(self):
        return self.admin

class UserBalance(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, related_name='user_balance')
    balance = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = 'UserBalance'

    def save(self, *args, **kwargs):
        self.balance = round(self.balance, 2)
        super(UserBalance, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=225, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return str(self.user.email)

class Category(models.Model):
    choice = models.CharField(max_length=100)

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name_plural = "Categories"


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10000, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.TextField()
    picture = models.ImageField(upload_to='picture', max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return F"{self.quantity} of {self.item.title}"

    class Meta:
        ordering = ['-id']




class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    cart = models.ManyToManyField(OrderItem)
    ref_code = models.CharField(max_length=30)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    dispatched = models.BooleanField(default=False)
    total = models.IntegerField(default=1)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.CharField(max_length=30)
    packaged = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    def __str__(self):
        return F"{self.ref_code} to {self.user.full_name} "

    class Meta:
        ordering = ['-id']






class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    tx_ref = models.CharField(max_length=1000)
    amount = models.FloatField()
    flw_ref = models.CharField(max_length=1000)
    tansaction_id = models.CharField(max_length=1000)
    status = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    ref_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pk}"
