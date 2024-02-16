import math
import json
import requests
import telebot
from telebot import types
import datetime
from csv import writer
import folium
# from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from folium import plugins
from IPython.display import display
import csv
from folium.features import DivIcon
import bot_auxiliar
import pandas as pd
from folium import plugins
from folium.utilities import image_to_url
import subprocess
from fastapi_utils.session import FastAPISessionMaker
# from fastapi import (APIRouter, Depends, HTTPException, Query)
import deps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crear la conexión a la base de datos
def create_db_engine():
    return create_engine('mysql+mysqlconnector://root:mypasswd@mysql_bot:3306/Telegram_bot_db')

# Crear la sesión de base de datos
def create_db_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

import crud
from sqlalchemy.orm import Session
from schemas.Member import MemberCreate, MemberUpdate, MemberSearchResults
from schemas.Recommendation import RecommendationCreate, RecommendationUpdate, RecommendationSearchResults
from schemas.last_user_position import Last_user_positionCreate, Last_user_positionUpdate, Last_user_positionSearchResults
from schemas.Measurement import MeasurementCreate, MeasurementUpdate, MeasurementSearchResults

# Ponemos nuestro Token generado con el @BotFather
TOKEN = "6738738196:AAFVC0OT3RAv4PJvHsV4Vj9zYIlulIlnPLw"
# Creamos nuestra instancia "bot" a partir de ese TOKEN
bot = telebot.TeleBot(TOKEN)
api_url = 'http://mve:8001'

# Variables para recordar el estado de las cosas!!
last_recomendation_per_user = {}
last_location_of_user = {}
recomendation_aceptada = {}

# Mensajes determinados 
message_goal_of_the_system={"The goal of this system is create a collage of our neighborhood.This system will ask you to go to different places in the neighborhood and take pictures that catch your attention in that place."}
message_change_personal_information = ("Also you can modify your personal information (if you want) using the following commands:\n" +
                                       "/setname [YOUR NAME] -> to set your name, \n"
                                       "/setsurname  [YOUR SURNAME] -> to set your surname, \n" +
                                       "/setage [YOUR AGE] -> Set your age, \n" +
                                       "/setmail [YOUR EMAIL] -> to set your email, \n" +
                                       "/setgender [NOBINARY or MALE or FEMALE or NOANSWER] -> to set your gender. \n" +
                                       "This information can be changed anytime using these commands.")

message_info_interaction = ("The goal of this system is to create a map of picture taken in diferentes places of Deusto. To create a map of the Deusto as pictures of Deusto. This system give you some recomendation of places to take photos and create a map of photos."+
                            "You can interact with me using the following commands:\n" +
                            "/recommendation -> to request places to take a photo, \n" +
                            "/measurements -> to send the photo in the place you accepted \n" +
                            "/map -> to see the map of the places with the photos \n" )
                            

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


# Manejar el comando /start ->
@bot.message_handler(commands=['start'])
def start(message):
    # We want to look if the user is already in the database or not!
    peticion = api_url + f'/members/{message.chat.id}'
    try:
        response = requests.get(peticion, headers=headers)
        # CASE (user exists in the database).
        if response.status_code == 200:
            data = response.json()  # data -> user information -> Member
            bot.send_message(message.chat.id, f"Hello {message.chat.first_name}! Welcome back!")
            bot.send_message(message.chat.id, message_goal_of_the_system)
            bot.send_message(message.chat.id, message_info_interaction)
            bot.send_message(message.chat.id, message_change_personal_information)
        # CASE (user dont exists in the database).
        else:
            data=bot_auxiliar.add_user(message=message)
            if data != None:
                # We have to insert a device in the dataset for the user and also relate the user with the device.
                data=bot_auxiliar.add_device()
                if data != None:
                    data=bot_auxiliar.add_member_device(member_id=message.chat.id, device_id=data['id'])
                    # We insert in the database the Member_Device entity.
                    if data != None:
                        bot.send_message(
                                message.chat.id, f"Hello! Nice to meet you {message.chat.first_name}!")
                        bot.send_message(message.chat.id, message_goal_of_the_system)
                        bot.send_message(message.chat.id, message_info_interaction)
                        bot.send_message(message.chat.id, message_change_personal_information)
                        # Insert the user in the telegram_bot_db
                        engine = create_db_engine()
                        db = create_db_session(engine)
                        Member= MemberCreate(id=message.chat.id, name=message.chat.first_name,surname="",age=0, gender="NOANSWER", city="", mail=message.chat.username, birthday=datetime.datetime.now())
                        crud.member.create_member(db=db, obj_in=Member)
                        db.close()
                    else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}") 
                        bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314. Wait few minutes and try again.")
     
                else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")  
                        bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314. Wait few minutes and try again.")
     
            else:
                print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
                bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314. Wait few minutes and try again.")
    
                                 
    except Exception as e:
        print("Error durante la conexion con la base de datos:", e)
        bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
        return None
    
           

