"""Manage admin page for main app."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib import admin
from django.utils.html import mark_safe
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import TokenProxy
from .models import (Category, Item, Order,
                     UserBalance, Profile, Payment)

User = get_user_model()

TokenAdmin.raw_id_fields = ['user']


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'admin', 'active', 'staff')
    list_filter = ('admin', 'active', 'staff')
    fieldsets = (
        (None, {'fields': ('full_name', 'email', 'password')}),
        # ('FULL NAME', {'fields': ('full_name',)}),
        ('permissions', {'fields': ('admin', 'active', 'staff')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class AdminUserBalance(admin.ModelAdmin):
    list_display = [
        'user',
        'balance'

    ]
    list_display_links = [
        'user',
    ]

    list_filter = [
        'user',
    ]

    search_fields = [
        'user__email',

    ]


def update_order_to_packaged(modeladmin, request, queryset):
    queryset.update(packaged=True)


update_order_to_packaged.short_description = 'Update pending orders to packaged'


class AdminOrder(admin.ModelAdmin):
    list_per_page = 10
    fields = ['payment', 'billing_address']
    list_display = [
        'user',
        'get_cart',
        'get_total',
        'get_payment',
        'get_address',
        'ordered_date',
        'ordered',
        'packaged',
        'received'

    ]

    list_display_links = [
        'user',

    ]

    list_filter = [
        'ordered_date',
        'packaged',
        'received',
    ]

    search_fields = [
        'user__email',
        'ordered_date',
        'received',
        'packaged',
        'ref_code',
    ]
    actions = [update_order_to_packaged]

    def get_cart(self, obj):
        return "\n".join([f"({a.quantity}  of {a.item.title}"
                          for a in obj.cart.all()])

    get_cart.short_description = 'Summary of Oder detsils'

    def get_total(self, obj):
        return f"{obj.total} item(s)"

    get_total.short_description = 'item count'

    def get_payment(self, obj):
        return f" ₦{obj.payment.amount}"

    get_payment.short_description = 'PAID'

    def get_address(self, obj):
        return f"{obj.billing_address} "

    get_address.short_description = 'billing address and landmark'

    def image_tag(self, obj):
        return mark_safe(['<img src="{}"/>'.format(a.item.picture.url) for a in obj.cart.all()])

    image_tag.short_description = 'Image'


class AdminPayment(admin.ModelAdmin):
    list_per_page = 10
    list_display = [
        'user',
        'tx_ref',
        'amount',
        'flw_ref',
        'tansaction_id',
        'status',
        'timestamp',
    ]

    list_display_links = [
        'user',

    ]

    list_filter = [
        'user',
        'amount',
        'flw_ref',
    ]

    search_fields = [
        'user__email',
        'amount',
        'flw_ref'

    ]


admin.site.register(Profile)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Category)
admin.site.register(Payment, AdminPayment)
admin.site.register(Item)
admin.site.register(Order, AdminOrder)
admin.site.register(UserBalance, AdminUserBalance)
admin.site.unregister(TokenProxy)
