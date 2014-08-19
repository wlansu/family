from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from .models import Member, Family


class AdminMemberCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Password'), max_length=255,  widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), max_length=255, widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ('email', 'family_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            msg = _("Passwords don't match")
            raise forms.ValidationError(msg)
        return password2

    def save(self, commit=True):
        user = super(AdminMemberCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        if commit:
            user.save()

        return user


class AdminMemberChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Member

    def clean_password(self):
        return self.initial["password"]

    def _clean_form(self):
        print 'here'

        return super(AdminMemberChangeForm, self)._clean_form()


class MemberAdmin(UserAdmin):
    add_form = AdminMemberCreationForm
    form = AdminMemberChangeForm

    list_display = ('email', 'name', 'family_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'family_name', 'name')
    ordering = ('name', )
    fieldsets = (
        (None, {'fields': {'email', 'password'}}),
        ('Parents', {'fields': {'parents'}}),
        ('Partner', {'fields': {'partner'}}),
        ('Children', {'fields': {'children'}}),
        ('Personal info', {
        'fields': {'name', 'family_name', 'photo', 'birthday', 'street', 'housenumber', 'zipcode', 'city', 'country',
                   'telephone'}}),
        ('Permissions', {'fields': ('is_active', 'send_activation_email', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'family_name', 'password1', 'password2')}),
    )


admin.site.register(Member, MemberAdmin)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', )


admin.site.register(Family, FamilyAdmin)
