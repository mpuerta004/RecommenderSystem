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

TOKEN = "6738738196:AAFVC0OT3RAv4PJvHsV4Vj9zYIlulIlnPLw" # Ponemos nuestro Token generado con el @BotFather
bot = telebot.TeleBot(TOKEN)  #Creamos nuestra instancia "bot" a partir de ese TOKEN
# #https://api.telegram.org/bot<TU_TOKEN/getUpdates
# #https://api.telegram.org/bot<TU_TOKEN>/getMe
api_url= 'http://localhost:8001'
last_recomendation_per_user={}
localizacion_user_recomendacion_Aceptada={}

message_change_personal_information= ("Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
                            "/setname [TU NOMBRE] ->  para definir tu nombre, \n"
                            "/setsurname  [TU APELLIDO] ->  para definir tu apellido, \n"+
                            "/setage [TU EDAD] -> Define tu edad, \n"+
                            "/setbirthday [YYYY-MM-DDT00:00:00] -> para definir tu cumpleaños, \n"+
                            "/setcity [TU CIUDAD] -> para definir tu ciudad, \n"+
                            "/setmail [TU EMAIL] -> para definir tu email, \n"+
                            "/setgender [NOBINARY or MALE or FEMALE or NOANSWER] -> para definir tu género. \n"+
                            "Esta información puede ser cambiada cuando quieras usando estos comandos.")

recomendation_aceptada={} 
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
#TODO explicar a los usuarios que no se pueden coger varias recomendaciones a la vez. 

"""PREGUNTAS
    - Es mejor enviar una especie de JSON y que los usuarios lo modifiquen si quieren? 
    - 
"""

#TODO poner la opcion de que el usario pueda poner todos sus datos personales de una vez 

# Manejar el comando /start -> 
@bot.message_handler(commands=['start'])
def send_locations(message):
    
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    #We want to look if the user is already in the database or not!
    peticion = api_url + f'/members/{message.chat.id}'
    response=None
    try:
        response = requests.get(peticion, headers=headers) 
        #If the answer is 200 -> the user is already in the database!
        
    except Exception as e:
        print("Error durante la solicitud:", e)
        return None
    
    #CASE (user exists in the database). 
    if response.status_code == 200:
        data = response.json()  # data -> user information -> Member
        bot.send_message(message.chat.id, f"Hola {message.chat.first_name}! Bienvenido de nuevo!")  
        bot.send_message(message.chat.id, message_change_personal_information) 
    #CASE (user dont exists in the database). 
    else:
        #TODO igual aqui se le pueden hacer algunas preguntas para que diga sus datos personales! 
        #We insert in the database. 
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
        response=None
        try:
            #Put endpoint to integrate the information of the user in the datases
            response = requests.put(peticion, headers=headers,
                                            json =payload) 
        except Exception as e:
            print("Error durante la conexion con la base de datos:", e)
            return None
                # Verificar el código de respuesta
        #We insert the user correctly in the database,
        if response.status_code == 201:
            # La solicitud fue exitosa
            data = response.json()  # Si la respuesta es JSON
            #We have to insert a device in the dataset for the user and also relate the user with the device. 
            peticion = api_url + "/devices"
            info_device={
                    "description": "string",
                    "brand": "string",
                    "model": "string",
                    "year": "string"
                    }
            response=None

            try:
                #Post a new device in the dataset.
                response = requests.post(peticion, headers=headers,json=info_device) 
            except Exception as e:
                print("Error durante la conexion con la base de datos:", e)
                return None
            #IF the device is correctly inserted in the dataset.
            if response.status_code == 201:
                data = response.json()  # Si la respuesta es JSON
                #We insert in the database the Member_Device entity. 
                info_device_member={
                        "member_id": message.chat.id,
                        "device_id": data['id'],
                    }
                #TODO igual el 1 de campaign no funciona 
                peticion = api_url + f"/sync/hives/1/campaigns/1/devices"
                response=None
                try:
                    response = requests.put(peticion, headers=headers,json=info_device_member)
                except Exception as e:
                    print("Error durante la conexion con la base de datos:", e)
                    return None
                #If we insert corretlly the user, the devide and the relation between them. 
                if response.status_code == 201:
                    # La solicitud fue exitosa
                    data = response.json()  # Si la respuesta es JSON
                    bot.send_message(message.chat.id, f"Hola! Encantado de conocerte {message.chat.first_name}!")
                    bot.send_message(message.chat.id, message_change_personal_information) 
                else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
            else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
        else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")


