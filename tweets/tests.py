from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Tweet
# Create your tests here.
User = get_user_model()
class TweetTestCase(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(username='abc',password='abcpass')

    def test_user_created(self):
        user = User.objects.get(username="abc")
        self.assertEqual(user.username,"abc")