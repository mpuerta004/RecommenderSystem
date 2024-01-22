import requests
import telebot 
from telebot import types
from enum import Enum
import random 
import datetime 


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
                        bot.send_message(message.chat.id, "Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
                            "/setname [TU NOMBRE] ->  para definir tu nombre, \n"
                            "/setsurname  [TU APELLIDO] ->  para definir tu apellido, \n"+
                            "/setage [TU EDAD] -> Define tu edad, \n"+
                            "/setbirthday [YYYY-MM-DDT00:00:00] -> para definir tu cumpleaños, \n"+
                            "/setcity [TU CIUDAD] -> para definir tu ciudad, \n"+
                            "/setmail [TU EMAIL] -> para definir tu email, \n"+
                            "/setgender [NOBINARY or MALE or FEMALE or NOANSWER] -> para definir tu género. \n"+
                            "Esta información puede ser cambiada cuando quieras usando estos comandos.") 
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
                        bot.send_message(message.chat.id, "Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
                            "/setname [TU NOMBRE] ->  para definir tu nombre, \n"
                            "/setsurname  [TU APELLIDO] ->  para definir tu apellido, \n"+
                            "/setage [TU EDAD] -> Define tu edad, \n"+
                            "/setbirthday [YYYY-MM-DDT00:00:00] -> para definir tu cumpleaños, \n"+
                            "/setcity [TU CIUDAD] -> para definir tu ciudad, \n"+
                            "/setmail [TU EMAIL] -> para definir tu email, \n"+
                            "/setgender [NOBINARY or MALE or FEMALE or NOANSWER] -> para definir tu género. \n"+
                            "Esta información puede ser cambiada cuando quieras usando estos comandos.") 
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
                bot.send_message(message.chat.id, "Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
                            "/setname seguido de tu nombre para definir tu nombre, \n"
                            "/setsurname seguido de tu apellido para definir tu apellido, \n"+
                            "/setage seguido de tu edad para definir tu edad, \n"+
                            "/setbirthday seguido de tu fecha de nacimiento para definir tu cumpleaños, \n"+
                            "/setcity  seguido de tu cuidad para definir tu ciudad, \n"+
                            "/setmail seguido de tu email para definir tu email, \n"+
                            "/setgender seguido de 'NOBINARY','MALE','FEMALE','NOANSWER' para definir tu género. \n"+
                            "Esta información puede ser cambiada cuando quieras.") 
                        
                
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
                        
                bot.send_message(message.chat.id, "Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
                            "/setname seguido de tu nombre para definir tu nombre, \n"
                            "/setsurname seguido de tu apellido para definir tu apellido, \n"+
                            "/setage seguido de tu edad para definir tu edad, \n"+
                            "/setbirthday seguido de tu fecha de nacimiento para definir tu cumpleaños, \n"+
                            "/setcity  seguido de tu cuidad para definir tu ciudad, \n"+
                            "/setmail seguido de tu email para definir tu email, \n"+
                            "/setgender seguido de 'NOBINARY','MALE','FEMALE','NOANSWER' para definir tu género. \n"+
                            "Esta información puede ser cambiada cuando quieras.") 
                
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
                        
                bot.send_message(message.chat.id, "Te recuerdo que puedes modificar tus datos personales con los siguientes comandos:\n" +
                            "/setname seguido de tu nombre para definir tu nombre, \n"
                            "/setsurname seguido de tu apellido para definir tu apellido, \n"+
                            "/setage seguido de tu edad para definir tu edad, \n"+
                            "/setbirthday seguido de tu fecha de nacimiento para definir tu cumpleaños, \n"+
                            "/setcity  seguido de tu cuidad para definir tu ciudad, \n"+
                            "/setmail seguido de tu email para definir tu email, \n"+
                            "/setgender seguido de 'NOBINARY','MALE','FEMALE','NOANSWER' para definir tu género. \n"+
                            "Esta información puede ser cambiada cuando quieras.") 
                
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
@bot.message_handler(commands=['recomendacion'])
def enviar_localizacion(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    location_btn = types.KeyboardButton("Compartir ubicación", request_location=True)
    markup.add(location_btn)
    bot.send_message(message.chat.id, "Pulsa el botón para compartir tu ubicación:", reply_markup=markup)
    #TODO comentar al usuario que para darle una recomendacion puede simplemente enviarle la posicion y ya. 


#Ofrecemos al usuario la posibilidad de compartir su ubicación.
@bot.message_handler(content_types=['location'])
def handle_location(message):
    
    #Si el usuario ya esta registrado o no! 
    peticion = api_url + f'/members/{message.chat.id}'
    try:
        # Realizar una petición POST con datos en el cuerpo
        response = requests.get(peticion, headers=headers) 
    
        # Verificar el código de respuesta
        if response.status_code == 200:
            # La solicitud fue exitosa -> el usuario esta en l abase de datos! 
            user_info = response.json()  # Si la respuesta es JSON
            # print("Respuesta exitosa:", data) # data -> Member
            
            info=           {
            "member_current_location": {
                "Longitude": message.location.longitude,
                "Latitude": message.location.latitude
            }
            }
            #Aqui hay que ver si recomendaciones aceptadas cerca de la posicion. 
            peticion = api_url + f"/members/{message.chat.id}/recommendations"
            response = requests.get(peticion, headers=headers)
        
            if response.status_code == 200:
                data_recomendaciones = response.json()
                print(data_recomendaciones)
                if len(data_recomendaciones['results'])>0:
                    for i in data_recomendaciones['results']:
                        if i['state'] =="ACCEPTED":
                        #hay una peticion aceptada! entonces tenemos que ver si el usuario esta cerca de aqui 
                            localizacion_user_recomendacion_Aceptada[message.chat.id]= info
                            bot.reply_to(message, "Esperamos la foto en el sitio! Gracias por tu colaboración!")
                            return None
                        else:
                                # En caso de no tener ninguna recomendacion aceptada -> creamos una.
                                peticion = api_url +"/hives/1/campaigns"
                                response = requests.get(peticion, headers=headers)
                                if response.status_code == 200:
                                    # La solicitud fue exitosa
                                    data = response.json() 
                                    a=len(data['results'])
                                    elemento=random.randint(0,a-1)
                                    campaign_id=data['results'][elemento]['id']
                                    peticion = api_url + f'/members/{message.chat.id}/campaigns/{campaign_id}/recommendations'
                                    
                                    response = requests.post(peticion, headers=headers,json=info) 
                                    # Verificar el código de respuesta
                                    if response.status_code == 201:
                                        # La solicitud fue exitosa
                                        # 
                                        data = response.json() 
                                        #Coger del data las posiciones de cada recomendacion! 
                                        last_recomendation_per_user[message.chat.id]=data['results']
                                        recomendation_aceptada[message.chat.id]=0
                                        
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
                                        print(f"Error en la solicitud de campañas. Código de respuesta: {response.status_code}")        
                                else:
                                    print(f"Error en la solicitud de campañas. Código de respuesta: {response.status_code}")
                        
                else:
                        # En caso de no tener ninguna recomendacion aceptada -> creamos una.
                        peticion = api_url +"/hives/1/campaigns"
                        response = requests.get(peticion, headers=headers)
                        if response.status_code == 200:
                            # La solicitud fue exitosa
                            data = response.json() 
                            a=len(data['results'])
                            elemento=random.randint(0,a-1)
                            campaign_id=data['results'][elemento]['id']
                            peticion = api_url + f'/members/{message.chat.id}/campaigns/{campaign_id}/recommendations'
                            
                            response = requests.post(peticion, headers=headers,json=info) 
                            # Verificar el código de respuesta
                            if response.status_code == 201:
                                # La solicitud fue exitosa
                                # 
                                data = response.json() 
                                #Coger del data las posiciones de cada recomendacion! 
                                last_recomendation_per_user[message.chat.id]=data['results']
                                recomendation_aceptada[message.chat.id]=0
                                
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
                                print(f"Error en la solicitud de campañas. Código de respuesta: {response.status_code}")        
                        else:
                            print(f"Error en la solicitud de campañas. Código de respuesta: {response.status_code}")
                        
            else:
                print(f"Error en la solicitud de campañas. Código de respuesta: {response.status_code}")        
            
           
        else:
            print("El usuario no existe -> No deberia pasar")
    except Exception as e:
        print("Error durante la solicitud:", e)
        
    # recomendaciones=create_recomendation_per_campaign(db=db,member_id=user_class.id,recipe_in=a,campaign_id=campaign_id,time=time)
    # Aquí puedes realizar acciones con la ubicación recibida, como guardarla o procesarla
    # bot.reply_to(message, f"Recibí tu ubicación: Latitud {latitude}, Longitud {longitude}")
   


@bot.message_handler(content_types=['photo'])
def handle_photo_and_location(message):
    # Verificar si el mensaje contiene una foto
    if message.photo:
        # Aquí puedes acceder a la información de la foto
        photo = message.photo[-1]  # Obtén la última foto, que suele ser la de mayor resolución
        file_id = photo.file_id

        # Puedes utilizar file_id para descargar la foto o realizar otras acciones según tus necesidades
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Puedes imprimir información adicional si lo deseas
        print(f"File ID: {file_id}")
        print(f"File Path: {file_path}")
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
            response.json()
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
        recomendation_aceptada[message.chat.id]=number
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
