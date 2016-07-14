from models import *
import views
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import JsonResponse
from django.utils import timezone
import json, datetime
#TODO import db

@csrf_exempt
def signup(request):
	ret = {'status':'FAIL'}
	data = request.POST
	username = data['email']
	email = data['email']
	pw = data['password']
	name = data['name']
	if User.objects.create_user(username=username, email=email, password=pw, first_name=name):
		#attempt login
		user = authenticate(username=username,password=pw)
		if user is not None:
			if user.is_active:
				ret['status'] = 'OK'
				login(request, user)
			else:
				ret['error'] = 'failed to make user active'
		else:
			# a very weird case where you managed to add the user but failed on the authentication
			ret['error'] = 'crazy auth issue'
			pass
	ret['error'] = 'failed to create new user'
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

def user_posts(request,uid):
	print "welcome user_posts %s" %uid
	posts = Post.objects.filter(author=uid)
	for p in posts:
		print p
	data = serializers.serialize('json', Post.objects.filter(author=uid), fields=('text','author'))
	ret = {'status':'OK',
			'data':data
			}
	return JsonResponse(ret)
@csrf_exempt
def create_post(request):
	ret = {'status':'FAIL'}
	if not request.user.is_authenticated():
		ret['error'] = "User is not logged in"
		return JsonResponse(ret)

	else:
		# make sure user isn't abusing the system
		if not request.user.is_staff:
			print "not staff"
			today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
			today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
			posts = Post.objects.filter(author=request.user, published_date__range=(today_min, today_max))
			print "total posts %d" %len(posts)
			if len(posts) > 2:
				ret['error'] = "You have exceeded your post limit for today"
				return JsonResponse(ret)
		data = request.POST
		uid = int(request.user.id)
		post_type = int(data.get('post_type'))
		p = Post.objects.create(author_id=uid, text=data.get('text'), post_type_id=post_type, published_date=datetime.datetime.now())
		p.save()
		ret = {'status':'OK'}
	return JsonResponse(ret)


@csrf_exempt
def get_posts(request):
	# gets all posts and returns them via ret['data']
	ret = {'status':'OK'}
	if not request.user.is_authenticated():
		ret['error'] = "User is not logged in"
		return JsonResponse(ret)
	else:
		ret['data'] = []
		posts = Post.objects.all()
		for p in posts:
			ret['data'].append(p.jsonify())
	return JsonResponse(ret)


@csrf_exempt
def get_post_types(request):
	ret = {'status':'OK', 'data':[]}
	types = PostType.objects.all()
	for t in types:
		ret['data'].append({
								'id': t.id,
								'name': t.name
							})
	return JsonResponse(ret)

@csrf_exempt
def follow(request):
	ret = {'status':'FAIL'}
	# check these two aren't already coupled
	return