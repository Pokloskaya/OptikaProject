from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from azure.storage.blob import BlobClient
from .facialrecognition import FacialRecog
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties
import os
from OptikaWeb.bdconnect import FirebaseManager
import numpy as np
import cv2


# Create your views here.
facialRecognizer = FacialRecog()

database = FirebaseManager()

connect_str = os.environ.get("APP_CONN")

IOTHUB_CONNECTION_STRING = os.environ.get("DEVICE_CONN")
DEVICE_ID = "testdevice"
iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)



@csrf_exempt
def generateDetectionLog(request):


    twin = iothub_registry_manager.get_twin(DEVICE_ID)
    twin_patch = Twin(properties= TwinProperties(desired={'readyToSend' : False}))
    
    twin = iothub_registry_manager.update_twin(DEVICE_ID, twin_patch, twin.etag)

    blob = BlobClient.from_connection_string(connect_str,"device-upload","testdevice/frame.jpg")

    modified = blob.get_blob_properties().last_modified

    binary = blob.download_blob().readall()

    database.sendDetectionLog(binary,"daniel",modified,"known")


    twin = iothub_registry_manager.get_twin(DEVICE_ID)
    twin_patch = Twin(properties= TwinProperties(desired={'readyToSend' : True}))
    twin = iothub_registry_manager.update_twin(DEVICE_ID, twin_patch, twin.etag)

    
    return JsonResponse({ "status": 200, "body": {}})