# command /setname.
@bot.message_handler(commands=['setname'])
def set_name(message):

    # Obtain the name of the user.
    name = message.text.replace('/setname', '').strip()
    # Int he case no name we explain the user how to do it.
    if not name:
        bot.reply_to(
            message, "Please provide a valid name after the /setname command. For example: /setname John")
    # if we have name:
    else:
        # We look if the user is in the database.
        peticion = api_url + f'/members/{message.chat.id}'
        response = None

        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers)
        except Exception as e:
            print("Error durante la conexion con la base de datos:", e)
            return None

        # if the user is in the database we update the name.
        if response.status_code == 200:
            data = response.json()  # Si la respuesta es JSON
            surname = data['surname']
            age = data['age']
            birthday = data['birthday']
            city = data['city']
            gender = data['gender']
            mail = data['mail']
            # We update the name in the database!
            peticion = api_url + '/sync/hives/1/members/'
            payload = [
                {
                    "member": {
                        "name": name,
                        "surname": surname,
                        "age": age,
                        "gender": gender,
                        "city": city,
                        "mail": mail,
                        "birthday": birthday,
                        "real_user": True,
                        "id": message.chat.id
                    },
                    "role": "WorkerBee"
                }
            ]
            response = None
            try:
                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                        json=payload)
            except Exception as e:
                print("Error durante la conexion con la base de datos:", e)
                return None
            # Verificar el código de respuesta
            if response.status_code == 201:
                data = response.json()  # Si la respuesta es JSON
                bot.reply_to(
                    message, f"Hello, {name}! Your name has been successfully registered.")
                # bot.reply_to(message, f"¡Hola, {name}! Tu nombre ha sido registrado correctamente.")
                bot.send_message(
                    message.chat.id, message_change_personal_information)
            else:
                print(
                    f"Error en la solicitud. Código de respuesta: {response.status_code}")
        else:
            print(
                f"Error en la solicitud. Código de respuesta: {response.status_code}")


@bot.message_handler(commands=['setgender'])
def set_gender(message):

    # Obtiene el nombre enviado por el usuario
    gender = message.text.replace('/setgender', '').strip()
    if not gender:
        bot.reply_to(
            message, f"Please provide a valid gender after the /setgender command. For example: '/setgender NOBINARY'. Possible genders are: [NOBINARY, MALE, FEMALE, or NOANSWER]")
    else:
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto!
        peticion = api_url + f'/members/{message.chat.id}'
        response = None
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers)

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                # en caso de que si -> update y respuesta acorde
                name = data['name']
                surname = data['surname']
                age = data['age']
                birthday = data['birthday']
                city = data['city']
                mail = data['mail']
                peticion = api_url + '/sync/hives/1/members/'
                payload = [
                    {
                        "member": {
                            "name": name,
                            "surname": surname,
                            "age": age,
                            "gender": gender,
                            "city": city,
                            "mail": mail,
                            "birthday": birthday,
                            "real_user": True,
                            "id": message.chat.id
                        },
                        "role": "WorkerBee"
                    }
                ]

                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                        json=payload)

                # Verificar el código de respuesta
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    bot.reply_to(
                        message, f"Your gender has been successfully registered. Thanks for your cooperation!")
                    bot.send_message(
                        message.chat.id, message_change_personal_information)
                    # data -> List[NewMembers]
                    print("Respuesta exitosa:", data)
                    # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                    print(
                        f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
            print("Error durante la solicitud:", e)


@bot.message_handler(commands=['setmail'])
def set_mail(message):

    # Obtiene el nombre enviado por el usuario
    mail = message.text.replace('/setmail', '').strip()
    if not mail:
        bot.reply_to(
            message, "Please provide a valid email after the /setmail command. For example: '/setmail user@example.com'")
    else:
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto!
        peticion = api_url + f'/members/{message.chat.id}'
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers)

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                # print("Respuesta exitosa:", data) # data -> Member
                # en caso de que si -> update y respuesta acorde
                print(data)
                surname = data['surname']
                age = data['age']
                birthday = data['birthday']
                city = data['city']
                name = data['name']
                gender = data['gender']

                peticion = api_url + '/sync/hives/1/members/'
                payload = [
                    {
                        "member": {
                            "name": name,
                            "surname": surname,
                            "age": age,
                            "gender": gender,
                            "city": city,
                            "mail": mail,
                            "birthday": birthday,
                            "real_user": True,
                            "id": message.chat.id
                        },
                        "role": "WorkerBee"
                    }
                ]

                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                        json=payload)

                # Verificar el código de respuesta
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    # data -> List[NewMembers]
                    print("Respuesta exitosa:", data)
                    bot.reply_to(
                        message, f"Your email has been successfully registered.")
                    bot.send_message(
                        message.chat.id, message_change_personal_information)
                    # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                    print(
                        f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
            print("Error durante la solicitud:", e)


