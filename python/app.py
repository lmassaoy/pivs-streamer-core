import os
import time
from responses.twitch_response import TwitchResponse, FollowersSet
from rabbitmq.rabbitmq import RabbitPublisher
import stomp


gaules = "181077473"
gaardes = "536389691"
client_id = "z7mzdxii95zb6y533fckayeyp6ugb5"
client_secret = "wly8uwegfy3b9lrth3t4kvfc6rxl73"
rabbit_server = "localhost"
rabbit_username = "lyamada"
rabbit_password = "lyamada"
twitter_queue = "twitter"
twitch_queue = "twitch"
discord_queue = "discord"
target_queues = [twitter_queue,twitch_queue,discord_queue]


def main():
    # Connecting to RabbitMQ || Declaring Queues
    rabbit_publisher = RabbitPublisher(rabbit_server,rabbit_username,rabbit_password)
    for channel in target_queues:
        rabbit_publisher.declare_queue(channel)


    # Initialize TwitchResponse
    twitch_watcher = TwitchResponse(gaules,client_id,client_secret)


    # Initialize FollowersSet
    last_follower_set = FollowersSet(twitch_watcher.get_followers())
    current_follower_set = FollowersSet(twitch_watcher.get_followers())

    # Initialize Live Status
    live_status = False


    loop_condition = 0
    # It's FOREEEEVEEEEEEER!
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
                for channel in target_queues:
                    rabbit_publisher.basic_msg_send(channel,{"type": "streaming"},str(live_stream))


        # Check Channel's Followers
        new_followers_count = current_follower_set.check_new_followers(last_follower_set)
        if new_followers_count > 0:
            if new_followers_count == 1:
                print("You have "+ str(new_followers_count) + " new follower :) || # of followers now: " + str(current_follower_set.count))
            else:
                print("You have "+ str(new_followers_count) + " new followers :) || # of followers now: " + str(current_follower_set.count))
            
            loops = 0
            while loops < new_followers_count:
                print(current_follower_set.follower_list[loops])
                for channel in target_queues:
                    rabbit_publisher.basic_msg_send(channel,{"type": "new_followers"},str(current_follower_set.follower_list[loops]))
                loops+=1


        last_follower_set = current_follower_set
        current_follower_set = FollowersSet(twitch_watcher.get_followers())


        time.sleep(5)

if __name__ == '__main__':
    main()