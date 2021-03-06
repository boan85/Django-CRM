import os
import json
from django.contrib.auth import logout, authenticate, login
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    CreateView, UpdateView, DetailView, TemplateView, View, DeleteView)
from common.models import User, Document, Attachments, Comment
from common.forms import UserForm, LoginForm, ChangePasswordForm, PasswordResetEmailForm, DocumentForm, UserCommentForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.conf import settings
from opportunity.models import Opportunity
from cases.models import Case
from contacts.models import Contact
from accounts.models import Account
from leads.models import Lead
from django.template.loader import render_to_string


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


class AdminRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.raise_exception = True
        if not request.user.role == "ADMIN":
            if not request.user.is_superuser:
                return self.handle_no_permission()
        return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["accounts"] = Account.objects.filter(status="open")
        context["contacts_count"] = Contact.objects.count()
        context["leads_count"] = Lead.objects.exclude(status='converted')
        context["opportunities"] = Opportunity.objects.all()
        return context


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = "change_password.html"

    def post(self, request, *args, **kwargs):
        error, errors = "", ""
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if not check_password(request.POST.get('CurrentPassword'), user.password):
                error = "Invalid old password"
            else:
                user.set_password(request.POST.get('Newpassword'))
                user.is_active = True
                user.save()
                return HttpResponseRedirect('/')
        else:
            errors = form.errors
        return render(request, "change_password.html", {'error': error, 'errors': errors})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context["user_obj"] = self.request.user
        return context


class LoginView(TemplateView):
    template_name = "login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST, request=request)
        if form.is_valid():

            user = User.objects.filter(email=request.POST.get('email')).first()
            # user = authenticate(username=request.POST.get('email'), password=request.POST.get('password'))
            if user is not None:
                if user.is_active:
                    user = authenticate(username=request.POST.get('email'),
                                        password=request.POST.get('password'))
                    if user is not None:
                        login(request, user)
                        return HttpResponseRedirect('/')
                    else:
                        return render(request, "login.html", {
                            "error": True,
                            "message": "Your username and password didn't match. Please try again."
                        })
                else:
                    return render(request, "login.html", {
                        "error": True,
                        "message": "Your Account is inactive. Please Contact Administrator"
                    })
            else:
                return render(request, "login.html", {
                    "error": True,
                    "message": "Your Account is not Found. Please Contact Administrator"
                })

        else:
            return render(request, "login.html", {
                "error": True,
                "message": "Your username and password didn't match. Please try again."
            })


class ForgotPasswordView(TemplateView):
    template_name = "forgot_password.html"


class LogoutView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.flush()
        return redirect("common:login")


class UsersListView(AdminRequiredMixin, TemplateView):
    model = User
    context_object_name = "users"
    template_name = "list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)
        context["users"] = self.get_queryset()
        context["per_page"] = self.request.POST.get('per_page')
        context['admin_email'] = settings.ADMIN_EMAIL
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class CreateUserView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "create.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        if form.cleaned_data.get("password"):
            user.set_password(form.cleaned_data.get("password"))
        user.save()

        mail_subject = 'Created account in CRM'
        message = render_to_string('new_user.html', {
            'user': user,
            'created_by': self.request.user

        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.content_subtype = "html"
        email.send()

        if self.request.is_ajax():
            data = {'success_url': reverse_lazy(
                'common:users_list'), 'error': False}
            return JsonResponse(data)
        return super(CreateUserView, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CreateUserView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'errors': form.errors})
        return response

    def get_context_data(self, **kwargs):
        context = super(CreateUserView, self).get_context_data(**kwargs)
        context["user_form"] = context["form"]
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return context


class UserDetailView(AdminRequiredMixin, DetailView):
    model = User
    context_object_name = "users"
    template_name = "user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        user_obj = self.object
        users_data = []
        for each in User.objects.all():
            assigned_dict = {}
            assigned_dict['id'] = each.id
            assigned_dict['name'] = each.username
            users_data.append(assigned_dict)
        context.update({
            "user_obj": user_obj,
            "opportunity_list": Opportunity.objects.filter(assigned_to=user_obj.id),
            "contacts": Contact.objects.filter(assigned_to=user_obj.id),
            "cases": Case.objects.filter(assigned_to=user_obj.id),
            "accounts": Account.objects.filter(assigned_to=user_obj.id),
            "assigned_data": json.dumps(users_data),
            "comments": user_obj.user_comments.all(),
        })
        return context


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "create.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        if self.request.is_ajax():
            if self.request.user.id != self.object.id:
                data = {'error_403': True, 'error': True}
                return JsonResponse(data)
        if user.role == "USER":
            user.is_superuser = False
        user.save()
        if self.request.user.role == "ADMIN" or self.request.user.is_superuser:
            if self.request.is_ajax():
                data = {'success_url': reverse_lazy(
                    'common:users_list'), 'error': False}
                return JsonResponse(data)
        if self.request.is_ajax():
            data = {'success_url': reverse_lazy(
                'common:profile'), 'error': False}
            return JsonResponse(data)
        return super(UpdateUserView, self).form_valid(form)

    def form_invalid(self, form):
        response = super(UpdateUserView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'errors': form.errors})
        return response

    def get_context_data(self, **kwargs):
        context = super(UpdateUserView, self).get_context_data(**kwargs)
        context["user_obj"] = self.object
        context["user_form"] = context["form"]
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return context


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect("common:users_list")


class PasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    form_class = PasswordResetEmailForm
    email_template_name = 'registration/password_reset_email.html'


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = "doc_create.html"

    def form_valid(self, form):
        doc = form.save(commit=False)
        doc.created_by = self.request.user
        doc.save()
        if self.request.is_ajax():
            data = {'success_url': reverse_lazy(
                'common:doc_list'), 'error': False}
            return JsonResponse(data)
        return super(DocumentCreateView, self).form_valid(form)

    def form_invalid(self, form):
        response = super(DocumentCreateView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'errors': form.errors})
        return response

    def get_context_data(self, **kwargs):
        context = super(DocumentCreateView, self).get_context_data(**kwargs)
        context["doc_form"] = context["form"]
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return context


class DocumentListView(LoginRequiredMixin, TemplateView):
    model = Document
    context_object_name = "documents"
    template_name = "doc_list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        request_post = self.request.POST
        if request_post:
            if request_post.get('doc_name'):
                queryset = queryset.filter(
                    title__icontains=request_post.get('doc_name'))
            if request_post.get('status'):
                queryset = queryset.filter(status=request_post.get('status'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DocumentListView, self).get_context_data(**kwargs)
        context["documents"] = self.get_queryset()
        context["status_choices"] = Document.DOCUMENT_STATUS_CHOICE
        context["per_page"] = self.request.POST.get('per_page')
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect("common:doc_list")


class UpdateDocumentView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = "doc_create.html"

    def form_valid(self, form):
        doc = form.save(commit=False)
        doc.save()
        if self.request.is_ajax():
            data = {'success_url': reverse_lazy(
                'common:doc_list'), 'error': False}
            return JsonResponse(data)
        return super(UpdateDocumentView, self).form_valid(form)

    def form_invalid(self, form):
        response = super(UpdateDocumentView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'errors': form.errors})
        return response

    def get_context_data(self, **kwargs):
        context = super(UpdateDocumentView, self).get_context_data(**kwargs)
        context["doc_obj"] = self.object
        context["doc_form"] = context["form"]
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return context


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = "doc_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        # documents = Document.objects.all()
        context.update({
            "file_type_code": self.object.file_type()[1],
            "doc_obj": self.object,
        })
        return context


def download_document(request, pk):
    doc_obj = Document.objects.filter(id=pk).last()
    path = doc_obj.document_file.path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(file_path)
            return response
    raise Http404


def download_attachment(request, pk):
    attachment_obj = Attachments.objects.filter(id=pk).last()
    path = attachment_obj.attachment.path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(file_path)
            return response
    raise Http404


def change_user_status(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return HttpResponseRedirect('/users/list/')


def add_comment(request):
    if request.method == "POST":
        user = get_object_or_404(User, id=request.POST.get('userid'))
        form = UserCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commented_by = request.user
            comment.user = user
            comment.save()
            return JsonResponse({
                "comment_id": comment.id, "comment": comment.comment,
                "commented_on": comment.commented_on,
                "commented_by": comment.commented_by.email
            })
        else:
            return JsonResponse({"error": form.errors})


def edit_comment(request, pk):
    if request.method == "POST":
        comment_obj = get_object_or_404(Comment, id=pk)
        if request.user == comment_obj.commented_by:
            form = UserCommentForm(request.POST, instance=comment_obj)
            if form.is_valid():
                comment_obj.comment = form.cleaned_data.get("comment")
                comment_obj.save(update_fields=["comment"])
                return JsonResponse({
                    "comment_id": comment_obj.id,
                    "comment": comment_obj.comment,
                })
            else:
                return JsonResponse({"error": form['comment'].errors})
        data = {'error': "You don't have permission to edit this comment."}
        return JsonResponse(data)


def remove_comment(request):
    if request.method == "POST":
        comment_obj = get_object_or_404(
            Comment, id=request.POST.get('comment_id'))
        if request.user == comment_obj.commented_by:
            comment_obj.delete()
            data = {"cid": request.POST.get("comment_id")}
            return JsonResponse(data)
        data = {'error': "You don't have permission to delete this comment."}
        return JsonResponse(data)
