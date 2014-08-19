import datetime
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _


class MemberUserManager(BaseUserManager):
    def create_user(self, email, family_name, password=None):
        """
            Make sure every user has a family name.
        """
        if not email:
            msg = _('Users must have an email adress')
            raise ValueError(msg)
        if not family_name:
            msg = _('Users must have a family')
            raise ValueError(msg)

        user = Member(email=MemberUserManager.normalize_email(email))
        user.family_name = Family().get_family_name(name=family_name)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, family_name):
        user = Member(email=MemberUserManager.normalize_email(email))
        user.family_name = Family().get_family_name(name=family_name)
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class ActiveMemberUserManager(MemberUserManager):
    """
    Manager whose queryset returns all members, instead of just the active ones.
    """

    def get_query_set(self):
        """
        Prevent inactive users from appearing on the site.
        """
        qs = super(ActiveMemberUserManager, self).get_query_set()

        return qs.filter(is_active=True)


class Family(models.Model):
    name = models.CharField(_('Name'), max_length=100)

    verbose_name = _('Family')
    verbose_name_plural = _('Families')

    def __unicode__(self):
        return u'%s' % self.name

    def get_family_name(self, name):
        try:
            family = Family.objects.get(name=name)
        except Family.DoesNotExist:
            family = Family(name=name)
            family.save()

        return family


class Member(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email'), unique=True, db_index=True)
    name = models.CharField(_('Name'), max_length=100, blank=True, null=True)
    photo = models.ImageField(_('Picture'), upload_to='pictures/', blank=True, null=True)
    family_name = models.ForeignKey('Family')
    birthday = models.DateField(_('Birthday'), blank=True, null=True)
    parents = models.ManyToManyField('self', symmetrical=False, blank=True, null=True, related_name='member_parents')
    children = models.ManyToManyField('self', symmetrical=False, blank=True, null=True, related_name='member_children')
    partner = models.ForeignKey('self', blank=True, null=True, related_name='member_partner')
    telephone = models.CharField(_('Phone number'), max_length=20, blank=True, null=True)
    street = models.CharField(_('Street'), max_length=100, blank=True, null=True)
    housenumber = models.CharField(_('House number'), max_length=10, blank=True, null=True)
    zipcode = models.CharField(_('Zipcode'), max_length=100, blank=True, null=True)
    city = models.CharField(_('City'), max_length=100, blank=True, null=True)
    country = models.CharField(_('Country'), max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'

    is_active = models.BooleanField(default=True)
    send_activation_email = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = MemberUserManager()
    active = ActiveMemberUserManager()

    verbose_name = _('Member')
    verbose_name_plural = _('Members')

    class Meta:
        ordering = ['birthday', 'name']

    def get_full_name(self):
        return u'%s %s' % (self.name, self.family_name)

    def get_short_name(self):
        return u'%s' % self.name

    def __unicode__(self):
        return self.get_full_name()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.send_activation_email:
            subject = 'Activation: www.lansu.eu'
            message = 'Your account has been activated, you can now log in/Je account is geactiveerd, je kunt nu inloggen.'
            from_email = settings.FROM_EMAIL
            to_email = [self.email]
            send_mail(subject, message, from_email, to_email)
            self.send_activation_email = False

        return super(Member, self).save(force_insert=False, force_update=False, using=None, update_fields=None)



class Comment(models.Model):
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    text = models.TextField(_("Text"))
    member = models.ForeignKey(Member)

    class Meta:
        ordering = ['-date', ]

    def __unicode__(self):
        return u'%s' % datetime.datetime.strftime(self.date, '%d-%m-%Y %H:%M')