# command /setname. 
@bot.message_handler(commands=['setname'])
def set_name(message):
    
    # Obtain the name of the user. 
    name = message.text.replace('/setname', '').strip()
    #Int he case no name we explain the user how to do it. 
    if not name:
        bot.reply_to(message, "Por favor, proporciona un nombre válido después del comando /setname. Por ejemplo, envia un mensaje similar a este: /setname Pepito")
    # if we have name:
    else:
        #We look if the user is in the database. 
        peticion = api_url + f'/members/{message.chat.id}'
        response=None

        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers) 
        except Exception as e:
            print("Error durante la conexion con la base de datos:", e)
            return None
        
        # if the user is in the database we update the name.
        if response.status_code == 200:
            data = response.json()  # Si la respuesta es JSON   
            surname=data['surname']
            age=data['age']
            birthday=data['birthday']
            city=data['city']
            gender=data['gender']
            mail=data['mail']
            #We update the name in the database!             
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
            response=None

            try:
                # Realizar una petición POST con datos en el cuerpo
                response = requests.put(peticion, headers=headers,
                                          json =payload) 
            except Exception as e:
                print("Error durante la conexion con la base de datos:", e)
                return None
            # Verificar el código de respuesta
            if response.status_code == 201:
                data = response.json()  # Si la respuesta es JSON
                bot.reply_to(message, f"¡Hola, {name}! Tu nombre ha sido registrado correctamente.")
                bot.send_message(message.chat.id,message_change_personal_information)
            else:
                    print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
        else:
            print(f"Error en la solicitud. Código de respuesta: {response.status_code}")

        
            

@bot.message_handler(commands=['setgender'])
def set_gender(message):
    
    # Obtiene el nombre enviado por el usuario
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    gender = message.text.replace('/setgender', '').strip()
    if not gender:
        bot.reply_to(message, "Por favor, proporciona un genero válido después del comando /setgender.")
    
    
    else:
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto! 
        peticion = api_url + f'/members/{message.chat.id}'
        response=None
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers) 

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                # en caso de que si -> update y respuesta acorde 
                name=data['name']
                surname=data['surname']
                age=data['age']
                birthday=data['birthday']
                city=data['city']
                mail=data['mail']
                        
                
               
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
                                            json =payload) 

                # Verificar el código de respuesta
                if response.status_code == 201:
                        # La solicitud fue exitosa
                        data = response.json()  # Si la respuesta es JSON
                        bot.reply_to(message, f"Tu género ha sido registrado correctamente. Gracias por tu colaboración!")
                        bot.send_message(message.chat.id, "Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
                            "/setname [TU NOMBRE] ->  para definir tu nombre, \n"
                            "/setsurname  [TU APELLIDO] ->  para definir tu apellido, \n"+
                            "/setage [TU EDAD] -> Define tu edad, \n"+
                            "/setbirthday [YYYY-MM-DDT00:00:00] -> para definir tu cumpleaños, \n"+
                            "/setcity [TU CIUDAD] -> para definir tu ciudad, \n"+
                            "/setmail [TU EMAIL] -> para definir tu email, \n"+
                            "/setgender [NOBINARY or MALE or FEMALE or NOANSWER] -> para definir tu género. \n"+
                            "Esta información puede ser cambiada cuando quieras usando estos comandos.") 
                        print("Respuesta exitosa:", data) # data -> List[NewMembers]
                        # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
                print("Error durante la solicitud:", e)
 
 
@bot.message_handler(commands=['setmail'])
def set_mail(message):
    
    # Obtiene el nombre enviado por el usuario
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    mail = message.text.replace('/setmail', '').strip()
    if not mail:
        bot.reply_to(message, "Por favor, proporciona un email válido después del comando /setmail.")
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
                surname=data['surname']
                age=data['age']
                birthday=data['birthday']
                city=data['city']
                name=data['name']
                gender=data['gender']
                        
                
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
                                            json =payload) 

                # Verificar el código de respuesta
                if response.status_code == 201:
                        # La solicitud fue exitosa
                        data = response.json()  # Si la respuesta es JSON
                        print("Respuesta exitosa:", data) # data -> List[NewMembers]
                        bot.reply_to(message, f"Tu email ha sido registrado.")
                        bot.send_message(message.chat.id, message_change_personal_information)
                        # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
                print("Error durante la solicitud:", e)
                
 
