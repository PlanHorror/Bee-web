import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), 'processor'))))
from processor.main import *
import time
import asyncio
class DataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.running = True
        await self.accept()

        await self.send(text_data=json.dumps({
            'message': 'Connected'        

        }))
        # Start a background task for periodic updates
        asyncio.create_task(self.send_time())    

        
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        self.send(text_data=json.dumps({
            'message': 'Received'
        }))
    async def disconnect(self, close_code):
        # Cancel the background task when the connection is closed
        self.running = False
        await self.close()
    async def send_time(self):
        while self.running:
            await asyncio.sleep(1)
            await self.send(text_data=json.dumps({
                'message': return_time()
            }))