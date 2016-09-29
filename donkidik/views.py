from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from donkidik.models import *
from django.contrib.auth.models import User

@login_required
def posts(request):
	return HttpResponse("this is the posts")

def index(request):
	context = {}
	return render(request, 'index.html',context)

@login_required
def home(request):
	return render(request, 'home.html')

@login_required
def userProfile(request,uid):
	uid = int(uid)
	own_profile = False
	if request.user.pk == uid:
		own_profile = True
	user = User.objects.filter(pk=uid)
	if not user:
		print "User ID %s not found" %uid
	userP = user[0].profile
	if not userP:
		print "User %s has no profile" %uid

	context = userP.jsonify()
	context['uid'] = uid
	if own_profile:
		context['own'] = True
	#return JsonResponse(context)
	return render(request, 'profile.html', context)

def gal1(request):
	return HttpResponse("<h1>gal1</h1>")

def gal2(request):
	return HttpResponse("<h1>gal2</h1>",status = 500)

def gal3(request):
	return HttpResponseRedirect('/gal/1/')