@bot.message_handler(commands=['setbirthday'])
def set_gender(message):
    
    # Obtiene el nombre enviado por el usuario
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    birthday = message.text.replace('/setbirthday', '').strip()
    if not birthday:
        #TODO
        bot.reply_to(message, "Por favor, proporciona una fecha correcta válido después del comando /setbirthday.")
    else:
        bot.reply_to(message, f"Tu fecha de nacimiento ha sido registrado.")
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
                surname=data['surname']
                age=data['age']
                city=data['city']
                name=data['name']
                mail=data['mail']
                gender=data['gender']
                        
               
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
                                            json =payload) 

                # Verificar el código de respuesta
                if response.status_code == 201:
                        # La solicitud fue exitosa
                        data = response.json()  # Si la respuesta es JSON
                        print("Respuesta exitosa:", data) # data -> List[NewMembers]
                        bot.send_message(message.chat.id, message_change_personal_information)
                        # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                    print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
                    bot.send_message(message.chat.id, "Por favor, asegurate que la informacion esta bien. Debes introducir /setbirthday [YYYY-MM-DDT00:00:00], por ejemplo /setbirthday 2021-01-11T00:00:00 es un comando válido.")

        except Exception as e:
                print("Error durante la solicitud:", e)
             
                
@bot.message_handler(commands=['setage'])
def set_age(message):
    
    # Obtiene el nombre enviado por el usuario
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    age = message.text.replace('/setage', '').strip()
    if not age:
        bot.reply_to(message, "Por favor, proporciona un nombre válido después del comando /setage.")
    
    
    else:
        bot.reply_to(message, f"¡Hola! Tu edad ha sido registrado.")
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
                surname=data['surname']
                name=data['name']
                birthday=data['birthday']
                city=data['city']
                gender=data['gender']
                mail=data['mail']
                bot.send_message(message.chat.id, message_change_personal_information)
                        
                
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
                                            json =payload) 

                # Verificar el código de respuesta
                if response.status_code == 201:
                        # La solicitud fue exitosa
                        data = response.json()  # Si la respuesta es JSON
                        print("Respuesta exitosa:", data) # data -> List[NewMembers]
                        # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
                print("Error durante la solicitud:", e)
            


@bot.message_handler(commands=['setsurname'])
def set_surname(message):
    
    # Obtiene el nombre enviado por el usuario
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    surname = message.text.replace('/setsurname', '').strip()
    if not surname:
        bot.reply_to(message, "Por favor, proporciona un nombre válido después del comando /setsurname.")
    
    
    else:
        bot.reply_to(message, f"¡Hola! Tu apellido ha sido registrado.")
        # en caso de que no -> Le preguntamos informacion y explicamos de que es el proyecto! 
        peticion = api_url + f'/members/{message.chat.id}'
        try:
            # Realizar una petición POST con datos en el cuerpo
            response = requests.get(peticion, headers=headers) 

            # Verificar el código de respuesta
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()  # Si la respuesta es JSON
                name=data['name']
                age=data['age']
                birthday=data['birthday']
                city=data['city']
                gender=data['gender']
                mail=data['mail']
                        
                bot.send_message(message.chat.id, message_change_personal_information)
                
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
                                            json =payload) 

                # Verificar el código de respuesta
                if response.status_code == 201:
                        # La solicitud fue exitosa
                        data = response.json()  # Si la respuesta es JSON
                        print("Respuesta exitosa:", data) # data -> List[NewMembers]
                        # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
                print("Error durante la solicitud:", e)

@bot.message_handler(commands=['setcity'])
def set_city(message):
    
    # Obtiene el nombre enviado por el usuario
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    city = message.text.replace('/setcity', '').strip()
    if not city:
        bot.reply_to(message, "Por favor, proporciona una ciudad válida después del comando /setcity.")
    
    
    else:
        bot.reply_to(message, f"¡Hola! Tu ciudad ha sido registrado.")
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
                surname=data['surname']
                name=data['name']
                age=data['age']
                birthday=data['birthday']
                gender=data['gender']
                mail=data['mail']
                        
                bot.send_message(message.chat.id, message_change_personal_information)
                
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
                                            json =payload) 

                # Verificar el código de respuesta
                if response.status_code == 201:
                        # La solicitud fue exitosa
                        data = response.json()  # Si la respuesta es JSON
                        print("Respuesta exitosa:", data) # data -> List[NewMembers]
                        # bot.send_message(message.chat.id, "Respuesta exitosa")
                else:
                        print(f"Error en la solicitud. Código de respuesta: {response.status_code}")

        except Exception as e:
                print("Error durante la solicitud:", e)


           
#TODO aqui te tienes que fiar del usuario! 
# Envia una ubicación para pedir la recomendación!
@bot.message_handler(commands=['recomendacion','medicion'])
def enviar_localizacion(message):
    #TODO ver si tengo alguna recomendacion aceptada!
        #En caso de que si tenga - le recuerdas la ubicación 
    #En caso de que no tenga - le pedimos la ubicación y le damos las recomendaciones. 
    markup = types.ReplyKeyboardMarkup(row_width=1)
    bot.send_message(message.chat.id, "Lo primero que necesitamos es que nos envies tu localización")
    location_btn = types.KeyboardButton("Compartir ubicación", request_location=True)
    markup.add(location_btn)
    bot.send_message(message.chat.id, "Pulsa el botón para compartir tu ubicación:", reply_markup=markup)
    #TODO comentar al usuario que para darle una recomendacion puede simplemente enviarle la posicion y ya. 


#Ofrecemos al usuario la posibilidad de compartir su ubicación.
@bot.message_handler(content_types=['location'])
def handle_location(message):
    user=bot_auxiliar.existe_user(message.chat.id)
    info=           {
                    "member_current_location": {
                        "Longitude": message.location.longitude,
                        "Latitude": message.location.latitude
                    }  }
    if user is not None:
        # Aqui recomendation_aceptada[message.chat.id] deberia ser 0 
        rec= bot_auxiliar.recomendaciones_aceptadas(message.chat.id)
        #El usuario tiene recomendaciones aceptadas!
        if rec is not None:
            # Se supone que el usuario esta en la celda. 
            localizacion_user_recomendacion_Aceptada[message.chat.id]= info
            bot.reply_to(message, "Es momento de que envies la foto!")
            # else:
            #     # Si no esta dentro de la celda -> le recordamos donde debe hacer la foto!
            #     bot.reply_to(message, "La medicion la tienes que sacar aqui:")
            #     bot.send_location(chat_id=message.chat.id, latitude= rec['cell']['centre']['Latitude'], longitude=rec['cell']['centre']['Longitude'])
            #     return None
        else:
            # En caso de no tener ninguna recomendacion aceptada -> creamos una.
            campaign=bot_auxiliar.get_campaign_hive_1(message.chat.id)
            if campaign is not None:
                campaign_id=campaign['id']

                data=bot_auxiliar.recomendacion(id_user=message.chat.id, campaign_id=campaign_id, info=info )
                if data is not None and data!={'detail': 'far_away'} :    
                    #Eliminamos los datos anteriores guardados
                    recomendation_aceptada[message.chat.id]=0
                    last_recomendation_per_user[message.chat.id]=data['results']                    
                    #TODO! ExTEPCIONES
                    if len(data['results'])==0:
                        bot.send_message(message.chat.id, "No hay recomendaciones para ti en este momento. Lo sentimos.")
                    elif len(data['results'])==1:
                        markup = types.ReplyKeyboardMarkup(row_width=1)
                        option1 = types.KeyboardButton(f"Opción 1")# - lat {data['results'][0]['cell']['centre']['Latitude']} long{data['results'][0]['cell']['centre']['Longitude']}")
                        markup.add(option1)
                        bot.send_message(message.chat.id, "Dada tu ubicación aqui tenemos 1 recomendaciones para ti. Las tres opciones estan explicadas aquí! \n")
                        bot.send_message(message.chat.id, "Opción 1:")
                        bot.send_location(chat_id=message.chat.id, latitude= data['results'][0]['cell']['centre']['Latitude'], longitude=data['results'][0]['cell']['centre']['Longitude'])
                                            #TODO indicaciones para proximas intrucciones en cuestion de medicion. 
                        bot.send_message(message.chat.id, "Porfavor elija en el menu la que quieras realizar.", reply_markup=markup)
                                        
                    elif len(data['results'])==2:
                            markup = types.ReplyKeyboardMarkup(row_width=1)
                            option1 = types.KeyboardButton(f"Opción 1")# - lat {data['results'][0]['cell']['centre']['Latitude']} long{data['results'][0]['cell']['centre']['Longitude']}")
                            option2 = types.KeyboardButton(f"Opción 2")# - lat {data['results'][1]['cell']['centre']['Latitude']} long{data['results'][1]['cell']['centre']['Longitude']}")

                            markup.add(option1,option2)
                            print(markup.keyboard)
                            bot.send_message(message.chat.id, "Dada tu ubicación aqui tenemos 2 recomendaciones para ti. Las dos opciones estan explicadas aquí! \n")
                            bot.send_message(message.chat.id, "Opción 1:")
                            bot.send_location(chat_id=message.chat.id, latitude= data['results'][0]['cell']['centre']['Latitude'], longitude=data['results'][0]['cell']['centre']['Longitude'])
                            bot.send_message(message.chat.id, "Opción 2:")
                            bot.send_location(chat_id=message.chat.id, latitude= data['results'][1]['cell']['centre']['Latitude'], longitude=data['results'][1]['cell']['centre']['Longitude'])
                            bot.send_message(message.chat.id, "Porfavor elija en el menu la que quieras realizar.", reply_markup=markup)              
                    else:
                            markup = types.ReplyKeyboardMarkup(row_width=1)
                            option1 = types.KeyboardButton(f"Opción {1} ")#- lat {data['results'][0]['cell']['centre']['Latitude']} long{data['results'][0]['cell']['centre']['Longitude']}")
                            option2 = types.KeyboardButton(f"Opción {2}")# - lat {data['results'][1]['cell']['centre']['Latitude']} long{data['results'][1]['cell']['centre']['Longitude']}")
                            option3 = types.KeyboardButton(f"Opción {3}")# - lat {data['results'][2]['cell']['centre']['Latitude']} long{data['results'][2]['cell']['centre']['Longitude']}")
                            markup.add(option1,option2,option3)
                            print(markup.keyboard)
                            bot.send_message(message.chat.id, "Dada tu ubicación aqui tenemos 3 recomendaciones para ti. Las tres opciones estan explicadas aquí! \n")
                            bot.send_message(message.chat.id, "Opción 1:")
                            bot.send_location(chat_id=message.chat.id, latitude= data['results'][0]['cell']['centre']['Latitude'], longitude=data['results'][0]['cell']['centre']['Longitude'])
                            bot.send_message(message.chat.id, "Opción 2:")
                            bot.send_location(chat_id=message.chat.id, latitude= data['results'][1]['cell']['centre']['Latitude'], longitude=data['results'][1]['cell']['centre']['Longitude'])
                            bot.send_message(message.chat.id, "Opción 3:")
                            bot.send_location(chat_id=message.chat.id, latitude= data['results'][2]['cell']['centre']['Latitude'], longitude=data['results'][2]['cell']['centre']['Longitude'])              
                            bot.send_message(message.chat.id, "Porfavor elija en el menu la que quieras realizar.", reply_markup=markup)
                                        
                else:
                    bot.reply_to(message, "No hay posibles recomendaicones para ti en este momento. Lo sentimos.")
            else:
                bot.reply_to(message, "No hay campañas activas cerca de ti. Lo sentimos.")
    else:
        print("El usuario no esta registrado.")
        bot.reply_to(message, "Esta habiendo un problema, por favor envie el comando \start. Gracias!")        

@bot.message_handler(content_types=['photo'])
def handle_photo_and_location(message):
    # Verificar si el mensaje contiene una foto
    if message.photo:
        # Aquí puedes acceder a la información de la foto
        peticion = api_url +f"/members/{message.chat.id}/measurements"
        posicion_user= localizacion_user_recomendacion_Aceptada[message.chat.id]
        date= datetime.datetime.utcnow()
        measurement_creation={ 
                              "datetime": date.strftime( "%Y-%m-%dT%H:%M:%S"),
                              "location": {
                                "Longitude":posicion_user["member_current_location"]["Longitude"],
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
        response = requests.post(peticion, headers=headers, json=measurement_creation)
 

        if response.status_code == 201:
            data=response.json()
            number= recomendation_aceptada[message.chat.id]
            recomendacion_info=last_recomendation_per_user[message.chat.id][int(number)]
            lat=recomendacion_info['cell']['centre']['Latitude']
            long=recomendacion_info['cell']['centre']['Longitude']
            file_id = message.photo[-1].file_id
            recomendation_aceptada[message.chat.id]=0
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
                # Result - a writer object
                # Pass the data in the list as an argument into the writerow() function
                writer_object.writerow(data_csv)
                # Close the file object
                f_object.close()
            bot.reply_to(message, "¡Gracias por enviar la foto!")
            
        elif response.status_code == 404:
            bot.reply_to(message, "Esta recomendacion no es viable... ")
            print("Error en la medicion puede ser por que no halla ")
        else:
            print(f"Error en la solicitud de medicion. Código de respuesta: {response.status_code}")
 

# Dada la eleccion del usuario almacenamos su eleccion en la base de datos. 
@bot.message_handler(func=lambda message: message.text=="Opción 1" or message.text=="Opción 2" or message.text=="Opción 3")
def handle_option(message):
    user_choice = message.text
    if last_recomendation_per_user[message.chat.id] is not None:
        #Asegurate que sigue activa la recomendacion es decir si tiene aceptadas y no las ha realizado hay que corregiirlo. 
        #TODO  
        number = message.text.replace('Opción ', '').strip()

        print(number)
        #TODO verificar que esto existe! ademas que no se puede modificar una reocmendacion si ya hay alguna. 
        recomendation_aceptada[message.chat.id]=int(number) -1
        number=int(number)-1
        recomendacion_info=last_recomendation_per_user[message.chat.id][number]
        recommendation_id=recomendacion_info['recommendation']['id']
        bot.reply_to(message, f"Elegiste: {user_choice}. Gracias por tu elección. Cuando estes en el sitio porfavor da al comendo de tomat medicion")
        bot.reply_to(message, f"El bot a registrado tu intencion porfavor cuando estes en la posicion indica el comando ---")
        peticion = api_url +f"/members/{message.chat.id}/recommendations/{recommendation_id}"
        info= "ACCEPTED"  
        response=None
        try:
            #Se registramos la recomendacion acceptada por el usuario.
            response = requests.patch(peticion, headers=headers,json=info)
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json() 
                
            else:
                print(f"Error en la solicitud de update de la recomendation. Código de respuesta: {response.status_code}")        

        except Exception as e:
            print("Error durante la solicitud:", e)
        
    else:
        bot.reply_to(message, f"No hay recomendaciones para ti en este momento. Lo sentimos. Porfavor pide una recomendacion.")
    



from folium import plugins
from folium.utilities import image_to_url

@bot.message_handler(commands=['Map'])
def crear_mapa(message):
    #Tengo que pedir el centro de la camapaña- surface 
    peticion = api_url +f"/hives/1/campaigns/1/surfaces"
    try:
        #Se registramos la recomendacion acceptada por el usuario.
        response = requests.get(peticion, headers=headers)
        if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()
                
                surface_centre_lat=data['results'][0]['boundary']['centre']['Latitude']
                surface_centre_long=data['results'][0]['boundary']['centre']['Longitude']
                surface_radius=data['results'][0]['boundary']['radius']
                # peticion= api_url +f"/members/{message.chat.id}/measurements"

                mapa = folium.Map(location=[surface_centre_lat, surface_centre_long], zoom_start=18)
                print(surface_centre_lat, surface_centre_long)
                peticion = api_url +f"/hives/1/campaigns/show"
                try:
                                
                    #Se registramos la recomendacion acceptada por el usuario.
                    response = requests.get(peticion, headers=headers)
                    if response.status_code == 200:
                        df = pd.read_csv('src/Servicio/Telegram_bot/Pictures/CSVFILE.csv', names=['latitud', 'longitud', 'url_imagen'])
                            # Obtener el número de combinaciones diferentes de las dos primeras columnas
                        grupos = df.groupby(['latitud', 'longitud'])['url_imagen'].apply(list).reset_index()
                        for index, row in grupos.iterrows():
                            combinacion = (row['latitud'], row['longitud'])
                            datos_tercera_columna = row['url_imagen']
                            n_files=len(datos_tercera_columna)
                            grados= 360/n_files
                            # d= math.sqrt(2*(surface_radius/2)**2)/1000
                            for i in range(0,n_files):
                                tamano_imagen= min(95 * 2 ** (18 - 10), 150)
                                # lat, long = bot_auxiliar.get_point_at_distance(lat1=combinacion[0], lon1=combinacion[1], bearing=i*grados, d=d)
                                lat, long= combinacion[0], combinacion[1]
                                if 0<=i*grados and 90>i*grados:
                                    print("de 0 a 90 grados")
                                    folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(100,100))).add_to(mapa)
                                    # marcador= agregar_imagen(mapa, lat, long, datos_tercera_columna[i], surface_radius,alineacion=(100,100))
                                    # marcador.add_to(mapa)   
                                elif 90<=i*grados and 180>i*grados:
                                    print("de 90 a 180")
                                    folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(100,0))).add_to(mapa)

                                    # marcador=agregar_imagen(mapa, lat, long, datos_tercera_columna[i], surface_radius,alineacion=(100,0))
                                    # marcador.add_to(mapa)
                                elif 180<=i*grados and 270>i*grados:
                                    print("de 180 a 270")
                                    folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(0,0))).add_to(mapa)

                                    # marcadr=agregar_imagen(mapa, lat,long, datos_tercera_columna[i], surface_radius,alineacion=(0,0))
                                    # mapa.get_root().html.add_child(marcador)
                                else:
                                    print("de 270 a 360")
                                    folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95),icon_anchor=(0,100))).add_to(mapa)

                                    # marcador=agregar_imagen(mapa, lat, long, datos_tercera_columna[i], surface_radius,alineacion=(0,100))
                                    # mapa.get_root().html.add_child(marcador)
                                df = pd.read_csv('src/Servicio/Telegram_bot/Pictures/DATAMAP.csv',names=["list_point", "id_user", "Cardinal_actual", "expected_measurements","color_number"])
                                for index, row in df.iterrows():
                                        list_point=json.loads(row["list_point"])
                                        id_user=row["id_user"]
                                        Cardinal_actual=row["Cardinal_actual"]
                                        excepted_measurements=row["expected_measurements"]
                                        # color_number=str(row[4])
                                    
                                        folium.Polygon(locations=list_point, color='black', fill=False,
                                                            weight=1, popup=(folium.Popup(str(id_user))), opacity=0.5, fill_opacity=0.2).add_to(mapa)
                                        
                                        folium.Marker(list_point[3],popup=f"Number of Expected measurements: {str(excepted_measurements)}",
                                                icon=DivIcon(
                                                    icon_size=(200, 36),
                                                    icon_anchor=(0, 0),
                                                    html=f'<div style="font-size: 20pt;">{str(Cardinal_actual)}</div>'
                                                )).add_to(mapa)


                                            # coordenadas = (lat,long)
                                            # ubicaciones.add(coordenadas)
                                    # mapa.save('map_antes_de_otro.html')
                        mapa.save('map.html')
                        print("Hemos terminado el mapa! ")
                        with open("map.html", "rb") as map_file:

                                        bot.send_document(message.chat.id, map_file, caption="Tu Mapa")
                            
                    else:
                                    print(f"Error en la solicitud de update de la recomendation. Código de respuesta: {response.status_code}")             
                except Exception as e:
                                print("Error durante la solicitud:", e)         

                # grupo_imagenes = folium.FeatureGroup(name='Imágenes')
                # mapa.add_child(grupo_imagenes)

        else:
                print(f"Error en la solicitud de update de la recomendation. Código de respuesta: {response.status_code}")        
   
    except Exception as e:
        print("Error durante la solicitud:", e)
    
    
    
import math 
import json

# def crear_collage(mapa, surface_radius):
#     # ubicaciones = set()  # Conjunto para rastrear las ubicaciones ya procesadas
#     df = pd.read_csv('src/Servicio/Telegram_bot/Pictures/CSVFILE.csv', names=['latitud', 'longitud', 'url_imagen'])
#         # Obtener el número de combinaciones diferentes de las dos primeras columnas
#     grupos = df.groupby(['latitud', 'longitud'])['url_imagen'].apply(list).reset_index()
#     for index, row in grupos.iterrows():
#         combinacion = (row['latitud'], row['longitud'])
#         datos_tercera_columna = row['url_imagen']
#         n_files=len(datos_tercera_columna)
#         grados= 360/n_files
#         # d= math.sqrt(2*(surface_radius/2)**2)/1000
#         for i in range(0,n_files):
#             tamano_imagen= min(95 * 2 ** (18 - 10), 150)
#             # lat, long = bot_auxiliar.get_point_at_distance(lat1=combinacion[0], lon1=combinacion[1], bearing=i*grados, d=d)
#             lat, long= combinacion[0], combinacion[1]
#             if 0<=i*grados and 90>i*grados:
#                 print("de 0 a 90 grados")
#                 folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(100,100))).add_to(mapa)
#                 # marcador= agregar_imagen(mapa, lat, long, datos_tercera_columna[i], surface_radius,alineacion=(100,100))
#                 # marcador.add_to(mapa)   
#             elif 90<=i*grados and 180>i*grados:
#                 print("de 90 a 180")
#                 folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(100,0))).add_to(mapa)

#                 # marcador=agregar_imagen(mapa, lat, long, datos_tercera_columna[i], surface_radius,alineacion=(100,0))
#                 # marcador.add_to(mapa)
#             elif 180<=i*grados and 270>i*grados:
#                 print("de 180 a 270")
#                 folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95), icon_anchor=(0,0))).add_to(mapa)

#                 # marcadr=agregar_imagen(mapa, lat,long, datos_tercera_columna[i], surface_radius,alineacion=(0,0))
#                 # mapa.get_root().html.add_child(marcador)
#             else:
#                 print("de 270 a 360")
#                 folium.Marker(location=[lat, long], icon=folium.CustomIcon(icon_image=datos_tercera_columna[i], icon_size=(95, 95),icon_anchor=(0,100))).add_to(mapa)

#                 # marcador=agregar_imagen(mapa, lat, long, datos_tercera_columna[i], surface_radius,alineacion=(0,100))
#                 # mapa.get_root().html.add_child(marcador)
#     df = pd.read_csv('src/Servicio/Telegram_bot/Pictures/DATAMAP.csv',names=["list_point", "id_user", "Cardinal_actual", "expected_measurements","color_number"])
#     for index, row in df.iterrows():
#         list_point=json.loads(row["list_point"])
#         id_user=row["id_user"]
#         Cardinal_actual=row["Cardinal_actual"]
#         excepted_measurements=row["expected_measurements"]
#         # color_number=str(row[4])
       
#         folium.Polygon(locations=list_point, color='black', fill=False,
#                             weight=1, popup=(folium.Popup(str(id_user))), opacity=0.5, fill_opacity=0.2).add_to(mapa)
        
#         folium.Marker(list_point[3],popup=f"Number of Expected measurements: {str(excepted_measurements)}",
#                 icon=DivIcon(
#                     icon_size=(200, 36),
#                     icon_anchor=(0, 0),
#                     html=f'<div style="font-size: 20pt;">{str(Cardinal_actual)}</div>'
#                 )).add_to(mapa)


#             # coordenadas = (lat,long)
#             # ubicaciones.add(coordenadas)
#     # mapa.save('map_antes_de_otro.html')
#     mapa.save('map.html')
#     print("Hemos terminado el mapa! ")
#     with open("mapa.html", "rb") as map_file:

#         bot.send_document(message.chat.id, map_file, caption="Tu Mapa")

#     return mapa


if __name__ == "__main__":
    # test_bot = bot_send_text('¡Hola, Telegram!')
    bot.polling()
    
    
    # user = bot.get_me()
    # print(user)
    # #Es equivalente a esto 
    # #https://api.telegram.org/bot<TU_TOKEN>/getMe
    # # Saber información de los grupos del Bot
    # updates = bot.get_updates()
    # print(updates)
    #Es equivalente a esto 
    #https://api.telegram.org/bot<TU_TOKEN/getUpdates
