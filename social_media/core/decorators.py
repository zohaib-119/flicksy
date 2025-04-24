from django.shortcuts import redirect

def redirect_authenticated_user(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper
