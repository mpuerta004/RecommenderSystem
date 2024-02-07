import math
import json
import requests
import telebot
from telebot import types
from enum import Enum
import random
import datetime
from csv import writer
import folium
from folium import plugins
from IPython.display import display
import csv
from folium.features import DivIcon
import bot_auxiliar
import pandas as pd

from folium import plugins
from folium.utilities import image_to_url

# Ponemos nuestro Token generado con el @BotFather
TOKEN = "6738738196:AAFVC0OT3RAv4PJvHsV4Vj9zYIlulIlnPLw"
# Creamos nuestra instancia "bot" a partir de ese TOKEN
bot = telebot.TeleBot(TOKEN)
# #https://api.telegram.org/bot<TU_TOKEN/getUpdates
# #https://api.telegram.org/bot<TU_TOKEN>/getMe
api_url = 'http://localhost:8001'
last_recomendation_per_user = {}
last_location_of_user = {}
# message_change_personal_information = ("Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
#                             "/setname [TU NOMBRE] -> para definir tu nombre, \n"
#                             "/setsurname  [TU APELLIDO] -> para definir tu apellido, \n"+
#                             "/setage [TU EDAD] -> Define tu edad, \n"+
#                             "/setbirthday [YYYY-MM-DDT00:00:00] -> para definir tu cumpleaños, \n"+
#                             "/setcity [TU CIUDAD] -> para definir tu ciudad, \n"+
#                             "/setmail [TU EMAIL] -> para definir tu email, \n"+
#                             "/setgender [NOBINARY or MALE or FEMALE or NOANSWER] -> para definir tu género. \n"+
#                             "Esta información puede ser cambiada cuando quieras usando estos comandos.")

message_change_personal_information = ("Also you can modify your personal information (if you want) using the following commands:\n" +
                                       "/setname [YOUR NAME] -> to set your name, \n"
                                       "/setsurname  [YOUR SURNAME] -> to set your surname, \n" +
                                       "/setage [YOUR AGE] -> Set your age, \n" +
                                       "/setmail [YOUR EMAIL] -> to set your email, \n" +
                                       "/setgender [NOBINARY or MALE or FEMALE or NOANSWER] -> to set your gender. \n" +
                                       "This information can be changed anytime using these commands.")
message_info_interaction = ("The goal of this system is to create a map of picture taken in diferentes places of Deusto. This system give you some recomendation of places to take photos and create a map of photos."+
                            "You can interact with me using the following commands:\n" +
                            "/recommendation -> to request places to take a photo, \n" +
                            "/measurements -> to send the photo in the place you accepted \n" +
                            "/map -> to see the map of the places with the photos \n" )
                            

recomendation_aceptada = {}
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


# TODO poner la opcion de que el usario pueda poner todos sus datos personales de una vez

# Manejar el comando /start ->
@bot.message_handler(commands=['start'])
def send_locations(message):

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # We want to look if the user is already in the database or not!
    peticion = api_url + f'/members/{message.chat.id}'
    response = None
    try:
        response = requests.get(peticion, headers=headers)
        # If the answer is 200 -> the user is already in the database!

    except Exception as e:
        print("Error durante la solicitud:", e)
        return None

    # CASE (user exists in the database).
    if response.status_code == 200:
        data = response.json()  # data -> user information -> Member
        # bot.send_message(message.chat.id, f"Hola {message.chat.first_name}! Bienvenido de nuevo!")
        bot.send_message(
            message.chat.id, f"Hello {message.chat.first_name}! Welcome back!")
        bot.send_message(message.chat.id, message_info_interaction)
        bot.send_message(message.chat.id, message_change_personal_information)
    # CASE (user dont exists in the database).
    else:
        # TODO igual aqui se le pueden hacer algunas preguntas para que diga sus datos personales!
        # We insert in the database.
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
        response = None
        try:
            # Put endpoint to integrate the information of the user in the datases
            response = requests.put(peticion, headers=headers,
                                    json=payload)
        except Exception as e:
            print("Error durante la conexion con la base de datos:", e)
            return None
            # Verificar el código de respuesta
        # We insert the user correctly in the database,
        if response.status_code == 201:
            # La solicitud fue exitosa
            data = response.json()  # Si la respuesta es JSON
            # We have to insert a device in the dataset for the user and also relate the user with the device.
            peticion = api_url + "/devices"
            info_device = {
                "description": "string",
                "brand": "string",
                "model": "string",
                "year": "string"
            }
            response = None

            try:
                # Post a new device in the dataset.
                response = requests.post(
                    peticion, headers=headers, json=info_device)
            except Exception as e:
                print("Error durante la conexion con la base de datos:", e)
                return None
            # IF the device is correctly inserted in the dataset.
            if response.status_code == 201:
                data = response.json()  # Si la respuesta es JSON
                # We insert in the database the Member_Device entity.
                info_device_member = {
                    "member_id": message.chat.id,
                    "device_id": data['id'],
                }
                # TODO igual el 1 de campaign no funciona
                peticion = api_url + f"/sync/hives/1/campaigns/1/devices"
                response = None
                try:
                    response = requests.put(
                        peticion, headers=headers, json=info_device_member)
                except Exception as e:
                    print("Error durante la conexion con la base de datos:", e)
                    return None
                # If we insert corretlly the user, the devide and the relation between them.
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    bot.send_message(
                        message.chat.id, f"Hello! Nice to meet you {message.chat.first_name}!")
                    bot.send_message(
                        message.chat.id, message_change_personal_information)
                else:
                    print(
                        f"Error en la solicitud. Código de respuesta: {response.status_code}")
            else:
                print(
                    f"Error en la solicitud. Código de respuesta: {response.status_code}")
        else:
            print(
                f"Error en la solicitud. Código de respuesta: {response.status_code}")


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
def set_gender(message):

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
@bot.message_handler(commands=['recomendation', 'measurement'])
def recibir_localizacion(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)

    location_btn = types.KeyboardButton(
        "Compartir ubicación", request_location=True)
    markup.add(location_btn)
    bot.send_message(
        message.chat.id, "The first step is to share your location. Please press the button to do so", reply_markup=markup)