@bot.message_handler(commands=['setbirthday'])
def set_birthday(message):

    # Obtiene el nombre enviado por el usuario
    birthday = message.text.replace('/setbirthday', '').strip()
    if not birthday:
        bot.reply_to(
            message, "Please provide a valid date after the /setbirthday command. For example: '/setbirthday 2021-01-11T00:00:00'")
    else:
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto!
        peticion = api_url + f'/members/{message.chat.id}'
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers)

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                # print("Respuesta exitosa:", data) # data -> Member
                # en caso de que si -> update y respuesta acorde
                print(data)
                surname = data['surname']
                age = data['age']
                city = data['city']
                name = data['name']
                mail = data['mail']
                gender = data['gender']

                peticion = api_url + '/sync/hives/1/members/'
                payload = [
                    {
                        "member": {
                            "name": name,
                            "surname": surname,
                            "age": age,
                            "gender": gender,
                            "city": city,
                            "mail": mail,
                            "birthday": birthday,
                            "real_user": True,
                            "id": message.chat.id
                        },
                        "role": "WorkerBee"
                    }
                ]

                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                        json=payload)

                # Verificar el código de respuesta
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    # data -> List[NewMembers]
                    print("Respuesta exitosa:", data)
                    bot.reply_to(
                        message, f"Your date of birth has been registered.")
                    bot.send_message(
                        message.chat.id, message_change_personal_information)
                    # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                    print(
                        f"Error en la solicitud. Código de respuesta: {response.status_code}")
                    # bot.send_message(message.chat.id, "Por favor, asegurate que la informacion esta bien. Debes introducir /setbirthday [YYYY-MM-DDT00:00:00], por ejemplo /setbirthday 2021-01-11T00:00:00 es un comando válido.")

        except Exception as e:
            print("Error durante la solicitud:", e)


