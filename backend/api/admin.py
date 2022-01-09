from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Admin
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined')
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance', 'created_at', 'updated_at', 'publickey')
    search_fields = ('user', 'currency')
    list_filter = ('user', 'currency')
    readonly_fields = ('created_at', 'updated_at', 'publickey', 'privatekey')

    add_fieldsets = (
        (None, {'fields': ('user', 'currency', 'balance')}),
    )

    fieldsets = (
        (None, {'fields': ('user', 'currency', 'balance')}),
        ('Private Key', {'fields': ('publickey', 'privatekey')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'currency', 'created_at')
    search_fields = ('sender', 'receiver', 'amount', 'currency')
    list_filter = ('sender', 'receiver', 'amount', 'currency')

    add_fieldsets = (
        (None, {'fields': ('sender', 'receiver', 'amount', 'currency')}),
    )

    fieldsets = (
        (None, {'fields': ('sender', 'receiver', 'amount', 'currency')}),
        ('Signature', {'fields': ('sender_signature','receiver_signature')}),
        ('Important dates', {'fields': ('created_at',)}),
        ("Before Balance", {'fields': ('before_sender_amount_snapshot', 'before_receiver_amount_snapshot')}),
        ("After Balance", {'fields': ('after_sender_amount_snapshot', 'after_receiver_amount_snapshot')}),
    )

    readonly_fields = ('created_at','sender_signature','receiver_signature', 'before_sender_amount_snapshot', 'before_receiver_amount_snapshot', 'after_sender_amount_snapshot', 'after_receiver_amount_snapshot')

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'admin')
    search_fields = ('name', 'symbol')
    list_filter = ('name', 'symbol')


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Currency, CurrencyAdmin)