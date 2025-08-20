from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User, UserProfile, UserSession, AccessAttempt

class CustomUserCreationForm(UserCreationForm):
    employee_id = forms.CharField(max_length=20, help_text='Format: XX123456')
    security_clearance = forms.ChoiceField(choices=User.SECURITY_LEVELS)
    rank = forms.ChoiceField(choices=User.RANKS)
    department = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=15)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'employee_id', 'security_clearance', 'rank', 
            'department', 'phone_number', 'is_field_agent'
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = (
        'username', 'employee_id', 'first_name', 'last_name', 
        'rank', 'security_clearance', 'department', 'is_field_agent', 
        'last_activity', 'is_active'
    )
    list_filter = (
        'rank', 'security_clearance', 'department', 'is_field_agent', 
        'is_active', 'is_staff', 'last_activity'
    )
    search_fields = ('username', 'employee_id', 'first_name', 'last_name', 'email')
    ordering = ('rank', 'last_name', 'first_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations SRT', {
            'fields': (
                'employee_id', 'security_clearance', 'rank', 
                'department', 'phone_number', 'is_field_agent'
            )
        }),
        ('Sécurité', {
            'fields': (
                'failed_login_attempts', 'account_locked_until', 
                'password_last_changed', 'two_factor_secret'
            ),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'employee_id',
                'first_name', 'last_name', 'email', 'security_clearance',
                'rank', 'department', 'phone_number', 'is_field_agent'
            ),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'preferred_language', 'timezone', 'created_at')
    list_filter = ('preferred_language', 'timezone', 'email_notifications', 'sms_notifications')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'location')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__username', 'ip_address', 'session_key')
    readonly_fields = ('session_key', 'created_at', 'last_activity')

@admin.register(AccessAttempt)
class AccessAttemptAdmin(admin.ModelAdmin):
    list_display = ('username_attempted', 'attempt_type', 'ip_address', 'success', 'timestamp')
    list_filter = ('attempt_type', 'success', 'timestamp')
    search_fields = ('username_attempted', 'ip_address')
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False