@bot.message_handler(commands=['setage'])
def set_age(message):
    # Obtiene el nombre enviado por el usuario
    age = message.text.replace('/setage', '').strip()
    if not age:
        bot.reply_to(
            message, "Please provide a valid age after the /setage command. For example: /setage 25")

    else:
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto!
        peticion = api_url + f'/members/{message.chat.id}'
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers)

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                # print("Respuesta exitosa:", data) # data -> Member
                # en caso de que si -> update y respuesta acorde
                print(data)
                surname = data['surname']
                name = data['name']
                birthday = data['birthday']
                city = data['city']
                gender = data['gender']
                mail = data['mail']
                bot.send_message(
                    message.chat.id, message_change_personal_information)

                peticion = api_url + '/sync/hives/1/members/'
                payload = [
                    {
                        "member": {
                            "name": name,
                            "surname": surname,
                            "age": age,
                            "gender": gender,
                            "city": city,
                            "mail": mail,
                            "birthday": birthday,
                            "real_user": True,
                            "id": message.chat.id
                        },
                        "role": "WorkerBee"
                    }
                ]

                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                        json=payload)

                # Verificar el código de respuesta
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    # data -> List[NewMembers]
                    # print("Respuesta exitosa:", data)
                    bot.reply_to(
                        message, f"Your age has been successfully registered.")
                else:
                    print(
                        f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
            print("Error durante la solicitud:", e)


@bot.message_handler(commands=['setsurname'])
def set_surname(message):

    # Obtiene el nombre enviado por el usuario
    surname = message.text.replace('/setsurname', '').strip()
    if not surname:
        bot.reply_to(
            message, "Please provide a valid surname after the /setsurname command. For example '/setsurname Doe'.")
    else:
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto!
        peticion = api_url + f'/members/{message.chat.id}'
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers)

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                name = data['name']
                age = data['age']
                birthday = data['birthday']
                city = data['city']
                gender = data['gender']
                mail = data['mail']

                bot.send_message(
                    message.chat.id, message_change_personal_information)

                peticion = api_url + '/sync/hives/1/members/'
                payload = [
                    {
                        "member": {
                            "name": name,
                            "surname": surname,
                            "age": age,
                            "gender": gender,
                            "city": city,
                            "mail": mail,
                            "birthday": birthday,
                            "real_user": True,
                            "id": message.chat.id
                        },
                        "role": "WorkerBee"
                    }
                ]

                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                        json=payload)

                # Verificar el código de respuesta
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    bot.reply_to(
                        message, f"Your surname has been successfully registered.")

                else:
                    print(
                        f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
            print("Error durante la solicitud:", e)


@bot.message_handler(commands=['setcity'])
def set_city(message):

    # Obtiene el nombre enviado por el usuario
    city = message.text.replace('/setcity', '').strip()
    if not city:
        bot.reply_to(
            message, "Please provide a valid city after the /setcity command. For example '/setcity Madrid'.")
    else:
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto!
        peticion = api_url + f'/members/{message.chat.id}'
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers)

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                # print("Respuesta exitosa:", data) # data -> Member
                # en caso de que si -> update y respuesta acorde
                print(data)
                surname = data['surname']
                name = data['name']
                age = data['age']
                birthday = data['birthday']
                gender = data['gender']
                mail = data['mail']

                bot.send_message(
                    message.chat.id, message_change_personal_information)

                peticion = api_url + '/sync/hives/1/members/'
                payload = [
                    {
                        "member": {
                            "name": name,
                            "surname": surname,
                            "age": age,
                            "gender": gender,
                            "city": city,
                            "mail": mail,
                            "birthday": birthday,
                            "real_user": True,
                            "id": message.chat.id
                        },
                        "role": "WorkerBee"
                    }
                ]

                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                        json=payload)

                # Verificar el código de respuesta
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    # data -> List[NewMembers]
                    print("Respuesta exitosa:", data)
                    bot.reply_to(
                        message, f"Your city has been successfully registered.")
                else:
                    print(
                        f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
            print("Error durante la solicitud:", e)



# Envia una ubicación para pedir la recomendación!
@bot.message_handler(commands=['recommendation'])
def recommendation(message):
    engine = create_db_engine()
    db = create_db_session(engine)
    member=crud.member.get_by_id(db=db, id=message.chat.id)
    member_2 = bot_auxiliar.existe_user(id_user=message.chat.id)
    if member != None and member_2 != None:
        
        markup = types.ReplyKeyboardMarkup(row_width=1)
        location_btn = types.KeyboardButton("Share location", request_location=True)
        markup.add(location_btn)
        bot.send_message(message.chat.id, "The first step is to share your location. Please press the button to do so", reply_markup=markup)
        #in the case we have the last position we delete this information! 
        last_user_position=crud.last_user_position.get_by_id(db=db, member_id=message.chat.id)
        db.commit()
        if last_user_position != None:
            crud.last_user_position.remove(db=db,Last_user_position=last_user_position)
            db.commit()
        # Elimino las recomendaciones pasadas. 
        list_recomendation= crud.recommendation.get_All_Recommendation(db=db, member_id=message.chat.id)
        for i in list_recomendation:
            crud.recommendation.remove(db=db, recommendation=i)
    else: 
        bot.reply_to(message, "Please first send the comand /start to be in the database. Thanks you! ")
    db.close()
    


# Envia una ubicación para pedir la recomendación!
@bot.message_handler(commands=['measurement'])
def measurement(message):
    engine = create_db_engine()
    db = create_db_session(engine)
    member=crud.member.get_by_id(db=db, id=message.chat.id)
    member_2 = bot_auxiliar.existe_user(id_user=message.chat.id)
    if member != None and member_2 != None:
        #Hemos verificado que el usuario existe:
        #TODO! verificar que es None el resultado que sale 
        recomendacion_aceeptada= crud.recommendation.get_recommendation_to_measurement(db=db, member_id=message.chat.id)
        if recomendacion_aceeptada != None: 
            #in the case we have the last position we delete this information! 
            last_user_position=crud.last_user_position.get_by_id(db=db, member_id=message.chat.id)
            db.commit()
            if last_user_position != None:
                crud.last_user_position.remove(db=db,Last_user_position=last_user_position)
                db.commit()
            #Le pido al usuario la localizacion. 
            markup = types.ReplyKeyboardMarkup(row_width=1)
            location_btn = types.KeyboardButton("Share location", request_location=True)
            markup.add(location_btn)
            bot.send_message(message.chat.id, "The first step is to share your location. Please press the button to do so", reply_markup=markup)
        else:
            bot.reply_to(message, "You do not have any accepted recommendations, please use the /recommendation command before performing this command.")
    else: 
        bot.reply_to(message, "Please first send the comand /start to be in the database. Thanks you! ")
    db.close()
    
@bot.message_handler(content_types=['location'])
def handle_location(message):
    user = bot_auxiliar.existe_user(message.chat.id)
    if user != None:
        #Volvemos a eliminar la localizacion anterior aunque no deberia ser necesario.
        #De etse modo nos aseguramos que solo hay una!  
        engine = create_db_engine()
        db = create_db_session(engine)  
        last_user_position=crud.last_user_position.get_by_id(db=db, member_id=message.chat.id)
        if last_user_position !=None:
            crud.last_user_position.remove(db=db,Last_user_position=last_user_position)
            db.commit()
        last_location_of_user= Last_user_positionCreate(member_id=message.chat.id, location={
                'Longitude': message.location.longitude, 'Latitude': message.location.latitude})
        crud.last_user_position.create_last_user_position(db=db, obj_in=last_location_of_user)
        rec = bot_auxiliar.recomendaciones_aceptadas(message.chat.id)
        # El usuario tiene recomendaciones aceptadas!
        if rec != None:
            #Elimino las recomendaciones que no son la aceptada. 
            list_notified_recommendation=crud.recommendation.get_recommendation_notified(db=db, member_id=message.chat.id)
            for i in list_notified_recommendation:
                crud.recommendation.remove(db=db, recommendation=i)
            bot.reply_to(message, "You have a active recomendation. It's time for you to send the photo! Plese send to me the photo to integrate it in the collague.")
            
        else:
            #Eliminamos las enteriores en caso de existir
            list_recommendation=crud.recommendation.get_All_Recommendation(db=db, member_id=message.chat.id)
            if list_recommendation !=None:
                for i in list_recommendation:
                    crud.recommendation.remove(db=db, recommendation=i)
            # En caso de no tener ninguna recomendacion aceptada -> creamos nuevas recomendaciones y eliminamos las anteriores. 
            campaign = bot_auxiliar.get_campaign_hive_1(message.chat.id)
            if campaign is not None:
                campaign_id = campaign['id'] 
                info = {
            "member_current_location": {
                "Longitude": message.location.longitude,
                "Latitude": message.location.latitude
            }} 
                data = bot_auxiliar.recomendacion(
                    id_user=message.chat.id, campaign_id=campaign_id, info=info)
                if data is not None and data!={"detail": "Incorrect_user_campaign"} and data != {'detail': 'far_away'} and data != {'details': 'Incorrect_user_role'} and data != {"detail": "no_measurements_needed"}:
                    # Metemos en nuestra base de datos las recomendaciones que nos han dado.
                    for i in range(0,len(data['results'])):
                        recomendation= RecommendationCreate(id=data['results'][i]['recommendation']['id'],member_id=message.chat.id, posicion=str(i), state="NOTIFIED")
                        crud.recommendation.create_recommendation(db=db, obj_in=recomendation)
                    # TODO! ExTEPCIONES
                    if len(data['results']) == 0:
                        bot.send_message(
                            message.chat.id, "There are no recommendations for you at this time. We're sorry.")
                        crud.last_user_position.remove(db=db,Last_user_position=last_location_of_user)
                    elif len(data['results']) == 1:
                        markup = types.ReplyKeyboardMarkup(row_width=1)
                        option1 = types.KeyboardButton(f"Option 1")
                        markup.add(option1)
                        bot.send_message(
                            message.chat.id, "At the moment, based on your location, we only have one recommendation for you. Hope you like it! \n")
                        bot.send_message(message.chat.id, "Option 1:")
                        bot.send_location(chat_id=message.chat.id, latitude=data['results'][0]['cell'][
                                          'centre']['Latitude'], longitude=data['results'][0]['cell']['centre']['Longitude'])
                        bot.send_message(
                            message.chat.id, "Please choose from the menu where you want to take the photo.", reply_markup=markup)
                    elif len(data['results']) == 2:
                        markup = types.ReplyKeyboardMarkup(row_width=1)
                        option1 = types.KeyboardButton(f"Option 1")
                        option2 = types.KeyboardButton(f"Option 2")
                        markup.add(option1, option2)
                        bot.send_message(
                            message.chat.id, "Given your location, we have 2 possible recommendations for you. Both options are explained here! \n")
                        bot.send_message(message.chat.id, "Option 1:")
                        bot.send_location(chat_id=message.chat.id, latitude=data['results'][0]['cell'][
                                          'centre']['Latitude'], longitude=data['results'][0]['cell']['centre']['Longitude'])
                        bot.send_message(message.chat.id, "Option 2:")
                        bot.send_location(chat_id=message.chat.id, latitude=data['results'][1]['cell'][
                                          'centre']['Latitude'], longitude=data['results'][1]['cell']['centre']['Longitude'])
                        bot.send_message(
                            message.chat.id, "Please choose from the menu where you want to take the photo.", reply_markup=markup)

                    else:
                        markup = types.ReplyKeyboardMarkup(row_width=1)
                        option1 = types.KeyboardButton(f"Option {1} ")
                        option2 = types.KeyboardButton(f"Option {2}")
                        option3 = types.KeyboardButton(f"Option {3}")
                        markup.add(option1, option2, option3)
                        bot.send_message(
                            message.chat.id, "Given your location, here we have 3 recommendations for you. All three options are explained below! \n")
                        bot.send_message(message.chat.id, "Option 1:")
                        bot.send_location(chat_id=message.chat.id, latitude=data['results'][0]['cell'][
                                          'centre']['Latitude'], longitude=data['results'][0]['cell']['centre']['Longitude'])
                        bot.send_message(message.chat.id, "Option 2:")
                        bot.send_location(chat_id=message.chat.id, latitude=data['results'][1]['cell'][
                                          'centre']['Latitude'], longitude=data['results'][1]['cell']['centre']['Longitude'])
                        bot.send_message(message.chat.id, "Option 3:")
                        bot.send_location(chat_id=message.chat.id, latitude=data['results'][2]['cell'][
                                          'centre']['Latitude'], longitude=data['results'][2]['cell']['centre']['Longitude'])
                        bot.send_message(
                            message.chat.id, "Please choose from the menu where you want to take the photo.", reply_markup=markup)
                else:
                    bot.reply_to(
                        message, "There are no possible recommendations for you at this time. We're sorry.")
            else:
                bot.reply_to(
                    message, "There are no active campaigns near you. We're sorry.")
    else:
        bot.reply_to(message, "Please first send the comand /start to be in the database. Thanks you! ")

    db.close()


# Dada la eleccion del usuario almacenamos su eleccion en la base de datos.
@bot.message_handler(func=lambda message: message.text == "Option 1" or message.text == "Option 2" or message.text == "Option 3")
def handle_option(message):
    user_choice = message.text
    engine = create_db_engine()
    db = create_db_session(engine)
    member=crud.member.get_by_id(db=db, id=message.chat.id)
    member_2 = bot_auxiliar.existe_user(id_user=message.chat.id)
    if member != None and member_2 != None:
        #En caso de tener almacenada la posicion del usuario la eliminamos.
        last_user_position=crud.last_user_position.get_by_id(db=db, member_id=message.chat.id)
        if last_user_position != None :
            crud.last_user_position.remove(db=db,Last_user_position=last_user_position)
        
        list_recomendation=crud.recommendation.get_All_Recommendation(db=db, member_id=message.chat.id)
        if list_recomendation != None:
            #llegado a este punto sabemos que el usuario ha dado position y que tiene recomendaciones aqui debe aceptar alguna. 
            #Nos aseguramos de que no tiene ninguna recomendacion activa:
            accepted_recomendation=crud.recommendation.get_recommendation_to_measurement(db=db, member_id=message.chat.id)
            if accepted_recomendation !=None:
                bot.reply_to(message, "You have already accepted a recommendation in the follow location. Please send the photo to complete the process.")
                recomendation= bot_auxiliar.recomendacion(id_user=message.chat.id, recomendation_id=  accepted_recomendation.id)
                bot.send_location(message.chat.id, latitude=recomendation['cell']['centre']['Latitude'], longitude=recomendation['cell']['centre']['Longitude'])  
            else:
                number = message.text.replace('Option ', '').strip()
                if int(number) != 1 and int(number)!= 2 and int(number) != 3:
                    bot.reply_to(
                        message, "Please choose a valid option from the menu. For example: 'Option 1', 'Option 2', or 'Option 3'. Or send a text with this information.")
                else:
                    rec=crud.recommendation.get_recommendation_for_position(db=db,member_id=message.chat.id,position=int(number)-1)
                    # Registramos la recomendacion aceptada que tiene el usuario. 
                    accepted_recomendation=bot_auxiliar.update_recomendation(id_user=message.chat.id, recomendation_id=rec.id)
                    if accepted_recomendation != None:
                        crud.recommendation.update(db=db, db_obj=rec, obj_in={"state":"ACCEPTED"})
                        bot.reply_to(message,
                                f"You chose {user_choice}. Thanks for your choice. When you're at the location, please type the /measurement command and follow the instructions. then we will ask your location again and a picture in this place.")       
                    else:
                            bot.reply_to(message.chat.id,"system error. Plase contact with @Maite314")
        else:
            bot.reply_to(
                message, f"First please go the There are no recommendations for you at this time. We're sorry. Please request a recommendation.")
    else:
        bot.reply_to(message, "Please first send the comand /start to be in the database. Thanks you! ")
    db.close()


@bot.message_handler(content_types=['photo'])
def handle_photo_and_location(message):
    # Verificar si el mensaje contiene una foto
    #Este tiene que tener la localizacion y la recomendacion y la foto 
    engine = create_db_engine()
    db = create_db_session(engine)
    last_user_position=crud.last_user_position.get_by_id(db=db, member_id=message.chat.id)
    if last_user_position != None:
        accepted_recomendation=crud.recommendation.get_recommendation_to_measurement(db=db, member_id=message.chat.id)
        recomendation_aceptada_2=bot_auxiliar.recomendaciones_aceptadas(message.chat.id)
        #Todo! asegurate que cuando recomendacion_Aceptada_2 es vacia te devuelve None. 
        if accepted_recomendation != None:

            if recomendation_aceptada_2 != None:
                data=bot_auxiliar.create_measurement(id_user=message.chat.id, Latitud=last_user_position.location['Latitude'], Longitud=last_user_position.location['Longitude'])
                if data != None:
                    #Guardamos la photo. 
                    file_id = message.photo[-1].file_id
                    file_info = bot.get_file(file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    file_path = f'Telegram_bot/Pictures/photo{data["id"]}.jpg'
                    with open(file_path, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    if data['recommendation_id'] == None:
                        lat, long = bot_auxiliar.get_point(id_user=message.chat.id, latitud=last_user_position.location['Latitude'], longuitud=last_user_position.location['Longitude'])
                        if lat != None and long != None:
                            #Calculado el punto de la celda dond eha ido la medicion. 
                            measurement=MeasurementCreate(id=data['id'],url=file_path, location={'Latitude':lat, 'Longitude':long})
                            crud.measurement.create_measurement(db=db, obj_in=measurement)
                            crear_mapa(message)
                            bot.reply_to(
                                    message, "Thanks for sending the photo!")
                            bot.send_message(
                                    message, "Your photo has been registered, but please take the photo at the location where you agreed to do so. You can see the map with photos with the command /map.")
                            #TODO! no se si esto esta bien!
                            lat = recomendation_aceptada_2['cell']['centre']['Latitude']
                            long = recomendation_aceptada_2['cell']['centre']['Longitude']
                            bot.send_location(chat_id=message.chat.id, latitude=lat, longitude=long)

                        else:
                            bot.reply_to(message, "Your position is out of the campaign. Please send the location at the point you agreed.")

                    else:
                        #LA medicion no es donde debe! 
                        elements=crud.recommendation.get_All_Recommendation(db=db, member_id=message.chat.id)
                        for i in elements:
                                crud.recommendation.remove(db=db, recommendation=i)
                        crud.last_user_position.remove(db=db, Last_user_position=last_user_position)
                        #TODO! verificar que esta todo bien 
                        lat, long= bot_auxiliar.get_point(id_user=message.chat.id, latitud=recomendation_aceptada_2['member_current_location']['Latitude'], longuitud=recomendation_aceptada_2['member_current_location']['Longitude'])
                        measurement=MeasurementCreate(id=data['id'],url=file_path, location={ 'Longitude': long, 'Latitude': lat})
                        crud.measurement.create_measurement(db=db, obj_in=measurement)   
                        db.commit()
                        crear_mapa(message)
                        bot.reply_to(message, "Thanks for sending the photo! You you se the result with the command /map.")
                else:
                    bot.reply_to(message, "Plase try again. Be sure that the location you send is in the accepted recomendation you select.")
            else:
                crud.recomendation.remove(db=db, db_obj=accepted_recomendation)
                bot.reply_to(message, "Please first send the comand /mesasurement or /recomendation to have your location. Thanks you! ")
          
        else:
            bot.reply_to(message, "Please first send the comand /mesasurement or /recomendation to have your location. Thanks you! ")
    else:
        bot.reply_to(message, "Please first send the comand /mesasurement or /recomendation to have your location. Thanks you! ")
    db.close()

def actualizar_repositorio():
    # Ejecutar el comando para agregar, hacer commit y hacer push del archivo HTML
    subprocess.run(['git', 'add', '-f', 'docs/index.html'])
    subprocess.run(['git', 'commit', '-m', 'Actualizar HTML'])
    subprocess.run(['git', 'push'])


def crear_mapa(message):
    data=bot_auxiliar.get_surface()
   
    if data != None:
        surface_centre_lat = data['results'][0]['boundary']['centre']['Latitude'] 
        surface_centre_long = data['results'][0]['boundary']['centre']['Longitude']
        surface_radius = data['results'][0]['boundary']['radius']
        mapa = folium.Map(
                location=[surface_centre_lat, surface_centre_long], zoom_start=18)
        #Este tiene que tener la localizacion y la recomendacion y la foto 
        engine = create_db_engine()
        db = create_db_session(engine)
        measuerements =crud.measurement.get_all(db=db)
        db.close()
        # Obtener el número de combinaciones diferentes de las dos primeras columnas
        campaign=bot_auxiliar.get_campaign_hive_1(id_user=message.chat.id)
        if campaign is None:
                bot.reply_to("Error in the visualizacion. Perhaps there is no active campaign. Please contact with @Maite314")
                return None
        else:
            radio=campaign['cells_distance']/2
            hipotenusa= math.sqrt(2*((radio)**2))
            las_pos_lat, las_pos_long= measuerements[0].location['Latitude'], measuerements[0].location['Longitude']
            n_files=0
            for i in measuerements:
                if i.location['Latitude'] != las_pos_lat and i.location['Longitude'] != las_pos_long:
                    n_files=1
                else: 
                    n_files=n_files+1
                            
                combinacion = (i.location['Latitude'], i.location['Longitude'] )
                datos_tercera_columna = i.url
                grados = 90
                lat, long = combinacion[0], combinacion[1]
                print(n_files*grados)
                if 0 <= n_files*grados and 90 > n_files*grados:
                                esquina_derecha_arriba=bot_auxiliar.get_point_at_distance(lat1=lat, lon1=long, d=radio,bearing=0 )
                                medio_ARRIBA=  bot_auxiliar.get_point_at_distance(lat1=lat, lon1=long, d=radio,bearing=90)
                                image_overlay = folium.raster_layers.ImageOverlay(
                                        image=datos_tercera_columna,
                                        bounds=[medio_ARRIBA,esquina_derecha_arriba],
                                        opacity=0.75,
                                        interactive=True,
                                        cross_origin=False,
                                        zindex=1,
                                    )
                                image_overlay.add_to(mapa)

                elif 90 <= n_files*grados and 180 > n_files*grados:
                                esquina_arriba_izquierda=bot_auxiliar.get_point_at_distance(lat1=lat, lon1=long, d=hipotenusa,bearing=135 )
                                medio_ARRIBA=  [lat,long]
                                image_overlay = folium.raster_layers.ImageOverlay(
                                        image=datos_tercera_columna,
                                        bounds=[esquina_arriba_izquierda,medio_ARRIBA],
                                        opacity=0.75,
                                        interactive=True,
                                        cross_origin=False,
                                        zindex=1,
                                    )
                                image_overlay.add_to(mapa)                               
                elif 180 <= n_files*grados and 270 > n_files*grados:
                                lateral_izq_medio=bot_auxiliar.get_point_at_distance(lat1=lat, lon1=long, d=radio,bearing=180 )
                                punto_central= bot_auxiliar.get_point_at_distance(lat1=lat, lon1=long, d=radio,bearing=270)
                                image_overlay = folium.raster_layers.ImageOverlay(
                                        image=datos_tercera_columna,
                                        bounds=[lateral_izq_medio,punto_central],
                                        opacity=0.75,
                                        interactive=True,
                                        cross_origin=False,
                                        zindex=1,
                                    )
                                image_overlay.add_to(mapa)
                else:
                                lateral_derecho_medio=bot_auxiliar.get_point_at_distance(lat1=lat, lon1=long, d=hipotenusa,bearing=315 )
                                central_point= [lat,long]
                                image_overlay = folium.raster_layers.ImageOverlay(
                                        image=datos_tercera_columna,
                                        bounds=[central_point,lateral_derecho_medio],
                                        opacity=0.75,
                                        interactive=True,
                                        cross_origin=False,
                                        zindex=1,
                                    )
                                image_overlay.add_to(mapa)
                           
            mapa.save('docs/index.html')
            actualizar_repositorio()
            bot.reply_to(
                        message, "The map is inb this URL: https://mpuerta004.github.io/Telegram_bot/")

    else:
        bot.reply_to(message, "Problem with the representation, campaigns and surface. Please contact with @Maite314")


@bot.message_handler(commands=['map'])
def crear_mapa_bot(message):
    crear_mapa(message)
    # Tengo que pedir el centro de la camapaña- surface
    bot.reply_to( message, "The map is in this URL: https://mpuerta004.github.io/Telegram_bot/. if your photo is not in the web page, wait a few seconds and reload the page.")

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, message_info_interaction)
    bot.send_message(message.chat.id, message_change_personal_information)
    bot.send_message(message.chat.id, "The map is in this URL: https://mpuerta004.github.io/Telegram_bot/")


if __name__ == "__main__":
    bot.polling()
