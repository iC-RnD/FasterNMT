import pika
import json


class ICRabbitMQ(object):
    def __init__(self, host, virtual_host, usr, passw, **kwargs):
        """
        Khởi tạo
        :param host: địa chỉ rabbitmq server
        :param virtual_host: virtual_host
        :param queue_name: tên queue
        :param usr: user rabbitmq server
        :param passw: password
        """
        self.host = host
        self.virtual_host = virtual_host
        self.user = usr
        self.passw = passw
        self.credentials = pika.PlainCredentials(usr, passw)
        self.connection = None
        self.kwargs = kwargs

    def init_connection(self):
        self.connection = \
            pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, virtual_host=self.virtual_host, credentials=self.credentials))

    def connection_close(self):
        self.connection.close()

    def connection_status(self):
        return self.connection.is_open

    def init_queue(self, queue_name, exchange="", durable=True, max_priority=-1):
        """
        khởi tạo queue
        :param exchange:
        :param queue_name: tên queue
        :param durable: true (Queue vẫn tồn tại nếu nhưng RabitMQ khởi động lại)
        :param max_priority: Mức độ priority tối đa; None thì không xét priority;
                            khác None thì xét priority (tối đa priority = 10)
        :return: channel
        """
        if self.connection is None:
            self.init_connection()
        channel = self.connection.channel()
        if exchange == "" and queue_name != "":
            if max_priority == -1:
                channel.queue_declare(queue=queue_name, durable=durable)
            else:
                channel.queue_declare(queue=queue_name, durable=durable, arguments={'x-max-priority': max_priority})
        return channel

    @staticmethod
    def publish_message(channel, routing_key, body, priority=-1, delivery_mode=2, exchange=''):
        """
        run pushlish message
        :param channel: channel đã được tạo
        :param routing_key: key hoặc tên queue (nếu exchange = '')
        :param body: data push
        :param priority: mức ưu tiên
        :param delivery_mode: ??
        :param exchange: routing
        """
        if priority == -1:
            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(body),
                                  properties=pika.BasicProperties(delivery_mode=delivery_mode))
        else:
            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(body),
                                  properties=pika.BasicProperties(delivery_mode=delivery_mode, priority=priority))
        print("push done")

    @staticmethod
    def run_consummer(channel, queue_name, callback_func, is_ack_type=1):
        """
        run consumer
        :param is_ack_type: 1 - xử lý xong mới ack; 2 - ack xong mới xử lý
        :param channel: channel đã được tạo
        :param queue_name: tên queue
        :param callback_func: hàm callback được định nghĩa bởi người dùng
        :return:
        """
        print(" *wait message")

        def callback(ch, method, properties, body):
            if is_ack_type == 1:
                body = json.loads(body.decode("utf-8"))
                callback_func(body, properties)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print("receive done: ")
            else:
                body = json.loads(body.decode("utf-8"))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                callback_func(body, properties)
                print("receive done: ")

        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        channel.start_consuming()


if __name__ == '__main__':
    host, virtual_host, usr, passw = '', '', '', ''
    rab = ICRabbitMQ(host, virtual_host, usr, passw)
    queue_name = ''

    # test run producer
    channel = rab.init_queue(queue_name, max_priority=10)
