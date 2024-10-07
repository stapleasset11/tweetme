import random
from django.conf import settings
from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404,JsonResponse,HttpResponseRedirect
from .models import Tweet
from .forms import TweetForm

ALLOWED_HOSTS = settings.ALLOWED_HOSTS


#Custom 'is_safe_url' function
from urllib.parse import urlparse

def is_safe_url(url, allowed_hosts=None, require_https=False):
    if not url:
        return False
    # You can customize allowed_hosts and require_https based on your needs
    parsed_url = urlparse(url)
    if require_https and parsed_url.scheme != 'https':
        return False
    return not parsed_url.netloc or parsed_url.netloc in allowed_hosts



# Create your views here.
def home_view(request,*args,**kwargs):
    return render(request, "pages/home.html",context={},status=200)

def tweet_create_view(request,*args,**kwargs):

    # ***********************************************************
     # Check if the request is AJAX
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    #************************************************************
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next") or None
    
    if form.is_valid():
        
        obj = form.save(commit=False)
        obj.save()
        if is_ajax:
            return JsonResponse(obj.serialize(),status=201)
        if next_url != None and is_safe_url(next_url,ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()

    if form.errors:
        if is_ajax:
            return JsonResponse(form.errors,status=400)
    
    return render(request,'components/form.html',context={"form":form}) 

def tweet_list_view(request,*args,**kwargs):
    qs = Tweet.objects.all()
    tweets_list = [x.serialize() for x in qs]

    data = {
        "isUser":False,
        "response": tweets_list
    }
    return JsonResponse(data)

def tweet_detail_view(request,tweet_id,*args,**kwargs):
    """
    REST API VIEW
    Consume by javascript or others
    Return Json data
    """
    data = {
       "id":tweet_id,
       
    }
    status = 200
    try:
        obj = Tweet.objects.get(id=tweet_id)
        data["content"] = obj.content
    except:
        data['message'] = "Not Found"
        status = 404

    
    return JsonResponse(data,status=status)