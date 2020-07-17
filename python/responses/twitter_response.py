import requests
from requests.exceptions import HTTPError
from requests_oauthlib import OAuth1
import tweepy

class TwitterResponse():
    def __init__(self, consumer_key, consumer_secret, api_token, api_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_token = api_token
        self.api_secret = api_secret
    

    def get_follower_list(self, user_name):
        cursor = -1
        follower_url = "https://api.twitter.com/1.1/followers/list.json?count=200&skip_status=true&include_user_entities=false&screen_name="+user_name+"&cursor="+str(cursor)
        auth = OAuth1(self.consumer_key, self.consumer_secret,
                        self.api_token, self.api_secret)

        twitter_response = requests.get(url=follower_url, auth=auth)
        
        if twitter_response.status_code == 429:
            return None
        
        followers_list = []

        followers_list = [user for user in twitter_response.json()["users"]]

        if twitter_response.json()["next_cursor"] == 0:
            return followers_list

        while twitter_response.json()["next_cursor"] != 0:
            follower_url = "https://api.twitter.com/1.1/followers/list.json?count=200&skip_status=true&include_user_entities=false&screen_name="+user_name+"&cursor="+twitter_response.json()["next_cursor_str"]
            twitter_response = requests.get(url=follower_url, auth=auth)
            if twitter_response.status_code == 429:
                return followers_list
            loop_list = [user for user in twitter_response.json()["users"]]
            followers_list.extend(loop_list)

        return followers_list
    
    def filter_followers(self, api_response):
        follower_list = api_response
        new_follower_list = []

        for follower in follower_list:
            follower_dict = {}
            follower_dict["id"] = follower["id"]
            follower_dict["name"] = follower["name"]
            follower_dict["screen_name"] = follower["screen_name"]
            new_follower_list.append(follower_dict)

        return new_follower_list

class TweepyAgent():
    def __init__(self, consumer_key, consumer_secret, api_token, api_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(api_token, api_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)


    def get_last_followers(self, user_name):
        user = self.api.get_user(user_name)
        followers_list = [{"follower_id": follower.id, "follower_name": follower.name, 'follower_screen_name': follower.screen_name} for follower in user.followers()]
        # for follower in user.followers():
        #     print(follower.id)
        #     print(follower.screen_name)
        return followers_list

    
    def get_followers_count(self, user_name):
        user = self.api.get_user(user_name)
        return user.followers_count
