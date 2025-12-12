from django.shortcuts import render
from django.views.generic import View


class HomePageView(View):
    template_name = "frontend/pages/home.html"

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)