# Ofrecemos al usuario la posibilidad de compartir su ubicación.


@bot.message_handler(content_types=['location'])
def handle_location(message):
    user = bot_auxiliar.existe_user(message.chat.id)
    if user is not None:
        info = {
            "member_current_location": {
                "Longitude": message.location.longitude,
                "Latitude": message.location.latitude
            }}
        last_location_of_user[message.chat.id] = info
        rec = bot_auxiliar.recomendaciones_aceptadas(message.chat.id)
        # El usuario tiene recomendaciones aceptadas!
        if rec is not None:
            bot.reply_to(message, "It's time for you to send the photo!")
        else:
            # En caso de no tener ninguna recomendacion aceptada -> creamos una.
            campaign = bot_auxiliar.get_campaign_hive_1(message.chat.id)
            if campaign is not None:
                campaign_id = campaign['id']

                data = bot_auxiliar.recomendacion(
                    id_user=message.chat.id, campaign_id=campaign_id, info=info)
                if data is not None and data != {'detail': 'far_away'} and data != {'details': 'Incorrect_user_role'}:
                    # Eliminamos los datos anteriores guardados
                    recomendation_aceptada[message.chat.id] = 0
                    last_recomendation_per_user[message.chat.id] = data['results']
                    # TODO! ExTEPCIONES
                    if len(data['results']) == 0:
                        bot.send_message(
                            message.chat.id, "There are no recommendations for you at this time. We're sorry.")
                    elif len(data['results']) == 1:
                        markup = types.ReplyKeyboardMarkup(row_width=1)
                        # - lat {data['results'][0]['cell']['centre']['Latitude']} long{data['results'][0]['cell']['centre']['Longitude']}")
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
        bot.send_message(
            message.chat.id, "There is an issue, please send the \start command. Thank you!")


# Dada la eleccion del usuario almacenamos su eleccion en la base de datos.
@bot.message_handler(func=lambda message: message.text == "Option 1" or message.text == "Option 2" or message.text == "Option 3")
def handle_option(message):
    user_choice = message.text
    if last_recomendation_per_user[message.chat.id] is not None:
        # Asegurate que sigue activa la recomendacion es decir si tiene aceptadas y no las ha realizado hay que corregiirlo.
        number = message.text.replace('Option ', '').strip()

        recomendation_aceptada[message.chat.id] = int(number) - 1
        number = int(number)-1
        recomendacion_info = last_recomendation_per_user[message.chat.id][number]
        recommendation_id = recomendacion_info['recommendation']['id']
        bot.reply_to(message,
                     f"You chose {user_choice}. Thanks for your choice. When you're at the location, please type the /measurement command and follow the instructions.")
        peticion = api_url + \
            f"/members/{message.chat.id}/recommendations/{recommendation_id}"
        info = "ACCEPTED"
        response = None
        try:
            # Se registramos la recomendacion acceptada por el usuario.
            response = requests.patch(peticion, headers=headers, json=info)
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()

            else:
                print(
                    f"Error en la solicitud de update de la recomendation. Código de respuesta: {response.status_code}")

        except Exception as e:
            print("Error durante la solicitud:", e)

    else:
        bot.reply_to(
            message, f"There are no recommendations for you at this time. We're sorry. Please request a recommendation.")


