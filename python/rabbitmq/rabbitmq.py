import pika
import ast


class RabbitPublisher():
    def __init__(self, server_name, username, password):
        self.credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(server_name, credentials=self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()


    def declare_queue(self, q_name):
        self.channel.queue_declare(queue = q_name, durable=True, exclusive=False, auto_delete=False)

    
    def basic_msg_send(self,routing_key,headers,message):
        properties = pika.BasicProperties(headers=headers)
        self.channel.basic_publish(exchange='', routing_key=routing_key, properties = properties, body=message)


    def close_conn(self):
        self.connection.close()


class RabbitListener():
    def __init__(self, server_name, username, password):
        self.credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(server_name, credentials=self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()


    def declare_queue(self, q_name):
        self.channel.queue_declare(queue = q_name, durable=True, exclusive=False, auto_delete=False)


    def basic_get(self, q_name):
        return self.channel.basic_get(q_name)


    def basic_ack(self, method_frame):
        self.channel.basic_ack(method_frame.delivery_tag)

    
    def binary_to_str(self, body):
        return str(ast.literal_eval(body.decode('utf-8')))