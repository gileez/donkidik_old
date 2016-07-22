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
			posts = Post.objects.filter(author=request.user, date__range=(today_min, today_max))
			print "total posts %d" %len(posts)
			if len(posts) > 2:
				ret['error'] = "You have exceeded your post limit for today"
				return JsonResponse(ret)
		data = request.POST
		uid = int(request.user.id)
		post_type = int(data.get('post_type'))
		p = Post.objects.create(author_id=uid, text=data.get('text'), post_type_id=post_type, date=datetime.datetime.now())
		p.save()
		if data['type_name'] == 'General':
			ret = {'status':'OK'}
		elif data['type_name'] == 'Report':
			spot_name = data['spot_name']
			spot = Spot.objects.filter(name=spot_name)[0]
			if not spot:
				ret['error']="Spot not found"
			else:
				knots = data['knots']
				p_meta = PostMeta.objects.create(post=p,knots=knots,spot=spot)
				#p_meta.save() 
				ret = {'status':'OK'}
	return JsonResponse(ret)

@csrf_exempt
@login_required
def remove_post(request, pid):
	ret = {'status':'FAIL'}
	p = Post.object.get(id=pid)
	if not p:
		ret['error'] = 'Post not found'
		return JsonResponse(ret)
	# TODO check for special deletion permissions
	if p.user.id != request.user.id:
		ret['error'] = 'Attempting to delete OPP'
		return JsonResponse(ret)
	if p.delete():
		ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def update_post(request, pid):
	ret = {'status':'FAIL'}
	p = Post.object.filter(id=pid)
	#make sure this post belongs to this user
	if not p:
		ret['error'] = "Post not found"
		return JsonResponse(ret)
	if p.user.id != request.user.id:
		ret['error'] = "Attempt to edit OPP"
		return JsonResponse(ret)
	if p:
		p.text = request.POST['text']
		p.date = timezone.now()
		p.save()
		ret['status'] = 'OK'
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
		for p in reversed(posts):
			ret['data'].append(p.jsonify())
	return JsonResponse(ret)


@csrf_exempt
@login_required
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
@login_required
def get_spots(request):
	ret = {'status':'OK', 'data':[]}
	spots = Spot.objects.all()
	for s in spots:
		ret['data'].append({
								'id': s.id,
								'name': s.name
							})
	return JsonResponse(ret)

@csrf_exempt
@login_required
def follow(request, uid):
	ret = {'status':'FAIL'}
	to_follow = User.objects.filter(id=uid)[0]
	if not to_follow:
		ret['error'] = "Unable to find user to follow"
		return JsonResponse(ret)
	# check these two aren't already coupled
	if request.user.profile.follows.filter(user_id=uid).count() > 0:
		# already following
		ret['error'] = "Made a follow request on someone you're already following"
		return JsonResponse(ret)
	UserProfile.objects.filter(user=request.user)[0].follows.add(to_follow.profile)
	ret['status']=['OK']
	return JsonResponse(ret)

@csrf_exempt
@login_required
def unfollow(request, uid):
	ret = {'status':'FAIL'}
	to_unfollow = User.objects.filter(id=uid)[0]
	if not to_unfollow:
		ret['error'] = "Unable to find user to follow"
		return JsonResponse(ret)
	# check these two are already coupled
	if not request.user.profile.follows.filter(user_id=uid):
		# not following...can't unfollow
		ret['error'] = "Cant unfollow someone you're not following"
		return JsonResponse(ret)
	UserProfile.objects.filter(user=request.user)[0].follows.remove(to_unfollow.profile)
	ret['status']=['OK']
	return JsonResponse(ret)

@csrf_exempt
@login_required
def post_upvote(request, pid):
	ret = {'status': 'FAIL'}
	# TODO:
	# make sure user has upvote permissions
	p = Post.objects.filter(id=pid)[0]
	if not p:
		ret['error'] = 'post not found'
		return JsonResponse(ret)
	if p.votes.filter(user=request.user):
		ret['error'] = 'user already upvoted this post'
		return JsonResponse(ret)
	# upvote this post
	p.upvote(request.user)
	# get upvote score - how many credits do we need to add based on who is making the vote
	# call function to upvote this user
	p.user.upvote()
	# save changes - TODO: find out if this is necessary
	p.user.save()
	p.save()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def post_downvote(request, pid):
	ret = {'status': 'FAIL'}
	p = Post.objects.filter(id=pid)[0]
	if not p:
		ret['error'] = 'post not found'
		return JsonResponse(ret)
	if not p.votes.filter(user=request.user):
		ret['error'] = 'user didnt upvote this post'
		return JsonResponse(ret)
	# upvote this post
	p.downvote(request.user)
	# TODO
	# get downvote score - how many credits do we need to add based on who is making the vote
	# call function to downvote this user
	p.user.downvote()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def create_forecast(request):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to create
	
	return JsonResponse(ret)