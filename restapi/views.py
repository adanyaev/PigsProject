from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import json
from main.models import *
from .serializers import CamerasSerializer
from django.contrib.auth import login, authenticate
from django.contrib.auth import authenticate, login
from django.core.files.base import ContentFile
from main.models import *
from django.views.decorators.csrf import csrf_exempt
import json
import subprocess
import sys
import cv2
import os


# Create your views here.
class RegisterUserApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
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

            ext_user = ExtendedUser(user=new_user)
            if 'patronymic' in data:
                ext_user.patronymic = data['patronymic']
            ext_user.save()

            login(request, new_user)
            
            # create and return success response
            response_data = {
                'success': True,
                'message': 'Пользователь успешно зарегистрирован'
            }
            
            return Response(response_data)

        except Exception as exc:
            return Response({'success': False, 'message': "Такой пользователь уже существует"})


class LoginUserApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
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
                return Response({'success': True, 'message': 'Пользователь успешно авторизован'})
            else:
                return Response({'success': False, 'message': 'Неверное имя пользователя или пароль'})
        except Exception as exc:
            return Response({'success': False, 'message': str(exc)})


class CameraListApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        objects = request.user.origin_user.camera_set.all()
        serializer = CamerasSerializer(objects, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        
        # extract required fields from data
        name = data['name']
        url = data["url"]
        model = data["model"]

        new_camera = Camera.objects.create(
            url=url, model=model, user=request.user.origin_user, name=name
        )
        new_camera.status = 0
        new_camera.save()

        try:
            cap = cv2.VideoCapture(new_camera.url)
            ret, frame = cap.read()
            if not ret:
                raise Exception("Cannot read stream")
            ret, buf = cv2.imencode('.jpg', frame)
            if not ret:
                raise Exception("Cannot read stream")
            content = ContentFile(buf.tobytes())
            new_camera.sample_image.save('sample_image_{}.jpg'.format(new_camera.id), content)

        except:
            response_data = {
            'success': False,
            'message': 'Error reading from videostream'
            }
            
            return Response(response_data, status=400)

        # create and return success response
        response_data = {
            'success': True,
            'message': 'Camera was added successfully',
            'cam_id': new_camera.id
        }
        
        return Response(response_data)


class CameraDetailApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        try:
            object = Camera.objects.get(id=id)
            serializer = CamerasSerializer(object)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as exc:
            return Response({"error": str(exc)})

    def put(self, request, id, *args, **kwargs):
        try:
            obj = Camera.objects.get(id=id)
        except:
            return Response({"error": "Такой камеры не существует"})

        data = request.data
        os.system(f"taskkill /PID {Camera.objects.get(pk=id).pid} /F")
        obj.url = data['url']
        obj.model = data["model"]
        obj.name = data["name"]
        
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
        
        return Response(response_data)

    def delete(self, request, id, *args, **kwargs):
        try:
            obj = Camera.objects.get(id=id)
        except:
            raise Response({"error": "Такой камеры не существует"})

        os.system(f"taskkill /PID {Camera.objects.filter(id=id)[0].pid} /F")
        obj.delete()

        response_data = {
            'success': True,
            'message': 'Камера успешно удалена'
        }
        
        return Response(response_data)


class LineSettingsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        id = data['camId']

        try:
            cam = request.user.origin_user.camera_set.get(id=id)
        except Exception as exc:
            response_data = {
                'success': False,
                'message': 'Такой камеры не существует'
            }
            return Response(response_data, status=405)
        
        lineDirection = int(data['lineDirection'])
        lineWidth = int(data['lineWidth'])
        linePlace = float(data['linePlace'])
        if not 1 <= lineWidth <= 640 or not 0.01 <= linePlace <= 0.99 or not 1 <= lineDirection <= 4:
            response_data = {
                'success': False,
                'message': 'Проверьте валидность параметров'
            }
        
            return Response(response_data, status=400)

        id2direction = {1: 'Up', 2: 'Down', 3: 'Left', 4: 'Right'}
        cam.direction = id2direction[lineDirection]
        cam.line_width = lineWidth
        cam.line_place = linePlace
        cam.status = 1
        cam.save()

        response_data = {
            'success': True,
            'message': 'Параметры камеры обновлены успешно!'
        }
        
        return Response(response_data)


class ResetCounterApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        try:
            cam = request.user.origin_user.camera_set.get(id=id)
            cam.current_counter = 0
            cam.save()
        except Exception as exc:
            response_data = {
                'success': False,
                'message': 'Такой камеры не существует'
            }
            return Response(response_data, status=405)
        
        response_data = {
            'success': True,
            'message': 'Значение счетчика установлено в 0'
        }
        return Response(response_data)


class GetCounterApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        try:
            cam = request.user.origin_user.camera_set.get(id=id)
        except Exception as exc:
            response_data = {
                'success': False,
                'message': 'Такой камеры не существует'
            }
            return Response(response_data, status=405)
        
        response_data = {
            'success': True,
            'counter': cam.current_counter,
            'message': 'Значение счетчика получено'
        }
        return Response(response_data)

