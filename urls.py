from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apps.members.views import HomeView, MemberDetail, Register, MemberChangeView, CreateComment, EditComment, \
    DeleteComment, FAQView, MailMembersView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^member/(?P<id>\d+)', login_required(MemberDetail.as_view()), name='member'),
    url(r'^accounts/register', Register.as_view(), name="register"),
    url(r'^accounts/change/(?P<id>\d+)', login_required(MemberChangeView.as_view()), name="change"),
    url(r'^accounts/login', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout', 'django.contrib.auth.views.logout', name='logout'),
    url(r'^accounts/password_change', 'django.contrib.auth.views.password_change',
        name='password_change'),
    url(r'^accounts/password_change/done', 'django.contrib.auth.views.password_change_done',
        name='password_change_done'),
    url(r'^accounts/password_reset', 'django.contrib.auth.views.password_reset',
        name='password_reset'),
    url(r'^accounts/password_reset/done', 'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^accounts/reset/done', 'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
    url(r'^add_child/(?P<child_id>\d+)', 'apps.members.views.add_child', name="add_child"),
    url(r'^add_parent/(?P<parent_id>\d+)', 'apps.members.views.add_parent', name="add_parent"),
    url(r'^add_partner/(?P<partner_id>\d+)', 'apps.members.views.add_partner', name="add_partner"),
    url(r'^comment/create', CreateComment.as_view(), name='create_comment'),
    url(r'^comment/edit/(?P<pk>\d+)', EditComment.as_view(), name='edit_comment'),
    url(r'^comment/delete/(?P<pk>\d+)', DeleteComment.as_view(), name='delete_comment'),
    url(r'faq/', login_required(FAQView.as_view()), name='faq'),
    url(r'send-mail/$', login_required(MailMembersView.as_view()), name='mail_members'),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"^media/(?P<path>.*)$", "django.views.static.serve",
            {"document_root": settings.MEDIA_ROOT,
             "show_indexes": True}
        ),
    )
