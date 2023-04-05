from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


def index(request):
	
	return redirect(login)

def login(request):
    
    context = {"page_name": "Authorization Page"}
    return render(request, 'main/login.html', context=context)

def register(request):

	context = {"page_name": "Registration Page"}
	return render(request, 'main/register.html', context=context)

def cameras(request):

	if request.method == "POST":
		url = request.POST["url"]
		direction = request.POST["direction"]
		line_place = request.POST["line_place"]
		line_width = request.POST["line_width"]
		model = request.POST["model"]

		

	context = {"page_name": "Connected cameras"}
	return render(request, 'main/cameras.html', context=context)

