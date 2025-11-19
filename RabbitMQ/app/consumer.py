import os
import time
import base64
import pika
import logging

logger = logging.getLogger(__name__)

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "tasks")
ROUTING_KEY = os.getenv("ROUTING_KEY", "encode")


def connect_with_retry():
    attempt = 1
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST)
            )
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            attempt += 1
            time.sleep(3)


def setup_queues(channel):
    dlx_name = "dlx"
    dlq_name = "task_queue_dlq"

    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="direct",
        durable=True,
    )

    channel.exchange_declare(
        exchange=dlx_name,
        exchange_type="direct",
        durable=True,
    )

    channel.queue_declare(queue=dlq_name, durable=True)
    channel.queue_bind(
        queue=dlq_name,
        exchange=dlx_name,
        routing_key="encode.dlq",
    )

    queue_name = "task_queue"
    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            "x-dead-letter-exchange": dlx_name,
            "x-dead-letter-routing-key": "encode.dlq",
        },
    )
    channel.queue_bind(
        queue=queue_name,
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
    )

    return queue_name


def process_message(body: bytes) -> str:

    text = body.decode("utf-8")

    if "fail" in text.lower():
        raise ValueError("Simulated processing failure")

    encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    return encoded


def main():
    connection = connect_with_retry()
    channel = connection.channel()
    queue_name = setup_queues(channel)

    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        try:
            result = process_message(body)
            print(f"Result od decoding {result}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
