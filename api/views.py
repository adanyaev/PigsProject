from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from main.models import *
import os
import json


@csrf_exempt
def loginUser(request):
    #Django view function, that gets users credentials from POST json request and autentificate user with try catch

    if request.method == "POST" and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
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