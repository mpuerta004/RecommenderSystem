import requests
import telebot 
from telebot import types
from enum import Enum
import random 
import datetime 
from csv import writer
import folium
from folium import plugins
# from IPython.display import display
import csv
import math
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from math import asin, atan2, cos, degrees, radians, sin, sqrt

# #https://api.telegram.org/bot<TU_TOKEN/getUpdates
# #https://api.telegram.org/bot<TU_TOKEN>/getMe
api_url= 'http://mve:8001'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }



def add_user(message):
    peticion = api_url + '/sync/hives/1/members/'
    payload = [
                {
                    "member": {
                        "name": message.chat.first_name,
                        "surname": "",
                        "age": 0,
                        "gender": "NOANSWER",
                        "city": "",
                        "mail": "",
                        "birthday": "2024-01-11T16:09:59",
                        "real_user": True,
                        "id": message.chat.id
                    },
                    "role": "WorkerBee"
                }
            ]
            # Put endpoint to integrate the information of the user in the datases
    try:
        response = requests.put(peticion, headers=headers,
                                            json=payload)
                # Verificar el código de respuesta
                # We insert the user correctly in the database,
        if response.status_code == 201:
                    # La solicitud fue exitosa
            data = response.json()  # Si la respuesta es JSON
            return data 
        else:
            return None
    except Exception as e:
        print( f"Error with the API: {e}")
        return None 
def add_device():
    peticion = api_url + "/devices"
    info_device = {
                    "description": "string",
                    "brand": "string",
                    "model": "string",
                    "year": "string"
                }
                # Post a new device in the dataset.
    try:
        response = requests.post(
                    peticion, headers=headers, json=info_device)
                        # IF the device is correctly inserted in the dataset.
        if response.status_code == 201:
                        data = response.json()  # Si la respuesta es JSON
                        return data
        else:
            return None
    except Exception as e:
        print( f"Error with the API: {e}")
        return None 

def add_member_device(device_id:int, member_id:int):
    info_device_member = {
                            "member_id": member_id,
                            "device_id": device_id,
                        }
    try:
        peticion = api_url + f"/sync/hives/1/campaigns/1/devices"
        response = requests.put(peticion, headers=headers, json=info_device_member)
        # If we insert corretlly the user, the devide and the relation between them.
        if response.status_code == 201:
                            # La solicitud fue exitosa
            data = response.json()  # Si la respuesta es JSON
            return data
        else:
            return None
    except Exception as e:
        print( f"Error with the api: {e}")
        return None 
    
    
    
def existe_user(id_user:int):
    #Si el usuario ya esta registrado o no! 
    peticion = api_url + f'/members/{id_user}'
    try:
        # Realizar una petición POST con datos en el cuerpo
        response = requests.get(peticion, headers=headers) 
        # Verificar el código de respuesta
        if response.status_code == 200:
            # La solicitud fue exitosa -> el usuario esta en l abase de datos! 
            user_info = response.json()  # Si la respuesta es JSON
            return user_info
        elif response.status_code == 404:
            print( f"Member with id=={id_user} not found" )
            return None      
        elif response.status_code == 500:
            print( f"Error with mysql" )
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )
        return None

def recomendaciones_aceptadas(id_user:int):
    #Aqui hay que ver si recomendaciones aceptadas cerca de la posicion. 
    peticion = api_url + f"/members/{id_user}/recommendations"
    try:
        response = requests.get(peticion, headers=headers)
        if response.status_code == 200:
            data_recomendaciones = response.json()
            if len(data_recomendaciones['results'])>0:
                for i in data_recomendaciones['results']:
                    if i['state'] =="ACCEPTED":   
                        return i
            return None
        else:
            print("Error with the API")
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )    
        return None

def recomendacion(id_user:int,recomendation_id:int):
    #Aqui hay que ver si recomendaciones aceptadas cerca de la posicion. 
    peticion = api_url + f"/members/{id_user}/recommendations/{recomendation_id}"
    try:
        response = requests.get(peticion, headers=headers)
        if response.status_code == 200:
            data= response.json()
            return data
        else:
            print("Error with the API")
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )    
        return None

def update_recomendation(id_user:int,recomendation_id:int):
    peticion = api_url + \
                        f"/members/{id_user}/recommendations/{recomendation_id}"
    info = "ACCEPTED"
    try:
                        # Se registramos la recomendacion acceptada por el usuario.
        response = requests.patch(peticion, headers=headers, json=info)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error with the API")
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )    
        return None
def create_measurement(id_user:int, Latitud:float, Longitud:float):
    peticion = api_url + f"/members/{id_user}/measurements"
    date = datetime.datetime.utcnow()
    measurement_creation = {
                        "datetime": date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "location": {
                            "Longitude": Longitud,
                            "Latitude": Latitud
                        },
                        "no2": 0,
                        "co2": 0,
                        "o3": 0,
                        "so02": 0,
                        "pm10": 0,
                        "pm25": 0,
                        "pm1": 0,
                        "benzene": 0}
    try:
        response = requests.post( peticion, headers=headers, json=measurement_creation)
        if response.status_code == 201:
            data = response.json()
            return data 
        else:
            print("Error with mysql")
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )
        return None


def get_surface():
    peticion = api_url + f"/hives/1/campaigns/1/surfaces"
    try:
        # Se registramos la recomendacion acceptada por el usuario.
        response = requests.get(peticion, headers=headers)
        if response.status_code == 200:
            # La solicitud fue exitosa
            data = response.json()
            return data 
        else:
            print("Error with mysql")
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )
        return None


def get_point(id_user:int, latitud:float, longuitud:float):
    peticion = api_url + \
                                f"/sync/get_location/{id_user}"
    date = datetime.datetime.utcnow()
    measurement_creation = {
                                "datetime": date.strftime("%Y-%m-%dT%H:%M:%S"),
                                "location": {
                                    "Longitude": longuitud,
                                    "Latitude": latitud
                                },
                                "no2": 0,
                                "co2": 0,
                                "o3": 0,
                                "so02": 0,
                                "pm10": 0,
                                "pm25": 0,
                                "pm1": 0,
                                "benzene": 0}
    try:
        response = requests.get(peticion, headers=headers, json=measurement_creation)
        if response.status_code == 200:
            data = response.json()
            return data["Latitude"], data['Longitude']
        else:
            print("Error with mysql")
            return None, None
    except Exception as e:
        print( f"Error with mysql {e}" )
        return None, None        


def get_campaign_hive_1(id_user:int):
    peticion = api_url +"/hives/1/campaigns"
    try:
        response = requests.get(peticion, headers=headers)
        if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json() 
                a=len(data['results'])
                elemento=random.randint(0,a-1)
                campaign=data['results'][elemento]
                return campaign
        else:
            print("Error with mysql")
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )
        return None

def recomendacion(id_user:int, info,campaign_id:int):
    peticion = api_url + f'/members/{id_user}/campaigns/{campaign_id}/recommendations'    
    try:               
        response = requests.post(peticion, params={'time': datetime.datetime.utcnow()},headers=headers,json=info) 
        if response.status_code == 201:
            data = response.json() 
            return data 
        else:
            print("Error with mysql")
            return None
    except Exception as e:
        print( f"Error with mysql {e}" )
        return None

# def obtener_dimensiones_imagen(url_imagen):
#     # Obtener las dimensiones de la imagen utilizando PIL
#     with Image.open(url_imagen) as img:
#         ancho, alto = img.size
#     return ancho, alto
            

def get_point_at_distance(lat1, lon1, d, bearing, R=6371):
    """
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth

    Returns new lat/lon coordinate {d}km from initial, in degrees
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    a = radians(bearing)
    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
    lon2 = lon1 + atan2(
        sin(a) * sin(d/R) * cos(lat1),
        cos(d/R) - sin(lat1) * sin(lat2)
    )
    return (degrees(lat2), degrees(lon2),)

