from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import HttpResponse
import json


class HomePageView(TemplateView):

    template_name = "show.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['loggedin'] = True
        return context