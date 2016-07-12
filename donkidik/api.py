import models
import views
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
#TODO import db

@csrf_exempt
def signup(request):
	ret = {'status':'FAIL'}
	data = request.POST
	username = data['email']
	email = data['email']
	pw = data['password']
	name = data['name']
	new_user = User.objects.create_user(username=username, email=email, password=pw, first_name=name)
	if new_user:
		new_user.save()
		ret['status'] = 'OK'
		#attempt login
		login(request, new_user)
	return JsonResponse(ret)
@csrf_exempt
def login_req(request):
	ret = {'status':'FAIL', 'error':''}
	data = request.POST
	username = data['email']
	pw = data['password']
	user = authenticate(username=username, password=pw)
	if user is not None:
		if not user.is_active:
			ret['error'] = 'User account is not active'
		else:
			login(request, user)
			ret['status'] = 'OK'
	return JsonResponse(ret)
@csrf_exempt
def logout_req(request):
	logout(request)
	return HttpResponseRedirect('/')