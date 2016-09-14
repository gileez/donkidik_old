from models import *
import views
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
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
		print "post type is %s" %data.get('post_type')
		post_type = int(data.get('post_type'))
		p = Post.objects.create(author_id=uid, text=data.get('text'), post_type_id=post_type, date=datetime.datetime.now())
		p.save()
		if data['type_name'] == 'General':
			ret = {'status':'OK'}
		elif data['type_name'] == 'Report':
			spot_name = data['spot_name']
			print "spot name is: %s" %spot_name 
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
	pid = int(pid)
	ret = {'status':'FAIL'}
	p = Post.objects.get(id=pid)
	if not p:
		ret['error'] = 'Post not found'
		return JsonResponse(ret)
	# TODO check for special deletion permissions
	print p.author.id
	print request.user.id
	if ( p.author.id != request.user.id ) and not request.user.is_superuser:
		ret['error'] = 'Attempting to delete OPP'
		return JsonResponse(ret)
	if p.delete():
		ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def update_post(request, pid):
	ret = {'status':'FAIL'}
	p = Post.objects.filter(id=pid)
	#make sure this post belongs to this user
	if not p:
		ret['error'] = "Post not found"
		return JsonResponse(ret)
	if p.author.id != request.user.id:
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
		posts = Post.objects.all().order_by('modified')
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
def get_followers(request, uid):
	ret = {'status': 'FAIL'}
	u = User.objects.get(id=uid)
	if not u:
		ret['error'] = 'Could not find user'
		return JsonResponse(ret)
	followers = u.profile.followed_by
	ret['followers'] = []
	for f in followers:
		ret['followers'] += f.jsonify()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def post_upvote(request, pid):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has upvote permissions
	pid = int(pid)
	p = Post.objects.filter(id=pid)[0]
	if not p:
		ret['error'] = 'post not found'
		return JsonResponse(ret)
	# upvote this post
	ret['change_score'] = 1 if p.upvote(request.user) else -1
	# get upvote score - how many credits do we need to add based on who is making the vote
	# call function to upvote this user
	#p.author.upvote()
	# save changes - TODO: find out if this is necessary
	#p.author.save()
	p.save()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def post_downvote(request, pid):
	ret = {'status': 'FAIL'}
	pid = int(pid)
	p = Post.objects.filter(id=pid)[0]
	if not p:
		ret['error'] = 'post not found'
		return JsonResponse(ret)
	# upvote this post
	ret['change_score'] = -1 if p.downvote(request.user) else 1
	p.save()
	# TODO
	# get downvote score - how many credits do we need to add based on who is making the vote
	# call function to downvote this user
	#p.author.downvote()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def create_forecast(request):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to create a forecast
	spots = request.POST['spots']
	for t in ['text','knots','gust']:
		if request.POST.get(t,None):
			params[t] = request.POST[t]
	f_date = datetime.datetime(request.POST['date'][0], request.POST['date'][1], request.POST['date'][2])
	# TODO generate session - logic + implementation
	f = Forecast.objects.create(user=request.user, f_date=f_date, **params)
	# add spots to forecast - is there a way to do this within constructor?
	spot_records = Spot.objects.filter(pk__in=spots)
	if not spot_record:
		ret['error'] = 'Spot ids %s not found' %spots
		return JsonResponse(ret)
	f.spots.add(spot_record)
	f.save()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def update_forecast(request, fid):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to create a forecast
	f = Forecast.objects.get(pk=fid)
	if not f:
		ret['error'] = 'Forecast not found'
		return JsonResponse(ret)
	if f.user.pk != request.user.pk:
		ret['error'] = "Attempting to change someone else's forecast"
		return JsonResponse(ret)
	for t in ['text','knots','gusts']:
		if request.POST.get(t,None):
			setattr(f, t, request.POST[t])
	# TODO what are the implications on sessions?
	f.save()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def remove_forecast(request, fid):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to create a forecast
	f = Forecast.objects.get(pk=fid)
	if not f:
		ret['error'] = 'Forecast not found'
		return JsonResponse(ret)
	if f.user.pk != request.user.pk:
		ret['error'] = "Attempting to change someone else's forecast"
		return JsonResponse(ret)
	f.delete()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def create_session(request):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to create a session
	# make sure there isn't a session going on
	spot_id = request.POST['spot_id']
	date = datetime.datetime(request.POST['date'][0], request.POST['date'][1], request.POST['date'][2])
	s = Session.objects.get(spot__pk=spot_id, date=date)
	if s:
		ret['error'] = 'A session already exists for this date and spot'
		ret['session_id'] = s.pk
		return JsonResponse(ret)
	spot = Spot.objects.get(pk=spot_id)
	if not spot:
		ret['error'] = 'Spot not found'
		return JsonResponse(ret)
	s = Session.objects.create(owner=request.user, spot=spot, date=date)
	s.users.add(request.user)
	s.save()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def remove_session(request, session_id):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to remove a session
	s = Session.objects.get(pk=session_id)
	if not s:
		ret['error'] = 'Session not found'
		return JsonResponse(ret)
	if s.user.pk != request.user.pk:
		ret['error'] = "Attempting to change someone else's forecast"
		return JsonResponse(ret)
	s.delete()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def join_session(request, session_id):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to join this session
	s = Session.objects.get(pk=session_id)
	if not s:
		ret['error'] = 'Session not found'
		return JsonResponse(ret)
	s.users.add(request.user)
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def leave_session(request, session_id):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to join this session
	s = Session.objects.get(pk=session_id)
	if not s:
		ret['error'] = 'Session not found'
		return JsonResponse(ret)
	s.users.remove(request.user)
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def add_comment(request, pid):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to comment
	text = request.POST['text']
	if not text:
		ret['error'] = 'Comment must have text'
		return JsonResponse(ret)
	p = Post.objects.get(pk=pid)
	if not p:
		ret['error'] = 'Post not found'
		return JsonResponse(ret)
	c = Comment.objects.create(user=request.user,date=timezone.now(), text=text)
	c.save()
	p.comments.add(c)
	p.modified = timezone.now()
	p.save()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def remove_comment(request, cid):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to comment
	c = Comment.objects.get(pk=cid)
	if not c:
		ret['error'] = 'Comment not found'
		return JsonResponse(ret)
	if c.user != request.user:
		ret['error'] = 'Attempt to remove comment that isnt yours'
		return JsonResponse(ret)
	c.delete()
	ret['status'] = 'OK'
	return JsonResponse(ret)

@csrf_exempt
@login_required
def update_comment(request, cid):
	ret = {'status': 'FAIL'}
	# TODO: make sure user has proper permissions to comment
	c = Comment.objects.get(pk=cid)
	if not c:
		ret['error'] = 'Comment not found'
		return JsonResponse(ret)
	if c.user != request.user:
		ret['error'] = 'Attempt to remove comment that isnt yours'
		return JsonResponse(ret)
	c.text = request.POST.get('text')
	c.date = timezone.now()
	c.save()
	ret['status'] = 'OK'
	return JsonResponse(ret)