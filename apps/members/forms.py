from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from .models import Member, Family, Comment


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'placeholder': _("This will also be your username")}))
    name = forms.CharField(label=_("Name"), widget=forms.TextInput(attrs={'placeholder': _('Your first name')}))
    family_name = forms.CharField(label=_("Family name"), max_length=255, widget=forms.TextInput(attrs={'placeholder': _('Your last name')}))
    birthday = forms.DateField(label=_("Birthday"), input_formats=['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'],
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'id': 'datepicker'}), required=True)
    password1 = forms.CharField(label=_("Password"), max_length=255, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), max_length=255, widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ("email", "name")

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))

        return password2

    def clean_family_name(self):
        family_name = self.cleaned_data.get('family_name')

        try:
            family = Family.objects.get(name=family_name)
        except Family.DoesNotExist:
            family = Family(name=family_name)
            family.save()

        self.family = family

        return family_name

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.name = self.cleaned_data["name"]
        user.family_name = self.family
        user.birthday = self.cleaned_data['birthday']
        user.is_active = False
        if commit:
            user.save()
            subject = 'New member needs activation'
            message = 'There is a new member: %s %s' % (user.name, user.family_name)
            from_email = settings.FROM_EMAIL
            to_email = [settings.ADMIN_EMAIL, ]
            send_mail(subject, message, from_email, to_email)
        return user


class MemberChangeForm(forms.ModelForm):
    birthday = forms.DateField(label=_("Birthday"), input_formats=['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'],
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'id': 'datepicker'}))
    # photo = forms.ImageField(label=_("Photo"), required=True)

    class Meta:
        model = Member
        fields = ["name", "email", "birthday", "telephone", "street", "housenumber",
                  "zipcode", "city", "country"]


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text', ]


class MailMembersForm(forms.Form):
    title = forms.CharField(label=_("Title"), max_length=255, required=True)
    text = forms.CharField(label=_("Message"), max_length=255, required=True, widget=forms.Textarea)
