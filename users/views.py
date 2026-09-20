from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from .factories import UserFactory
from .forms import UserRegistrationForm


class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("artists:artist-list")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        UserFactory.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            role=form.cleaned_data["role"],
        )

        return super().form_valid(form)
   

class UserLoginView(LoginView):
    template_name = "users/login.html"


class UserLogoutView(LogoutView):
    pass