import os
import time
import pika
import logging

logger = logging.getLogger(__name__)

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "tasks")
ROUTING_KEY = os.getenv("ROUTING_KEY", "encode")

MESSAGES = [
    "Hello world",
    "Rabbit messaging",
    "This message will fail",
    "Another test message",
]

def connect_with_retry():
    attempt = 1
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST)
            )
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.info("Connection fail")
            attempt += 1
            time.sleep(3)

def main():
    connection = connect_with_retry()
    channel = connection.channel()

    dlx_name = "dlx"
    dlq_name = "task_queue_dlq"
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct", durable=True)
    channel.exchange_declare(exchange=dlx_name, exchange_type="direct", durable=True)
    channel.queue_declare(queue=dlq_name, durable=True)
    channel.queue_bind(queue=dlq_name, exchange=dlx_name, routing_key="encode.dlq")

    queue_name = "task_queue"
    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            "x-dead-letter-exchange": dlx_name,
            "x-dead-letter-routing-key": "encode.dlq",
        },
    )
    channel.queue_bind(queue=queue_name, exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY)

    i = 0
    while True:
        message = MESSAGES[i % len(MESSAGES)]

        i += 1
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=message.encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        time.sleep(5)

if __name__ == "__main__":
    main()
