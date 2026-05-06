import os
import json
from typing import Callable

import aio_pika

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')


async def publish_event(exchange_name: str, event: dict):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.FANOUT,
            durable=True,
        )
        message = aio_pika.Message(
            body=json.dumps(event).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key='')


async def consume_events(exchange_name: str, callback: Callable):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.FANOUT,
            durable=True,
        )
        queue = await channel.declare_queue('', exclusive=True)
        await queue.bind(exchange)

        async with queue.iterator() as q:
            async for message in q:
                async with message.process():
                    event = json.loads(message.body.decode())
                    await callback(event)
