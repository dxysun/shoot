# from django.shortcuts import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
from django.shortcuts import render


class SimpleMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # if request.session.get('user', None):
        #     pass
        # else:
        #     return redirect("login")
        if request.path != '/shoot/login' and request.path != '/shoot/login_admin':
            if request.session.get('user', None):
                pass
            else:
                return redirect("login")


