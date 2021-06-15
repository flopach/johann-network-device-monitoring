import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import time
from celery.result import AsyncResult
from johann.celery import app
import logging

logger = logging.getLogger("applogger")

class StatusConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "statusgroup"
        async_to_sync(self.channel_layer.group_add)(self.group_name,self.channel_name) 
        self.accept()

    def disconnect(self, close_code):
        self.channel_layer.group_discard(self.channel_name, 'statusgroup')

    def receive(self, text_data):
        """
        Based on the input from the StatusWebsocket do various functions
        for now it is only one type for processing the celery task status
        """
        try:
            r_data = json.loads(text_data)
            self.process_task_status(r_data["type"],r_data["task_id"])            
        except Exception as e:
            logger.exception("Error when task_id was received from the websocket: {}".format(e))

    def process_task_status(self,task_type,task_id):
        """
        Send updates about the celery task status based on the task_id

        Possible types:
        - task_normal: Task with no result output, only status message
        - task_content: Task with output of the result
        """
        task = AsyncResult(id=task_id, app=app)

        if task.successful() == True:
            if task_type == "task_normal":
                self.send_status("t_result",task.result)
            elif task_type == "task_content":
                self.send_status("t_content_result",task.result)
        else:
            self.send_status("t_status",task.state)

    def send_status(self,type,content):
        """
        Send message

        type: t_status, t_result
        """
        msg = {
            "type" : type,
            "content" : content
        }
        #print("sending: {}".format(msg))
        self.send(json.dumps(msg))