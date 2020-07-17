import os
import time
from rabbitmq.rabbitmq import RabbitPublisher
from responses.twitch_response import TwitchResponse, FollowersSet
from responses.twitter_response import TweepyAgent


def main():
    twitch_streamer_id = str(os.environ.get('TWITCH_STREAMER_ID'))
    client_id = os.environ.get('TWITCH_APP_CLIENT_ID')
    client_secret = os.environ.get('TWITCH_APP_CLIENT_SECRET')
    rabbit_server = os.environ.get('RABBITMQ_SERVER')
    rabbit_username = os.environ.get('RABBITMQ_USERNAME')
    rabbit_password = os.environ.get('RABBITMQ_PASSWORD')
    twitter_queue = os.environ.get('RABBITMQ_TWITTER_QUEUE')
    twitch_queue = os.environ.get('RABBITMQ_TWITCH_QUEUE')
    discord_queue = os.environ.get('RABBITMQ_DISCORD_QUEUE')
    target_queues = [twitter_queue,twitch_queue,discord_queue]
    consumer_key = os.environ.get('TWITTER_APP_CONSUMER_KEY')
    consumer_secrect = os.environ.get('TWITTER_APP_CONSUMER_SECRET')
    api_token = os.environ.get('TWITTER_APP_TOKEN')
    api_secret = os.environ.get('TWITTER_APP_TOKEN_SECRET')
    twitter_username = os.environ.get('TWITTER_STREAMER_USERNAME')


    # Connecting to RabbitMQ || Declaring Queues
    rabbit_publisher = RabbitPublisher(rabbit_server,rabbit_username,rabbit_password)
    for queue in target_queues:
        rabbit_publisher.declare_queue(queue)


    # Initialize TwitchResponse & FollowersSets
    twitch_watcher = TwitchResponse(twitch_streamer_id,client_id,client_secret)

    last_follower_set = FollowersSet(twitch_watcher.get_followers())
    current_follower_set = FollowersSet(twitch_watcher.get_followers())


    # Initialize Tweepy Agent, Followers Count and Followers Set
    tweepy_agent = TweepyAgent(consumer_key,consumer_secrect,api_token,api_secret)

    last_twitter_followers_count = tweepy_agent.get_followers_count(twitter_username)
    current_twitter_followers_count = tweepy_agent.get_followers_count(twitter_username)
    last_twitter_followers_set = tweepy_agent.get_last_followers(twitter_username)
    current_twitter_followers_set = tweepy_agent.get_last_followers(twitter_username)


    # Initialize Live Status
    live_status = False


    loop_condition = 0
    # It's FOREEEEVEEEEEEER! <3 KISS
    while loop_condition < 1:
        
        # Check Live Stream
        if live_status:
            live_stream = twitch_watcher.get_live_stream_data()
            if live_stream == None:
                live_status = False
                print("Streaming finished!")
        else:
            live_stream = twitch_watcher.get_live_stream_data()
            if live_stream != None:
                live_status = True
                print("Streaming going on!")
                for queue in target_queues:
                    rabbit_publisher.basic_msg_send(queue,{"type": "streaming"},str(live_stream))


        # Check Channel's Followers
        new_followers_count = current_follower_set.check_new_followers(last_follower_set)
        if new_followers_count > 0:
            loops = 0
            while loops < new_followers_count:
                rabbit_publisher.basic_msg_send(twitch_queue,{"type": "new_twitch_follower"},str(current_follower_set.follower_list[loops]))
                loops+=1


        last_follower_set = current_follower_set
        current_follower_set = FollowersSet(twitch_watcher.get_followers())


        # Check Twitter's Followers
        if current_twitter_followers_count > last_twitter_followers_count:
            last_followers_id_list = [follower["follower_id"] for follower in last_twitter_followers_set]

            for follower in current_twitter_followers_set:
                if follower["follower_id"] not in last_followers_id_list:
                    message = str({'follower_id': follower["follower_id"], 'follower_name': follower["follower_name"], 'follower_screen_name': follower["follower_screen_name"]})
                    rabbit_publisher.basic_msg_send(twitter_queue,{"type": "new_twitter_follower"},message)

        last_twitter_followers_count = current_twitter_followers_count
        last_twitter_followers_set = current_twitter_followers_set
        current_twitter_followers_count = tweepy_agent.get_followers_count(twitter_username)
        current_twitter_followers_set = tweepy_agent.get_last_followers(twitter_username)


        time.sleep(60)

if __name__ == '__main__':
    main()               
                