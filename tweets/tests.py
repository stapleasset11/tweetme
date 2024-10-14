from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
from .models import Tweet
# Create your tests here.
User = get_user_model()
class TweetTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='admin',password='Sakawa123')
        Tweet.objects.create(content="my app is coming along nicely guys!!!",user = self.user)
        Tweet.objects.create(content="my app is coming along nicely guys!!!",user = self.user)
        Tweet.objects.create(content="my app is coming along nicely guys!!!",user = self.user)

        self.currentCount = Tweet.objects.all().count()

    def test_tweet_created(self):
        tweet_obj = Tweet.objects.create(content="maximum effort",user = self.user)
        self.assertEqual(tweet_obj.id,4)
        self.assertEqual(tweet_obj.user,self.user)
    
    def get_client(self):
        client = APIClient()
        client.login(username=self.user.username, password='Sakawa123')
        return client
    
    def test_api_login(self):
        client = self.get_client()
        response = client.get("/api/tweets/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()),3)

    def test_tweet_list(self):
        client = self.get_client()
        response = client.get("/api/tweets/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()),3)

    def test_action_likes(self):
        client = self.get_client()
        response = client.post("/api/tweets/action/",{"id":1,"action":"like"})
        self.assertEqual(response.status_code,200)
        like_count = response.json().get("likes")
        self.assertEqual(like_count,1)
        

    def test_action_unlike(self):
        client = self.get_client()
        response = client.post("/api/tweets/action/",{"id":2,"action":"like"})
        self.assertEqual(response.status_code,200)
        response = client.post("/api/tweets/action/",{"id":2,"action":"unlike"})

        self.assertEqual(response.status_code,200)
        like_count = response.json().get("likes")
        self.assertEqual(like_count,0)

    def test_action_retweet(self):
        client = self.get_client()
        # current_count = self.currentCount
        response = client.post("/api/tweets/action/",{"id":2,"action":"retweet"})
        self.assertEqual(response.status_code,201)
        data = response.json()
        new_tweet_id = data.get("id")
        self.assertNotEqual(2,new_tweet_id) 
        self.assertEqual(self.currentCount +1,new_tweet_id)

    def test_tweet_create_api_view(self):
        request_data = {"content":"This is nothing more than a test tweet!!"}
        client = self.get_client()
        response = client.post("/api/tweets/create/",request_data)
        self.assertEqual(response.status_code,201)
        response_data = response.json()
        new_tweet_id = response_data.get("id") 
        self.assertEqual(self.currentCount +1,new_tweet_id)

    def test_tweet_detail_api_view(self):
        client = self.get_client()
        response = client.get("/api/tweets/2/")
        self.assertEqual(response.status_code,200)
        data = response.json()
        _id = data.get("id")
        self.assertEqual(_id,2)


    def test_tweet_delete_api_view(self):
        client = self.get_client()
        response = client.delete("/api/tweets/2/delete/")
        self.assertEqual(response.status_code,200)

        response = client.delete("/api/tweets/2/delete/")
        self.assertEqual(response.status_code,404)
        

