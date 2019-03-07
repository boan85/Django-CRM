from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views import View

from wc_gravity_forms.gravity_forms_utils import GravityFormsUtils


class GravityFormsList(LoginRequiredMixin, View):

    def get(self, request):
        gravity_forms = GravityFormsUtils().get_forms_list_for_front_page()
        return render(request, "gravity_forms.html", {'gravity_forms': gravity_forms})


class GravityFormView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        gravity_form = GravityFormsUtils().get_form(kwargs.get('pk'))
        return render(request, "gravity_form_view.html", {'gravity_form': gravity_form})
