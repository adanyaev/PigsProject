from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from main.models import *
import os
import json
import subprocess
import sys
import time


@csrf_exempt
def loginUser(request):
    #Django view function, that gets users credentials from POST json request and autentificate user with try catch

    if request.method == "POST" and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            rememberMe = data['rememberMe']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if not rememberMe:
                    request.session.set_expiry(0)
                return JsonResponse({'success': True, 'message': 'User authenticated successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid username or password'})
        except:
            return JsonResponse({'success': False, 'message': 'An error occurred while authenticating user'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def regUser(request):
    #Django view function, that gets username, password, email, name, surname from json request data and registers a new user with fields

    if request.method == "POST" and request.content_type == 'application/json':
       # parse json data from request
        data = json.loads(request.body)
        
        # extract required fields from data
        username = data['username']
        password = data['password']
        email = data['email']
        first_name = data['name']
        last_name = data['surname']
        
        # create new user instance and set fields values
        new_user = User.objects.create_user(username, email, password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        
        # save the user
        new_user.save()

        login(request, new_user)
        
        # create and return success response
        response_data = {
            'success': True,
            'message': 'User registered successfully'
        }
        
        return JsonResponse(response_data)
    
    # handle other request methods 
    else:
        response_data = {
            'success': False,
            'message': 'Only POST requests are allowed'
        }
        
        return JsonResponse(response_data, status=405)
    

@csrf_exempt
@login_required
def create_camera(request):
    if request.method == "POST" and request.content_type == 'application/json':
       # parse json data from request
        data = json.loads(request.body)
        
        # extract required fields from data
        url = data["url"]
        direction = data["direction"]
        line_place = data["line_place"]
        line_width = data["line_width"]
        model = data["model"]
        
        try:
            command = [sys.executable, r'./subprocess/pigEvaluator.py', '-c', url, '-d', direction, '--pig_detection_line_place', line_place, '--pig_detection_line_width', line_width, '--detection_model', './subprocess/best150']
            sf = subprocess.Popen(command)

        except:
            print("Не удалось создать камеру")

        new_camera = Camera.objects.create(
            url=url, direction=direction, line_place=line_place,
            line_width=line_width, model=model, pid=sf.pid
        )    
        new_camera.save()

        # create new user instance and set fields values
        # new_user = User.objects.create_user(username, email, password)
        # new_user.first_name = first_name
        # new_user.last_name = last_name
        
        # # save the user
        # new_user.save()

        # login(request, new_user)
        
        # create and return success response
        response_data = {
            'success': True,
            'message': 'Camera was added successfully'
        }
        
        return JsonResponse(response_data)
    
    # handle other request methods 
    else:
        response_data = {
            'success': False,
            'message': 'Only POST requests are allowed'
        }
        
        return JsonResponse(response_data, status=405)


@login_required
@csrf_exempt
def delete_camera(request):
    if request.method == "POST" and request.content_type == 'application/json':
       # parse json data from request
        data = json.loads(request.body)
        
        id = data["id"]
        print(Camera.objects.filter(id=id))
        print(Camera.objects.filter(id=id)[0].pid)
        
        #taskkill /PID <pid> /F
        os.system(f"taskkill /PID {Camera.objects.filter(id=id)[0].pid} /F")
        Camera.objects.filter(id=id).delete()

        response_data = {
            'success': True,
            'message': 'Camera was deleted successfully'
        }
        
        return JsonResponse(response_data)
    
    # handle other request methods 
    else:
        response_data = {
            'success': False,
            'message': 'Only POST requests are allowed'
        }
        
        return JsonResponse(response_data, status=405)


@login_required
@csrf_exempt
def edit_camera(request):
    if request.method == "POST" and request.content_type == 'application/json':
       # parse json data from request
        data = json.loads(request.body)
        
        id = data["id"]
        obj = Camera.objects.get(pk=id)
        os.system(f"taskkill /PID {Camera.objects.get(pk=id).pid} /F")
        obj.url = data['url']
        obj.direction = data['direction']
        obj.line_place = data["line_place"]
        obj.line_width = data["line_width"]
        obj.model = data["model"]
        
        
        try:
            command = [sys.executable, r'./subprocess/pigEvaluator.py', '-c', obj.url, '-d', obj.direction, '--pig_detection_line_place', obj.line_place, '--pig_detection_line_width', obj.line_width, '--detection_model', './subprocess/best150']
            sf = subprocess.Popen(command)
            obj.pid = sf.pid
        except:
            print("Не удалось создать камеру")
        obj.save()


        response_data = {
            'success': True,
            'message': 'Camera was edited successfully'
        }
        
        return JsonResponse(response_data)
    
    # handle other request methods 
    else:
        response_data = {
            'success': False,
            'message': 'Only POST requests are allowed'
        }
        
        return JsonResponse(response_data, status=405)
