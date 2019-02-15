import json

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView, TemplateView, View)

from accounts.models import Account, Tags
from common.forms import BillingAddressForm
from common.models import User, Comment, Team, Attachments
from common.utils import LEAD_STATUS, LEAD_SOURCE, COUNTRIES
from contacts.models import Contact
from leads.models import Lead
from leads.forms import LeadCommentForm, LeadForm, LeadAttachmentForm
from planner.models import Event, Reminder
from planner.forms import ReminderForm


class LeadListView(LoginRequiredMixin, TemplateView):
    model = Lead
    context_object_name = "lead_obj"
    template_name = "leads.html"

    def get_queryset(self):
        queryset = self.model.objects.all().exclude(status='converted')
        request_post = self.request.POST
        if request_post:
            if request_post.get('first_name'):
                queryset = queryset.filter(first_name__icontains=request_post.get('first_name'))
            if request_post.get('last_name'):
                queryset = queryset.filter(last_name__icontains=request_post.get('last_name'))
            if request_post.get('city'):
                queryset = queryset.filter(address__city__icontains=request_post.get('city'))
            if request_post.get('email'):
                queryset = queryset.filter(email__icontains=request_post.get('email'))
            if request_post.get('status'):
                queryset = queryset.filter(status=request_post.get('status'))
            if request_post.get('tag'):
                queryset = queryset.filter(tags__in=request_post.get('tag'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        context["lead_obj"] = self.get_queryset()
        context["status"] = LEAD_STATUS
        context["per_page"] = self.request.POST.get('per_page')
        context['tags'] = Tags.objects.all()
        context['open_leads'] = self.get_queryset()
        context['close_leads'] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class CreateLeadView(LoginRequiredMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = "create_lead.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(CreateLeadView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateLeadView, self).get_form_kwargs()
        kwargs.update({"assigned_to": self.users})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        address_form = BillingAddressForm(request.POST)
        if form.is_valid() and address_form.is_valid():
            return self.form_valid(form, address_form)

        return self.form_invalid(form, address_form)

    def form_valid(self, form, address_form):
        address_object = address_form.save()
        lead_obj = form.save(commit=False)
        lead_obj.address = address_object
        lead_obj.created_by = self.request.user
        lead_obj.save()
        if self.request.POST.get('tags', ''):
            tags = self.request.POST.get("tags")
            splitted_tags = tags.split(",")
            for t in splitted_tags:
                tag = Tags.objects.filter(name=t)
                if tag:
                    tag = tag[0]
                else:
                    tag = Tags.objects.create(name=t)
                lead_obj.tags.add(tag)
        if self.request.POST.getlist('assigned_to', []):
            lead_obj.assigned_to.add(*self.request.POST.getlist('assigned_to'))
            assigned_to_list = self.request.POST.getlist('assigned_to')
            current_site = get_current_site(self.request)
            for assigned_to_user in assigned_to_list:
                user = get_object_or_404(User, pk=assigned_to_user)
                mail_subject = 'Assigned to lead.'
                message = render_to_string('assigned_to/leads_assigned.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': self.request.scheme,
                    'lead': lead_obj
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.send()
        if self.request.POST.getlist('teams', []):
            lead_obj.teams.add(*self.request.POST.getlist('teams'))
        # if self.request.POST.get('status') == "converted":
        try:
            contact_object = Contact.objects.get(email=self.request.POST.get('contact_email', ''))
            # TODO add redirected page
            return HttpResponseRedirect(reverse("leads:contact_exist", args=[lead_obj.id]))
        except Contact.DoesNotExist:
            good_phone = False
            phone_number = lead_obj.phone
            # import re
            # try:
            #     m = re.search(r'^\+?[1-9]\d{1,14}$', phone_number)
            #     match = m.goup(0)
            #     good_phone = True
            # except AttributeError:
            #     context = {'bad_phone': 'bad_phone'}
            #     return context
            contact_object = Contact.objects.create(
                created_by=self.request.user,
                email=lead_obj.contact_email, phone=lead_obj.phone,
                description=self.request.POST.get('memo'),
                first_name=lead_obj.first_name,
                last_name=lead_obj.last_name
            )
            lead_obj.contact = contact_object
            lead_obj.save()
            # account_object = Account.objects.create(
            #     created_by=self.request.user, name=lead_obj.account_name,
            #     email=lead_obj.email, phone=lead_obj.phone,
            #     description=self.request.POST.get('description'),
            #     website=self.request.POST.get('website'),
            # )
            # account_object.billing_address = address_object
            # for tag in lead_obj.tags.all():
            #     account_object.tags.add(tag)
            # account_object.tags.add(address_object)
        if self.request.POST.getlist('assigned_to', []):
            contact_object.assigned_to.add(*self.request.POST.getlist('assigned_to'))
            # account_object.assigned_to.add(*self.request.POST.getlist('assigned_to'))
            assigned_to_list = self.request.POST.getlist('assigned_to')
            current_site = get_current_site(self.request)
            for assigned_to_user in assigned_to_list:
                user = get_object_or_404(User, pk=assigned_to_user)
                mail_subject = 'Assigned to account.'
                message = render_to_string('assigned_to/contact_assigned.html', {
                    # message = render_to_string('assigned_to/account_assigned.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': self.request.scheme,
                    'account': contact_object
                    # 'account': account_object
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.send()
        if self.request.POST.getlist('teams', []):
            contact_object.teams.add(*self.request.POST.getlist('teams'))
        contact_object.save()
        if self.request.POST.get("savenewform"):
            return redirect("leads:add_lead")
        return redirect('leads:list')

    def form_invalid(self, form, address_form):
        return self.render_to_response(
            self.get_context_data(form=form, address_form=address_form))

    def get_context_data(self, **kwargs):
        context = super(CreateLeadView, self).get_context_data(**kwargs)
        context["lead_form"] = context["form"]
        context["teams"] = Team.objects.all()
        context["accounts"] = Account.objects.all()
        context["users"] = self.users
        context["countries"] = COUNTRIES
        context["status"] = LEAD_STATUS
        context["source"] = LEAD_SOURCE
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
        context["teams_list"] = [
            int(i) for i in self.request.POST.getlist('teams', []) if i]
        if "address_form" in kwargs:
            context["address_form"] = kwargs["address_form"]
        else:
            if self.request.POST:
                context["address_form"] = BillingAddressForm(self.request.POST)
            else:
                context["address_form"] = BillingAddressForm()
        return context


class LeadContactAlreadyExist(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = "contact_exist.html"

    def get_context_data(self, **kwargs):
        context = super(LeadContactAlreadyExist, self).get_context_data(**kwargs)
        return context


class RelateLeadAndContact(LoginRequiredMixin, UpdateView):
    model = Lead
    template_name = "related_account.html"
    fields = ('contact', 'contact_email', 'id')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            lead = Lead.objects.get(id=kwargs.get('pk', ''))
            contact = Contact.objects.get(email=lead.contact_email)
            lead.contact = contact
            lead.save()
        return redirect("leads:list")


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    context_object_name = "lead_record"
    template_name = "view_leads.html"

    def get_context_data(self, **kwargs):
        context = super(LeadDetailView, self).get_context_data(**kwargs)
        comments = Comment.objects.filter(lead__id=self.object.id).order_by('-id')
        attachments = Attachments.objects.filter(lead__id=self.object.id).order_by('-id')
        events = Event.objects.filter(
            Q(created_by=self.request.user) | Q(updated_by=self.request.user)
        ).filter(attendees_leads=context["lead_record"])
        meetings = events.filter(event_type='Meeting').order_by('-id')
        calls = events.filter(event_type='Call').order_by('-id')
        RemindersFormSet = modelformset_factory(Reminder, form=ReminderForm, can_delete=True)
        reminder_form_set = RemindersFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '10',
        })

        assigned_data = []
        for each in context['lead_record'].assigned_to.all():
            assigned_dict = {}
            assigned_dict['id'] = each.id
            assigned_dict['name'] = each.email
            assigned_data.append(assigned_dict)

        context.update({
            "attachments": attachments, "comments": comments, "status": LEAD_STATUS, "countries": COUNTRIES,
            "reminder_form_set": reminder_form_set, "meetings": meetings, "calls": calls,
            "assigned_data": json.dumps(assigned_data)})
        return context


class UpdateLeadView(LoginRequiredMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = "create_lead.html"

    def dispatch(self, request, *args, **kwargs):
        self.error = ""
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(UpdateLeadView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(UpdateLeadView, self).get_initial()
        status = self.request.GET.get('status', None)
        if status:
            initial.update({"status": status})
        return initial

    def get_form_kwargs(self):
        kwargs = super(UpdateLeadView, self).get_form_kwargs()
        kwargs.update({"assigned_to": self.users})
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        status = request.GET.get('status', None)
        if status:
            self.error = "This field is required."
            self.object.status = "converted"
        return super(UpdateLeadView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        address_obj = self.object.address
        form = self.get_form()
        address_form = BillingAddressForm(request.POST, instance=address_obj)
        if request.POST.get('status') == "converted":
            form.fields['contact_email'].required = True
        else:
            form.fields['contact_email'].required = False
        if form.is_valid() and address_form.is_valid():
            return self.form_valid(form, address_form)

        return self.form_invalid(form, address_form)

    def form_valid(self, form, address_form):
        assigned_to_ids = self.get_object().assigned_to.all().values_list('id', flat=True)
        address_obj = address_form.save()
        lead_obj = form.save(commit=False)
        lead_obj.address = address_obj
        lead_obj.save()
        lead_obj.teams.clear()
        lead_obj.tags.clear()
        all_members_list = []
        if self.request.POST.get('tags', ''):
            tags = self.request.POST.get("tags")
            splitted_tags = tags.split(",")
            for t in splitted_tags:
                tag = Tags.objects.filter(name=t)
                if tag:
                    tag = tag[0]
                else:
                    tag = Tags.objects.create(name=t)
                lead_obj.tags.add(tag)
        if self.request.POST.getlist('assigned_to', []):
            if self.request.POST.get('status') != "converted":

                current_site = get_current_site(self.request)

                assigned_form_users = form.cleaned_data.get('assigned_to').values_list('id', flat=True)
                all_members_list = list(set(list(assigned_form_users)) - set(list(assigned_to_ids)))
                if len(all_members_list):
                    for assigned_to_user in all_members_list:
                        user = get_object_or_404(User, pk=assigned_to_user)
                        mail_subject = 'Assigned to lead.'
                        message = render_to_string('assigned_to/leads_assigned.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'protocol': self.request.scheme,
                            'lead': lead_obj
                        })
                        email = EmailMessage(mail_subject, message, to=[user.email])
                        email.send()

            lead_obj.assigned_to.clear()
            lead_obj.assigned_to.add(*self.request.POST.getlist('assigned_to'))

        if self.request.POST.getlist('teams', []):
            lead_obj.teams.add(*self.request.POST.getlist('teams'))
        if self.request.POST.get('status') == "converted":
            account_object = Account.objects.create(
                created_by=self.request.user, name=lead_obj.account_name,
                email=lead_obj.email, phone=lead_obj.phone,
                description=self.request.POST.get('description'),
                website=self.request.POST.get('website')
            )
            account_object.billing_address = address_obj
            for tag in lead_obj.tags.all():
                account_object.tags.add(tag)
            if self.request.POST.getlist('assigned_to', []):
                account_object.assigned_to.add(*self.request.POST.getlist('assigned_to'))
                assigned_to_list = self.request.POST.getlist('assigned_to')
                current_site = get_current_site(self.request)
                for assigned_to_user in assigned_to_list:
                    user = get_object_or_404(User, pk=assigned_to_user)
                    mail_subject = 'Assigned to account.'
                    message = render_to_string('assigned_to/account_assigned.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'protocol': self.request.scheme,
                        'account': account_object
                    })
                    email = EmailMessage(mail_subject, message, to=[user.email])
                    email.send()
            if self.request.POST.getlist('teams', []):
                account_object.teams.add(*self.request.POST.getlist('teams'))
            account_object.save()
        status = self.request.GET.get('status', None)
        if status:
            return redirect('accounts:list')

        return redirect('leads:list')

    def form_invalid(self, form, address_form):
        return self.render_to_response(
            self.get_context_data(form=form, address_form=address_form))

    def get_context_data(self, **kwargs):
        context = super(UpdateLeadView, self).get_context_data(**kwargs)
        context["lead_obj"] = self.object
        context["address_obj"] = self.object.address
        context["lead_form"] = context["form"]
        context["teams"] = Team.objects.all()
        context["accounts"] = Account.objects.all()
        context["users"] = self.users
        context["countries"] = COUNTRIES
        context["status"] = LEAD_STATUS
        context["source"] = LEAD_SOURCE
        context["error"] = self.error
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
        context["teams_list"] = [
            int(i) for i in self.request.POST.getlist('teams', []) if i]
        if "address_form" in kwargs:
            context["address_form"] = kwargs["address_form"]
        else:
            if self.request.POST:
                context["address_form"] = BillingAddressForm(
                    self.request.POST, instance=context["address_obj"])
            else:
                context["address_form"] = BillingAddressForm(
                    instance=context["address_obj"])
        return context


class DeleteLeadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    # @user_passes_test(lambda u: u.is_superuser)
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.object = get_object_or_404(Lead, id=kwargs.get("pk"))
            if self.object.address_id:
                self.object.address.delete()
            self.object.delete()
        return redirect("leads:list")


class ConvertLeadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        lead_obj = get_object_or_404(Lead, id=kwargs.get("pk"))
        if lead_obj.contact_email:
            lead_obj.status = 'converted'
            lead_obj.save()
            from django.db import IntegrityError
            try:
                contact_object = Contact.objects.create(
                    created_by=self.request.user,
                    email=lead_obj.contact_email, phone=lead_obj.phone,
                    description=self.request.POST.get('memo'),
                    first_name=lead_obj.first_name,
                    last_name=lead_obj.last_name
                )
            except IntegrityError:
                return HttpResponseRedirect(reverse("leads:contact_exist", args=[lead_obj.id]))
            assignedto_list = lead_obj.assigned_to.all().values_list('id', flat=True)
            contact_object.assigned_to.add(*assignedto_list)
            contact_object.save()
            current_site = get_current_site(self.request)
            for assigned_to_user in assignedto_list:
                user = get_object_or_404(User, pk=assigned_to_user)
                mail_subject = 'Assigned to account.'
                message = render_to_string('assigned_to/account_assigned.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': self.request.scheme,
                    'contact': contact_object
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.send()
            return redirect("accounts:list")

        return HttpResponseRedirect(
            reverse('leads:edit_lead', kwargs={'pk': lead_obj.id}) + '?status=converted')


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = LeadCommentForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.object = None
        self.lead = get_object_or_404(Lead, id=request.POST.get('leadid'))
        if (
                                request.user in self.lead.assigned_to.all() or
                                request.user == self.lead.created_by or request.user.is_superuser or
                        request.user.role == 'ADMIN'
        ):
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)

            return self.form_invalid(form)

        data = {'error': "You don't have permission to comment."}
        return JsonResponse(data)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.commented_by = self.request.user
        comment.lead = self.lead
        comment.save()
        return JsonResponse({
            "comment_id": comment.id, "comment": comment.comment,
            "commented_on": comment.commented_on,
            "commented_by": comment.commented_by.email
        })

    def form_invalid(self, form):
        return JsonResponse({"error": form['comment'].errors})


class UpdateCommentView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.comment_obj = get_object_or_404(Comment, id=request.POST.get("commentid"))
        if request.user == self.comment_obj.commented_by:
            form = LeadCommentForm(request.POST, instance=self.comment_obj)
            if form.is_valid():
                return self.form_valid(form)

            return self.form_invalid(form)

        data = {'error': "You don't have permission to edit this comment."}
        return JsonResponse(data)

    def form_valid(self, form):
        self.comment_obj.comment = form.cleaned_data.get("comment")
        self.comment_obj.save(update_fields=["comment"])
        return JsonResponse({
            "commentid": self.comment_obj.id,
            "comment": self.comment_obj.comment,
        })

    def form_invalid(self, form):
        return JsonResponse({"error": form['comment'].errors})


class DeleteCommentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(Comment, id=request.POST.get("comment_id"))
        if request.user == self.object.commented_by:
            self.object.delete()
            data = {"cid": request.POST.get("comment_id")}
            return JsonResponse(data)

        data = {'error': "You don't have permission to delete this comment."}
        return JsonResponse(data)


class GetLeadsView(LoginRequiredMixin, ListView):
    model = Lead
    context_object_name = "leads"
    template_name = "leads_list.html"

    def get_context_data(self, **kwargs):
        context = super(GetLeadsView, self).get_context_data(**kwargs)
        context["leads"] = self.get_queryset()
        return context


class AddAttachmentsView(LoginRequiredMixin, CreateView):
    model = Attachments
    form_class = LeadAttachmentForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.object = None
        self.lead = get_object_or_404(Lead, id=request.POST.get('leadid'))
        if (
                                request.user in self.lead.assigned_to.all() or
                                request.user == self.lead.created_by or request.user.is_superuser or
                        request.user.role == 'ADMIN'
        ):
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            return self.form_invalid(form)

        data = {'error': "You don't have permission to add attachment."}
        return JsonResponse(data)

    def form_valid(self, form):
        attachment = form.save(commit=False)
        attachment.created_by = self.request.user
        attachment.file_name = attachment.attachment.name
        attachment.lead = self.lead
        attachment.save()
        return JsonResponse({
            "attachment_id": attachment.id,
            "attachment": attachment.file_name,
            "attachment_url": attachment.attachment.url,
            "created_on": attachment.created_on,
            "created_by": attachment.created_by.email,
            "download_url": reverse('common:download_attachment', kwargs={'pk': attachment.id}),
            "attachment_display": attachment.get_file_type_display()
        })

    def form_invalid(self, form):
        return JsonResponse({"error": form['attachment'].errors})


class DeleteAttachmentsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(Attachments, id=request.POST.get("attachment_id"))
        if (
                            request.user == self.object.created_by or request.user.is_superuser or
                        request.user.role == 'ADMIN'
        ):
            self.object.delete()
            data = {"aid": request.POST.get("attachment_id")}
            return JsonResponse(data)

        data = {'error': "You don't have permission to delete this attachment."}
        return JsonResponse(data)
