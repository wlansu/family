from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView, FormView

from .forms import RegisterForm, MemberChangeForm, CreateCommentForm, MailMembersForm
from .models import Member, Comment


class HomeView(ListView):
    model = Member
    template_name = 'homepage.html'
    context_object_name = 'members'

    def get_queryset(self):
        return Member.active.all()

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        # needed to show the link to detail view
        try:
            wouter = self.model.objects.get(name='Wouter')
        except:
            wouter = self.model.objects.filter(is_superuser=True)[0]

        latest_comments = Comment.objects.all()[:5]

        context.update({
            'wouter': wouter,
            'latest_comments': latest_comments
        })

        return context


class FAQView(TemplateView):
    template_name = 'faq.html'


class MemberDetail(DetailView):
    model = Member
    template_name = 'member-detail.html'
    context_object_name = 'member'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(MemberDetail, self).get_context_data(**kwargs)
        obj = self.get_object()
        user = Member.objects.get(id=self.request.user.id)
        can_add_child = False
        can_add_parent = False
        can_add_partner = False
        if obj.id != user.id and obj.birthday and user.birthday:
            if obj.birthday < user.birthday and obj not in user.parents.all():
                can_add_parent = True
            if obj.birthday > user.birthday and obj not in user.children.all():
                can_add_child = True
            if obj not in user.parents.all() and user.children.all() and obj != user.partner:
                can_add_partner = True
        context.update({
            'comments': Comment.objects.filter(member=self.get_object()),
            'can_add_child': can_add_child,
            'can_add_parent': can_add_parent,
            'can_add_partner': can_add_partner
        })

        return context


class Register(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'

    def get_success_url(self):
        messages.success(self.request, _("Your registration was successful. An administrator will have to approve your account before you can log in."))
        return reverse('home')


class MemberChangeView(UpdateView):
    model = Member
    form_class = MemberChangeForm
    template_name = 'registration/change.html'
    pk_url_kwarg = 'id'
    context_object_name = 'member'

    def get(self, request, *args, **kwargs):
        member = self.get_object()
        if request.user.id != member.id:
            return HttpResponseForbidden()

        return super(MemberChangeView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _("Your information has been changed."))
        return reverse('member', args=[self.kwargs['id']])


class CreateComment(CreateView):
    form_class = CreateCommentForm
    template_name = 'create_comment.html'

    def get_success_url(self):
        messages.success(self.request, _("Your comment was created."))
        return reverse('member', args=[self.request.user.id])

    def form_valid(self, form):
        form.instance.member = Member.objects.get(id=self.request.user.id)
        return super(CreateComment, self).form_valid(form)


class DeleteComment(DeleteView):
    model = Comment

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.member == request.user:
            obj.delete()
            return HttpResponseRedirect(self.get_success_url())

        return HttpResponseForbidden(_("You are not the owner of this comment"))

    def get_success_url(self):
        messages.success(self.request, _('Your comment has been deleted.'))
        return reverse('member', args=[self.request.user.id])


class EditComment(UpdateView):
    model = Comment
    fields = ['text', ]
    template_name = 'create_comment.html'

    def get_success_url(self):
        messages.success(self.request, _("Your comment was changed."))
        return reverse('member', args=[self.request.user.id])


class MailMembersView(FormView):
    form_class = MailMembersForm
    template_name = 'mail_members.html'

    def form_valid(self, form):
        subject = form.cleaned_data['title']
        message = form.cleaned_data['text']
        from_email = settings.FROM_EMAIL
        to_email = [x.email for x in Member.active.all()]
        send_mail(subject, message, from_email, to_email)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, _("The email has been sent."))
        return reverse('member', args=[self.request.user.id])


def add_child(request, child_id):
    child = Member.objects.get(id=child_id)
    member = Member.objects.get(id=request.user.id)

    if member.birthday > child.birthday:
        messages.error(request, _("You are younger than %s.") % child.get_short_name())
    else:
        messages.success(request, _("%s has been added as your child.") % child.get_short_name())
        member.children.add(child)
        member.save()
        child.parents.add(member)
        child.save()

    return redirect(reverse('member', args=[child_id]))


def add_parent(request, parent_id):
    parent = Member.objects.get(id=parent_id)
    member = Member.objects.get(id=request.user.id)

    if len(member.parents.all()) >= 2:
        messages.error(request, _("You already have 2 parents. If this is a mistake, please contact an administrator."))
    elif member.birthday < parent.birthday:
        messages.error(request, _("You are older than %s.") % parent.get_short_name())
    else:
        messages.success(request, _("%s has been added as your parent.") % parent.get_short_name())
        member.parents.add(parent)
        member.save()
        parent.children.add(member)
        parent.save()

    return redirect(reverse('member', args=[parent_id]))


def add_partner(request, partner_id):
    partner = Member.objects.get(id=partner_id)
    member = Member.objects.get(id=request.user.id)

    if member.partner:
        messages.error(request,
            _("You already have a partner: %s. If this is a mistake, please contact an administrator")
            % member.partner.get_full_name())
    else:
        messages.success(request, _("%s has been added as your partner.") % partner.get_short_name())
        member.partner = partner
        member.save()
        partner.partner = member
        partner.save()

    return redirect(reverse('member', args=[partner_id]))
