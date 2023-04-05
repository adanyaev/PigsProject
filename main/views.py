from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main.models import *


def index(request):
	
	return redirect(login)

def login(request):
    
    context = {"page_name": "Authorization Page"}
    return render(request, 'main/login.html', context=context)

def register(request):

	context = {"page_name": "Registration Page"}
	return render(request, 'main/register.html', context=context)

def logout_view(request):
    logout(request)
    return redirect(login)

def cameras(request):
	context = {
		"page_name": "Connected cameras",
		"cameras": Camera.objects.all().order_by('id')[::-1]
	}
	return render(request, 'main/cameras.html', context=context)
