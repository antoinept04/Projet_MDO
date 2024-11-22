from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('homepage')

        return view_func(request, *args, **kwargs)
    return wrapper_func

def staff_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('homepage')

        return view_func(request, *args, **kwargs)
    return wrapper_func
