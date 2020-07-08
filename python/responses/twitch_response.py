import requests
from requests.exceptions import HTTPError


class TwitchResponse():
    def __init__(self, streams_user_id, client_id, client_secret):
        self.streams_user_id = streams_user_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.bearer_token = ""
        self.url_games = "https://api.twitch.tv/helix/games?id="
        self.url_tags = "https://api.twitch.tv/helix/tags/streams?"
        self.url_followers = "https://api.twitch.tv/helix/users/follows?to_id="+streams_user_id
        self.url_streams = "https://api.twitch.tv/helix/streams?user_id="+streams_user_id
        self.url_streamer_videos = "https://api.twitch.tv/helix/videos?user_id="+streams_user_id
        self.url_oauth2 = "https://id.twitch.tv/oauth2/token?client_id="+client_id+"&client_secret="+client_secret+"&grant_type=client_credentials"
        self.authenticate()


    def authenticate(self):
        try:
            response = requests.post(url=self.url_oauth2)
            response.raise_for_status()
            self.bearer_token = response.json()["access_token"]
            return self.bearer_token
        except requests.exceptions.HTTPError as err:
            print(err)
            return None


    def response_http_get(self,url):
        request_headers = {'Authorization': 'Bearer ' + self.bearer_token, 'client-id': self.client_id}
        return requests.get(url=url, headers=request_headers)
         

    def get_followers(self):
        try:
            response = self.response_http_get(self.url_followers)
            if (response.status_code == 401):
                self.bearer_token = self.authenticate()
                response = self.response_http_get(self.url_followers)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(err)
            return None

    
    def get_videos(self):
        try:
            response = self.response_http_get(self.url_streamer_videos)
            if (response.status_code == 401):
                self.bearer_token = self.authenticate()
                response = self.response_http_get(self.url_streamer_videos)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(err)
            return None

    
    def get_stream(self):
        try:
            response = self.response_http_get(self.url_streams)
            if (response.status_code == 401):
                self.bearer_token = self.authenticate()
                response = self.response_http_get(self.url_streams)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(err)
            return None        


    def get_game(self, game_id):
        try:
            response = self.response_http_get(self.url_games+game_id)
            if (response.status_code == 401):
                self.bearer_token = self.authenticate()
                response = self.response_http_get(self.url_games+game_id)

            response.raise_for_status()
            return response.json()["data"][0]
        except requests.exceptions.HTTPError as err:
            print(err)
            return None 


    def get_tags(self, tags):
        query_params = "tag_id="+"&tag_id=".join(tags)
        try:
            response = self.response_http_get(self.url_tags+query_params)
            if (response.status_code == 401):
                self.bearer_token = self.authenticate()
                response = self.response_http_get(self.url_tags+query_params)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(err)
            return None


    def filter_tags_per_localization(self, tags, localization):
        tags_list = []
        for tag in tags["data"]:
            tag_dict = {}
            tag_dict["name"] = tag["localization_names"][localization]
            tag_dict["description"] = tag["localization_descriptions"][localization]
            tags_list.append(tag_dict)
        return tags_list


    def check_live_stream(self):
        stream_list = self.get_stream()["data"]
        if len(stream_list)>0:
                current_stream = stream_list[0]
                if current_stream["type"] == "live":
                    return True
        return False


    def get_live_stream_data(self):
        if self.check_live_stream():
            live_stream = self.get_stream()["data"][0]

            game_data = self.get_game(live_stream["game_id"])

            live_tags = self.get_tags(live_stream["tag_ids"])
            tags_data = {}
            tags_data["tags"] = self.filter_tags_per_localization(live_tags, "pt-br")

            live_stream["game_data"] = game_data
            live_stream["tags_data"] = tags_data

            return live_stream
        return None


class FollowersSet():
    def __init__(self, follows_captured):
        self.count = follows_captured["total"]
        self.follower_list = follows_captured["data"]


    def check_followers_count(self, last_followers_got):
        if (self.count == last_followers_got.count):
            print("0 new followers, past count: " + str(last_followers_got.count) + ", new count: " + str(self.count))
        if (self.count < last_followers_got.count):
            print(str(last_followers_got.count - self.count) + " followers left the channel :( past count: "
                    + str(last_followers_got.count) + ", new count: " + str(self.count))
        if (self.count > last_followers_got.count):
            print("You have "+ str(self.count - last_followers_got.count) + " followers :) past count: "
                    + str(last_followers_got.count) + ", new count: " + str(self.count))


    def check_new_followers(self, last_followers_got):
        if (self.count > last_followers_got.count):
            return self.count - last_followers_got.count
        return 0


