import random
from django.conf import settings
from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404,JsonResponse,HttpResponseRedirect
from .models import Tweet
from .forms import TweetForm
from .serializers import TweetSerializer,TweetActionSerializer,TweetCreateSerializer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated

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
    print(request.user)
    return render(request, "pages/home.html",context={},status=200)

@api_view(['POST'])
# authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def tweet_create_view(request,*args,**kwargs):
    data = request.POST or None
    serializer = TweetCreateSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data,status=201)
        
    return Response({},status=400)

@api_view(['GET'])

def tweet_detail_view(request,tweet_id,*args,**kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({},status=404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    
    return Response(serializer.data,status=200)

@api_view(['DELETE','POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request,tweet_id,*args,**kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({},status=404)
    qs = qs.filter(user=request.user)
    if not qs.exists():
        return Response({"message":"You cannot delete this tweet"},status=401)
    obj = qs.first()
    obj.delete()
    
    return Response({"message":"Tweet removed"},status=200) 


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request,*args,**kwargs):
    ''''
    id is required
    Actions are like, unlike, retweet
    '''
    serializer = TweetActionSerializer(data = request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get("id")
        action = data.get("action")
        content = data.get("content")
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({},status=404)
    obj = qs.first()
    if action == "like":
        obj.likes.add(request.user)
        serializer = TweetSerializer(obj)
        return Response(serializer.data,status=200)   

    elif action == "unlike":
        obj.likes.remove(request.user)
        serializer = TweetSerializer(obj)
        return Response(serializer.data,status=200)
    elif action == "retweet":
        
        new_tweet = Tweet.objects.create(user=request.user,parent=obj,content=content)
        serializer = TweetSerializer(new_tweet)
        return Response(serializer.data,status=201) 
    return Response({},status=200)   


@api_view(['GET'])

def tweet_list_view(request,*args,**kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs,many=True)
    
    return Response(serializer.data)


def tweet_create_view_pure_django(request,*args,**kwargs):
    '''
    REST API Create View -> DRF
    '''
    # Check if the request is AJAX
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if is_ajax:
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)

    # ***********************************************************
    #  # Check if the request is AJAX
    # is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    #************************************************************
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next") or None
    
    if form.is_valid():
        
        obj = form.save(commit=False)
        obj.user = user
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

def tweet_list_view_pure_django(request,*args,**kwargs):
    qs = Tweet.objects.all()
    tweets_list = [x.serialize() for x in qs]

    data = {
        "isUser":False,
        "response": tweets_list
    }
    return JsonResponse(data)

def tweet_detail_view_pure_django(request,tweet_id,*args,**kwargs):
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