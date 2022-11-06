from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import json
from azure.storage.blob import BlobClient
from .facialrecognition import FacialRecog
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties
import os
from OptikaWeb.bdconnect import *
import numpy as np
import cv2


# Create your views here.
facialRecognizer = FacialRecog()

STORAGE_CONNECTION_STRING = os.environ.get("STORAGE_CONN")

IOTHUB_CONNECTION_STRING = os.environ.get("DEVICE_CONN")

DEVICE_ID = os.environ.get("DEVICE_ID")

iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)



@csrf_exempt
def generateDetectionLog(request):


    twin = iothub_registry_manager.get_twin(DEVICE_ID)
    twin_patch = Twin(properties= TwinProperties(desired={'readyToSend' : False}))
    
    twin = iothub_registry_manager.update_twin(DEVICE_ID, twin_patch, twin.etag)

    blob = BlobClient.from_connection_string(STORAGE_CONNECTION_STRING,"device-upload",f"{DEVICE_ID}/frame.jpg")

    modified = blob.get_blob_properties().last_modified

    binary = blob.download_blob().readall()

    frame = cv2.imdecode(np.asarray(bytearray(binary), dtype="uint8"), cv2.IMREAD_COLOR)

    detection = facialRecognizer.detect(frame)

    if detection:

        sendDetectionLog(detection['0'],",".join(detection),modified,"known")


    twin = iothub_registry_manager.get_twin(DEVICE_ID)
    twin_patch = Twin(properties= TwinProperties(desired={'readyToSend' : True}))
    twin = iothub_registry_manager.update_twin(DEVICE_ID, twin_patch, twin.etag)

def loadPeopleToRecog(request):

    """This function will happen everytime"""

    facialRecognizer.loadPeople(getPeople())

    return redirect("/")


