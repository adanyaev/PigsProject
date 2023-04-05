from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required
def index(request):
	
	return render(request, 'main/index.html')


def login(request):
    
    return render(request, 'main/login.html')


def logout_view(request):
    logout(request)
    return redirect(login)


def register(request):

	return render(request, 'main/register.html')