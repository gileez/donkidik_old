from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from donkidik import models
@login_required
def posts(request):
	return HttpResponse("this is the posts")

def index(request):
	context = {}
	return render(request, 'index.html',context)
@login_required
def home(request):
	posts = models.Post.objects.all()
	context={'posts':[]}
	for p in posts:
		context['posts'].append({	'author': p.author.username,
									'text':p.text,
									'post_type': p.post_type
								})
	return render(request, 'home.html',context)

def gal1(request):
	return HttpResponse("<h1>gal1</h1>")

def gal2(request):
	return HttpResponse("<h1>gal2</h1>",status = 500)

def gal3(request):
	return HttpResponseRedirect('/gal/1/')