@bot.message_handler(content_types=['photo'])
def handle_photo_and_location(message):
    # Verificar si el mensaje contiene una foto
    if message.photo:
        rec = bot_auxiliar.recomendaciones_aceptadas(message.chat.id)
        # El usuario tiene recomendaciones aceptadas!
        if rec is None:
            bot.send_message(
                message.chat.id, "We don't have your location. Please request a recommendation using the /recomendation command.")
        else:
            # Aquí puedes acceder a la información de la foto
            peticion = api_url + f"/members/{message.chat.id}/measurements"
            posicion_user = last_location_of_user[message.chat.id]
            date = datetime.datetime.utcnow()
            measurement_creation = {
                "datetime": date.strftime("%Y-%m-%dT%H:%M:%S"),
                "location": {
                    "Longitude": posicion_user["member_current_location"]["Longitude"],
                    "Latitude": posicion_user["member_current_location"]["Latitude"]
                },
                "no2": 0,
                "co2": 0,
                "o3": 0,
                "so02": 0,
                "pm10": 0,
                "pm25": 0,
                "pm1": 0,
                "benzene": 0}
            response = requests.post(
                peticion, headers=headers, json=measurement_creation)
            if response.status_code == 201:
                data = response.json()
                if data['recommendation_id'] == None:
                    file_id = message.photo[-1].file_id
                    file_info = bot.get_file(file_id)
                    # Descarga la foto
                    downloaded_file = bot.download_file(file_info.file_path)

                    # Guarda la foto en el sistema de archivos
                    file_path = f'src/Servicio/Telegram_bot/Pictures/photo{data["id"]}.jpg'
                    with open(file_path, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    peticion = api_url + \
                        f"/sync/get_location/{message.chat.id}"
                    posicion_user = last_location_of_user[message.chat.id]
                    date = datetime.datetime.utcnow()
                    measurement_creation = {
                        "datetime": date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "location": {
                            "Longitude": posicion_user["member_current_location"]["Longitude"],
                            "Latitude": posicion_user["member_current_location"]["Latitude"]
                        },
                        "no2": 0,
                        "co2": 0,
                        "o3": 0,
                        "so02": 0,
                        "pm10": 0,
                        "pm25": 0,
                        "pm1": 0,
                        "benzene": 0}

                    response = requests.get(
                        peticion, headers=headers, json=measurement_creation)
                    if response.status_code == 200:
                        data = response.json()
                        data_csv = [data["Latitude"],
                                    data['Longitude'], file_path]
                        with open("src/Servicio/Telegram_bot/Pictures/CSVFILE.csv", "a", newline="") as f_object:
                            # Pass the CSV  file object to the writer() function
                            writer_object = writer(f_object)
                            writer_object.writerow(data_csv)
                            # Close the file object
                            f_object.close()
                        bot.reply_to(
                            message, "Thanks for sending the photo!")
                        bot.send_message(
                            message, "Your photo has been registered, but please take the photo at the location where you agreed to do so.")

                        number = recomendation_aceptada[message.chat.id]
                        recomendacion_info = last_recomendation_per_user[message.chat.id][int(
                            number)]
                        lat = recomendacion_info['cell']['centre']['Latitude']
                        long = recomendacion_info['cell']['centre']['Longitude']
                        bot.send_location(
                            chat_id=message.chat.id, latitude=lat, longitude=long)

                    else:
                        print(
                            f"Error en la solicitud de medicion. Código de respuesta: {response.status_code}")

                else:
                    number = recomendation_aceptada[message.chat.id]
                    recomendacion_info = last_recomendation_per_user[message.chat.id][int(
                        number)]
                    lat = recomendacion_info['cell']['centre']['Latitude']
                    long = recomendacion_info['cell']['centre']['Longitude']
                    file_id = message.photo[-1].file_id
                    recomendation_aceptada[message.chat.id] = 0
                    del last_recomendation_per_user[message.chat.id]
                    # Obtiene información sobre el archivo de la foto
                    file_info = bot.get_file(file_id)

                    # Descarga la foto
                    downloaded_file = bot.download_file(file_info.file_path)

                    # Guarda la foto en el sistema de archivos
                    file_path = f'src/Servicio/Telegram_bot/Pictures/photo{data["id"]}.jpg'
                    with open(file_path, 'wb') as new_file:
                        new_file.write(downloaded_file)

                    data_csv = [lat, long, file_path]
                    with open("src/Servicio/Telegram_bot/Pictures/CSVFILE.csv", "a", newline="") as f_object:
                        # Pass the CSV  file object to the writer() function
                        writer_object = writer(f_object)
                        writer_object.writerow(data_csv)
                        f_object.close()
                    bot.reply_to(message, "Thanks for sending the photo!")

            elif response.status_code == 401:
                bot.reply_to(
                    message, "There is no active campaign or this position is not within the campaign. Please send a location at the point you agreed.")
                bot.reply_to(
                    message, "Please take the photo at the location where you agreed to do so.")
                number = recomendation_aceptada[message.chat.id]
                recomendacion_info = last_recomendation_per_user[message.chat.id][int(
                    number)]
                lat = recomendacion_info['cell']['centre']['Latitude']
                long = recomendacion_info['cell']['centre']['Longitude']
                bot.send_location(chat_id=message.chat.id,
                                  latitude=lat, longitude=long)
            else:
                print(
                    f"Error en la solicitud de medicion. Código de respuesta: {response.status_code}")


@bot.message_handler(commands=['map'])
def crear_mapa(message):
    # Tengo que pedir el centro de la camapaña- surface
    peticion = api_url + f"/hives/1/campaigns/1/surfaces"
    try:
        # Se registramos la recomendacion acceptada por el usuario.
        response = requests.get(peticion, headers=headers)
        if response.status_code == 200:
            # La solicitud fue exitosa
            data = response.json()

            surface_centre_lat = data['results'][0]['boundary']['centre']['Latitude']
            surface_centre_long = data['results'][0]['boundary']['centre']['Longitude']
            surface_radius = data['results'][0]['boundary']['radius']
            # peticion= api_url +f"/members/{message.chat.id}/measurements"

            mapa = folium.Map(
                location=[surface_centre_lat, surface_centre_long], zoom_start=18)
            print(surface_centre_lat, surface_centre_long)
            peticion = api_url + f"/hives/1/campaigns/show"
            try:

                # Se registramos la recomendacion acceptada por el usuario.
                response = requests.get(peticion, headers=headers)
                if response.status_code == 200:
                    df = pd.read_csv('src/Servicio/Telegram_bot/Pictures/CSVFILE.csv',
                                     names=['latitud', 'longitud', 'url_imagen'])
                    # Obtener el número de combinaciones diferentes de las dos primeras columnas
                    grupos = df.groupby(['latitud', 'longitud'])[
                        'url_imagen'].apply(list).reset_index()
                    for index, row in grupos.iterrows():
                        combinacion = (row['latitud'], row['longitud'])
                        datos_tercera_columna = row['url_imagen']
                        n_files = len(datos_tercera_columna)
                        grados = 360/n_files
                        for i in range(0, n_files):
                            tamano_imagen = min(95 * 2 ** (18 - 10), 150)
                            lat, long = combinacion[0], combinacion[1]
                            if 0 <= i*grados and 90 > i*grados:
                                print("de 0 a 90 grados")
                                folium.Marker(location=[lat, long], icon=folium.CustomIcon(
                                    icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(100, 100))).add_to(mapa)

                            elif 90 <= i*grados and 180 > i*grados:
                                print("de 90 a 180")
                                folium.Marker(location=[lat, long], icon=folium.CustomIcon(
                                    icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(100, 0))).add_to(mapa)

                            elif 180 <= i*grados and 270 > i*grados:
                                print("de 180 a 270")
                                folium.Marker(location=[lat, long], icon=folium.CustomIcon(
                                    icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(0, 0))).add_to(mapa)

                            else:
                                print("de 270 a 360")
                                folium.Marker(location=[lat, long], icon=folium.CustomIcon(
                                    icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(0, 100))).add_to(mapa)

                            df = pd.read_csv('src/Servicio/Telegram_bot/Pictures/DATAMAP.csv', names=[
                                             "list_point", "id_user", "Cardinal_actual", "expected_measurements", "color_number"])
                            for index, row in df.iterrows():
                                list_point = json.loads(row["list_point"])
                                id_user = row["id_user"]
                                Cardinal_actual = row["Cardinal_actual"]
                                excepted_measurements = row["expected_measurements"]
                                # color_number=str(row[4])

                                folium.Polygon(locations=list_point, color='black', fill=False,
                                               weight=1, popup=(folium.Popup(str(id_user))), opacity=0.5, fill_opacity=0.2).add_to(mapa)

                                folium.Marker(list_point[3], popup=f"Number of Expected measurements: {str(excepted_measurements)}",
                                              icon=DivIcon(
                                    icon_size=(200, 36),
                                    icon_anchor=(0, 0),
                                    html=f'<div style="font-size: 20pt;">{str(Cardinal_actual)}</div>'
                                )).add_to(mapa)

                    mapa.save('map.html')
                    bot.reply_to(
                        message, "This is the map with the result of the photos.")
                    with open("map.html", "rb") as map_file:
                        bot.send_document(
                            message.chat.id, map_file, caption="Tu Mapa")
                else:
                    print(
                        f"Error en la solicitud de update de la recomendation. Código de respuesta: {response.status_code}")
            except Exception as e:
                print("Error durante la solicitud:", e)

        else:
            print(
                f"Error en la solicitud de update de la recomendation. Código de respuesta: {response.status_code}")

    except Exception as e:
        print("Error durante la solicitud:", e)


if __name__ == "__main__":
    bot.polling()
