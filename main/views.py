from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
from main.models import *

import main.video_stream as vs


@login_required
def index(request):
	
	context = {"page_name": "Main Page"}
	return render(request, 'main/index.html', context=context)


def login(request):
    
    context = {"page_name": "Authorization Page"}
    return render(request, 'main/login.html', context=context)


def register(request):

	context = {"page_name": "Registration Page"}
	return render(request, 'main/register.html', context=context)


def logout_view(request):
    logout(request)
    return redirect(login)


@login_required
def cameras(request):
	cameras = Camera.objects.all()
	if cameras:
		cameras_cont = cameras.order_by('id')[::-1]
	else:
		cameras_cont = []
	context = {
			"page_name": "Connected cameras",
			"cameras": cameras_cont
		}
	return render(request, 'main/cameras.html', context=context)


@login_required
def camera(request, id):
	
	context = {
		"page_name": "Camera page",
		"object": Camera.objects.get(pk=id)
	}
	return render(request, 'main/camera.html', context=context)


@login_required
@gzip.gzip_page
def live_stream(request, id):
	try:
		cam_obj = Camera.objects.get(pk=id)

		cam = vs.VideoCamera(id, cam_obj.line_width, cam_obj.line_place, cam_obj.direction)
		return StreamingHttpResponse(vs.gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
	except:  
		print("Error in streaming video")


@login_required
def setLineSettings(request, id):

	context = {
		"page_name": "Настройка линии детекции",
		"cam_id": id
	}
	return render(request, 'main/setLineSettings.html', context=context)