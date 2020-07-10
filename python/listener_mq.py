import ast
from rabbitmq.rabbitmq import RabbitListener


q_name = "teste"
twitter_queue = "twitter"
twitch_queue = "twitch"
discord_queue = "discord"
target_queues = [twitter_queue,twitch_queue,discord_queue]


rabbit_consumer = RabbitListener("localhost","lyamada","lyamada")
for channel in target_queues:
    rabbit_consumer.declare_queue(channel)


for channel in target_queues:
    method_frame, header_frame, body = rabbit_consumer.basic_get(channel)
    while method_frame:
        print("channel: " + channel + "|| type: "+ header_frame.headers["type"] + " || " + rabbit_consumer.binary_to_str(body))
        rabbit_consumer.basic_ack(method_frame)
        method_frame, header_frame, body = rabbit_consumer.basic_get(channel)