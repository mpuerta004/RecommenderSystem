
import math
import json
import requests
import telebot
from Telegram_bot.Token  import TOKEN
from telebot import types
import datetime
from csv import writer
import folium
import threading
from folium import plugins
from schemas.Recommendation import RecommendationCreate, RecommendationUpdate, RecommendationSearchResults
from schemas.Measurement import MeasurementCreate, MeasurementUpdate, MeasurementSearchResults
from IPython.display import display
import csv
from folium.features import DivIcon
from Telegram_bot import bot_auxiliar
import pandas as pd
from folium import plugins
from folium.utilities import image_to_url
import subprocess
from fastapi_utils.session import FastAPISessionMaker
import deps
# from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import crud
import io
from PIL import Image


# from sqlalchemy.orm import Session
# from schemas.Member import MemberCreate, MemberUpdate, MemberSearchResults
# from schemas.Recommendation import RecommendationCreate, RecommendationUpdate, RecommendationSearchResults
# from schemas.last_user_position import Last_user_positionCreate, Last_user_positionUpdate, Last_user_positionSearchResults
# from schemas.Measurement import MeasurementCreate, MeasurementUpdate, MeasurementSearchResults

from Telegram_bot.usuario import User
from Telegram_bot.measurement_bot import Measurement_bot
# Ponemos nuestro Token generado con el @BotFather
bot = telebot.TeleBot(TOKEN)
from telebot.types import ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove


api_url = 'http://mve:8001'
list_users= {}

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


# Manejar el comando /start ->
@bot.message_handler(commands=['start'])
def start(message):
    global list_users  # Declaramos que vamos a usar la variable global

    bot.send_chat_action(message.chat.id, 'typing')

    # We want to look if the user is already in the database or not!
    peticion = api_url + f'/members/{message.chat.id}'
    try:
        response = requests.get(peticion, headers=headers)
        # CASE (user exists in the database).c-> tenemos sus datos! 
        if response.status_code == 200:
            data = response.json()  # data -> user information -> Member
            chat_id=data['id']
            #Si esta creado el objeto de este usuario en la lista de usuarios, no lo creamos de nuevo y sino se creara! 
            User(chat_id=message.chat.id,list_users=list_users,data=data)
            user=list_users[message.chat.id]
            markup=ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Wellcome back {user.name}!",reply_markup=markup)
            #TODO
            # explain_interaction(message)
        # CASE NEW USER
        else:
            data=bot_auxiliar.new_new_user(message=message)
            if data != None:
                # We have to insert a device in the dataset for the user and also relate the user with the device.
                User(chat_id=message.chat.id,list_users=list_users)
                markup=ReplyKeyboardRemove()
                bot.send_message(message.chat.id, f"Hello! I am the MVE bot. Vamos a conocernos un poco!",reply_markup=markup)
                markup=ForceReply()
                msg=bot.send_message(message.chat.id, "Como te llamas?", reply_markup=markup) 
                bot.register_next_step_handler(msg, registrar_nombre) 
            else:
                print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
                bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314. Wait few minutes and try again.")
    
    except Exception as e:
        print("Error durante la conexion con la base de datos:", e)
        bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")


@bot.message_handler(commands=['personal_information'])
def personal_information(message):
    markup=ReplyKeyboardRemove()
    user=list_users[message.chat.id]
    texto='<code>Actual information:</code>\n'
    texto+=f"<code>NAME...:</code> {user.name}\n"
    texto+=f"<code>SURNAME:</code> {user.surname}\n"
    texto+=f"<code>AGE....:</code> {user.age}\n"
    texto+=f"<code>MAIL...:</code> {user.mail}\n"
    texto+=f"<code>GENDER.:</code> {user.gender}\n"
    bot.send_message(message.chat.id, texto,parse_mode="html",reply_markup=markup)
        
    markup=ReplyKeyboardMarkup(one_time_keyboard=True, 
                                       input_field_placeholder="Do you want to change it?",
                                       resize_keyboard=True)
    markup.add('Yes','No')

    msg=bot.send_message(message.chat.id, "Do you want to change it?", reply_markup=markup) 
    bot.register_next_step_handler(msg, change_personal_information) 
    
    
def change_personal_information(message):
    chat_id= message.chat.id 
    if chat_id not in list(list_users.keys()):
        bot.send_message(message.chat.id, "Please first introduce /start command")
    else:
        if message.text != "Yes" and message.text != "No":
            bot.send_message(message.chat.id, "Please provide a valid answer")
            markup=ReplyKeyboardMarkup(one_time_keyboard=True, 
                                        input_field_placeholder="Do you want to change it?",
                                        resize_keyboard=True)
            markup.add('Yes','No')

            msg=bot.send_message(message.chat.id, "Do you want to change it?", reply_markup=markup) 
            bot.register_next_step_handler(msg, change_personal_information) 
        else:
            if message.text=="Yes":
                markup=ForceReply()
                msg=bot.send_message(message.chat.id, "Cual es tu nombre?", reply_markup=markup) 
                bot.register_next_step_handler(msg, registrar_nombre)
            else:
                markup=ReplyKeyboardRemove()
                bot.send_message(message.chat.id, "Ok, no problem",reply_markup=markup)
                return None


def registrar_nombre(message):
    global list_users  # Declaramos que vamos a usar la variable global

    global list_users  # Declaramos que vamos a usar la variable global
    bot.send_chat_action(message.chat.id, 'typing')
	#aqui en message.text tenemos la info del nombre. 
    nombre=message.text
    if type(nombre) != str or nombre == "":
        markup=ReplyKeyboardRemove()
        msg=bot.reply_to(message, "Please provide a valid name",reply_markup=markup)
        bot.register_next_step_handler(msg, registrar_nombre) 

    # if we have name:
    else:
        # We look if the user is in the database.
        set_name=bot_auxiliar.set_name(member_id=message.chat.id, name=nombre)
        if set_name != None :
            user=list_users[message.chat.id]
            user.set_name( name=nombre,list_users=list_users)
            print(list_users[message.chat.id])
            markup=ForceReply()
            msg=bot.send_message(message.chat.id, "Cual es tu apellido?", reply_markup=markup) 
            bot.register_next_step_handler(msg, registrar_apellido) 
            
        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
            return None
    


def registrar_apellido(message):
    global list_users  # Declaramos que vamos a usar la variable global

    bot.send_chat_action(message.chat.id, 'typing')
    surname=message.text
    if type(surname) != str or surname == "":
        msg=bot.reply_to(message, "Please provide a valid surname")
        bot.register_next_step_handler(msg, registrar_apellido) 

    # if we have name:
    else:
        set_name=bot_auxiliar.set_surname(member_id=message.chat.id, surname=surname)
        if set_name != None :
            user=list_users[message.chat.id]
            user.set_surname(surname=surname,list_users=list_users)
            markup=ForceReply()
            msg=bot.send_message(message.chat.id, "Cual es tu edad?", reply_markup=markup) 
            bot.register_next_step_handler(msg, registrar_edad) 
           
        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
            return None
    
def registrar_edad(message):
    global list_users  # Declaramos que vamos a usar la variable global
    bot.send_chat_action(message.chat.id, 'typing')

	#aqui en message.text tenemos la info del nombre. 
    age=message.text
    if message.text.isdigit() == False or int(message.text) < 0 or int(message.text) > 120:
        msg=bot.reply_to(message, "Please provide a valid age")
        bot.register_next_step_handler(msg, registrar_edad) 

    # if we have name:
    else:
        # We look if the user is in the database.
        set_name=bot_auxiliar.set_age(member_id=message.chat.id, age=age)
        if set_name != None :
            user=list_users[message.chat.id]
            user.set_age( age=age,list_users=list_users)
            markup=ForceReply()
            msg=bot.send_message(message.chat.id, "Cual es tu mail?", reply_markup=markup) 
            bot.register_next_step_handler(msg, registrar_email) 
           
        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
            return None


def registrar_email(message):
    global list_users  # Declaramos que vamos a usar la variable global

    bot.send_chat_action(message.chat.id, 'typing')

    mail=message.text
    if type(mail) != str or mail == "":
        bot.reply_to(message, "Please provide a valid mail")
        bot.register_next_step_handler(msg, registrar_email) 

    # if we have name:
    else:
        # We look if the user is in the database.
        set_name=bot_auxiliar.set_mail(member_id=message.chat.id, mail=mail)
        if set_name != None :
            user=list_users[message.chat.id]
            user.set_mail(mail=mail,list_users=list_users)
            markup=ReplyKeyboardMarkup(one_time_keyboard=True, 
                                       input_field_placeholder="Selecciona tu Genero",
                                       resize_keyboard=True)
            markup.add("NO BINARY","MALE","FEMALE",'NO ANSWER')

            msg=bot.send_message(message.chat.id, "Cual es tu genero?", reply_markup=markup) 
            bot.register_next_step_handler(msg, registrar_genero) 
           
        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
            return None   
        
def registrar_genero(message):
    global list_users  # Declaramos que vamos a usar la variable global

    bot.send_chat_action(message.chat.id, 'typing')

    gender=message.text
    if gender not in ["NO BINARY","MALE","FEMALE",'NO ANSWER']:
        bot.reply_to(message, "Please provide a valid gender")
        markup=ReplyKeyboardMarkup(one_time_keyboard=True, 
                                       input_field_placeholder="Selecciona tu Genero",
                                       resize_keyboard=True)
        markup.add("NO BINARY","MALE","FEMALE",'NO ANSWER')

        msg=bot.send_message(message.chat.id, "Cual es tu genero?", reply_markup=markup) 
        bot.register_next_step_handler(msg, registrar_genero)
    # if we have name:
    else:
        # We look if the user is in the database.
        if gender=="NO BINARY":
            gender_transformate="NOBINARY"
        elif gender=="NO ANSWER":
            gender_transformate="NOANSWER"
        else:
            gender_transformate=gender
        set_name=bot_auxiliar.set_gender(member_id=message.chat.id, gender=gender_transformate)
        if set_name != None :
            markup=ReplyKeyboardRemove()
            user=list_users[message.chat.id]
            user.set_gender( gender=gender_transformate,list_users=list_users)
            texto='<code>Datos introducidos:</code>\n'
            texto+=f"<code>NAME...:</code> {user.name}\n"
            texto+=f"<code>SURNAME:</code> {user.surname}\n"
            texto+=f"<code>AGE....:</code> {user.age}\n"
            texto+=f"<code>MAIL...:</code> {user.mail}\n"
            texto+=f"<code>GENDER.:</code> {user.gender}\n"
            bot.send_message(message.chat.id, texto,parse_mode="html", reply_markup=markup)

            

        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
            return None   




# Envia una ubicación para pedir la recomendación!
@bot.message_handler(commands=['recommendation'])
def recommendation(message):
    bot.send_chat_action(message.chat.id, 'typing')

    user=list_users[message.chat.id]
    member_2 = bot_auxiliar.existe_user(id_user=message.chat.id)
    if user != None and member_2 != None:
        # TODO si tienes la ubicacion en tiempo real esto no te deberia hacer falta pero no se como encontrar la ubicacion en tiempo real actualizada. De todos modos solo habria que eliminar esta pregunta de pedirle la ubicación. 
        # response=bot_auxiliar.get_recomendacion(id_user=message.chat.id)
        # for i in range(response['results']):
        #     if response['results'][i]['state']=="ACCEPTED":
        #         list_users[message.chat.id].recommendations_aceptada.append(response['results'][i])
        if list_users[message.chat.id].recommendations_aceptada==[]:
            list_users[message.chat.id].recommendations=[]
            markup = ReplyKeyboardMarkup(one_time_keyboard=True, 
                                        input_field_placeholder="Enviar tu ubicación",
                                        resize_keyboard=True)
            location_btn = types.KeyboardButton("Enviar ubicación",request_location=True)
            markup.add(location_btn)
            
            msg=bot.send_message(message.chat.id, "To begin, please share your location by pressing the button below. If you don't see it, please press the button before the clip button.", reply_markup=markup)
            #in the case we have the last position we delete this information! 
            
            
            bot.register_next_step_handler(msg, crear_la_Recomendacion) 
        else:
            markup=ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "You have already accepted a recommendation. Please first finish the measurement before requesting a new recommendation. I will send you the location of the recomendation",reply_markup=markup)
            rec_Accepted=list_users[message.chat.id].recommendations_aceptada
            bot.send_location(chat_id=message.chat.id, latitude=rec_Accepted.point['Latitude'], longitude=rec_Accepted.point['Longitude'])
            
        
    else: 
        bot.reply_to(message, "Please first send the command /start to be added to the database. Thank you!")
    

def crear_la_Recomendacion(message):
    
    #El uusario ha enviado la ubicación debemos crear la recomendación
    # message.text="location"
    # print(message.location.live_period)
    # time.sleep(2* 60)
    # print(message.location.live_period)
    
    campaign = bot_auxiliar.get_campaign_hive_1(message.chat.id)
    if campaign is not None:
        campaign_id = campaign['id'] 
        info = {
            "member_current_location": {
                "Longitude": message.location.longitude,
                "Latitude": message.location.latitude
            }} 
        data = bot_auxiliar.recomendacion_2(
        id_user=message.chat.id, campaign_id=campaign_id, info=info)
        if data is not None and data!={"detail": "Incorrect_user_campaign"} and data != {'detail': 'far_away'} and data != {'details': 'Incorrect_user_role'} and data != {"detail": "no_measurements_needed"}:
            locations = []
            if len(data['results']) == 0:
                markup=ReplyKeyboardRemove()

                bot.send_message(
                            message.chat.id, "There are currently no recommendations available for you. We apologize for the inconvenience.",reply_markup=markup)     
                                       
            else:
                markup=ReplyKeyboardMarkup(one_time_keyboard=True, 
                                       input_field_placeholder="Selecciona la recomendación",
                                       resize_keyboard=True)
                recommendations=[]
                for i in range(0,len(data['results'])):
                    point = data['results'][i]['cell']['centre']
                    
                    recomendation= RecommendationCreate(id=data['results'][i]['recommendation']['id'],member_id=message.chat.id, posicion=str(i), state="NOTIFIED",point={"Longitude":point['Longitude'],"Latitude":point['Latitude']})
                    
                    locations=locations+[{"latitude":point['Latitude'],"longitude":point['Longitude'],"title":f"Recommendation {i}"}]
                    markup.add(f"Recommendation {i}")
                    
                    recommendations.append(recomendation)
                    
                    # Generar el mapa con folium
                map = folium.Map(location=[message.location.latitude, message.location.longitude], zoom_start=17)
                user=list_users[message.chat.id]
                list_users[message.chat.id].recommendations=recommendations 
                user.recommendations=recommendations
                
                    # Añadir marcador para la ubicación del usuario
                folium.Marker(
                    [message.location.latitude, message.location.longitude],
                        popup="You are here",
                        icon=folium.Icon(color="blue")
                    ).add_to(map)

                    # Añadir marcadores para las localizaciones predefinidas
                for loc in locations:
                        folium.Marker(
                            [loc["latitude"], loc["longitude"]],
                            popup=loc["title"]
                        ).add_to(map)

                    # Guardar el mapa en un objeto BytesIO
                 # Guardar el mapa en un archivo local para depuración
                map.save("map.html")
                # Enviar el mapa al usuario
                # try:
                map_path = f'recommendation{message.chat.id}.html'
                map.save(map_path)
                with open(map_path, 'rb') as map_file:
                        msg=bot.send_document(message.chat.id, document=map_file,reply_markup=markup)
                        bot.register_next_step_handler(msg, user_select_recomendations) 

                        
                # except Exception as e:
                #     print(f"Failed to send photo: {e}")
                # bot.register_next_step_handler(msg, user_select_recomendations) 
        else:
            markup=ReplyKeyboardRemove()

            msg=bot.send_message(message, "Unfortunately, there are no recommendations available for you at this time. We apologize for the inconvenience.",reply_markup=markup)

            
def user_select_recomendations(message):
    a=message.text
    recommendation=list_users[message.chat.id].recommendations[int(a[-1])]
    list_users[message.chat.id].recommendations=[]
    list_users[message.chat.id].recommendations_aceptada=[]
    list_users[message.chat.id].recommendations_aceptada.append(recommendation)
    print(message.text)
    print(recommendation)
    accepted_recomendation=bot_auxiliar.update_recomendation(id_user=message.chat.id, recomendation_id=recommendation.id)
    markup=ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"¨Porfavor cuando llegues al punto seleccionado utiliza el comando /upload_photo",reply_markup=markup)
    bot.send_message(message.chat.id, f"Te recuerdo que la ubicacion a la que tienes que ir para sacar la foto es la siguiente",reply_markup=markup)
    bot.send_location(chat_id=message.chat.id, latitude=recommendation.point['Latitude'], longitude=recommendation.point['Longitude'])


@bot.message_handler(commands=['upload_photo'])
def medicion(message):
    bot.send_chat_action(message.chat.id, 'typing')
    user=list_users[message.chat.id]
    member_2 = bot_auxiliar.existe_user(id_user=message.chat.id)
    if user != None and member_2 != None:
        # TODO si tienes la ubicacion en tiempo real esto no te deberia hacer falta pero no se como encontrar la ubicacion en tiempo real actualizada. De todos modos solo habria que eliminar esta pregunta de pedirle la ubicación. 
        # response=bot_auxiliar.get_recomendacion(id_user=message.chat.id)
        # for i in range(response['results']):
        #     if response['results'][i]['state']=="ACCEPTED":
        #         list_users[message.chat.id].recommendations_aceptada.append(response['results'][i])
        if list_users[message.chat.id].recommendations_aceptada!=[]:
            list_users[message.chat.id].recommendations=[]
            markup = ReplyKeyboardMarkup(one_time_keyboard=True, 
                                        input_field_placeholder="Enviar tu ubicación",
                                        resize_keyboard=True)
            location_btn = types.KeyboardButton("Enviar ubicación",request_location=True)
            markup.add(location_btn)
            
            msg=bot.send_message(message.chat.id, "To begin, please share your location by pressing the button below. If you don't see it, please press the button before the clip button.", reply_markup=markup)
            #in the case we have the last position we delete this information! 
            bot.register_next_step_handler(msg, pedir_photo) 
            
        else:
            markup=ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "You have already accepted a recommendation. Please first finish the measurement before requesting a new recommendation. I will send you the location of the recomendation",reply_markup=markup)
            rec_Accepted=list_users[message.chat.id].recommendations_aceptada
            bot.send_location(chat_id=message.chat.id, latitude=rec_Accepted.point['Latitude'], longitude=rec_Accepted.point['Longitude'])
            
        
    else: 
        bot.reply_to(message, "Please first send the command /start to be added to the database. Thank you!")


def pedir_photo(message):
    list_users[message.chat.id].location_to_measure={"Longitude": message.location.longitude,"Latitude": message.location.latitude}
    # Longitude: message.location.longitude
    # Latitude: message.location.latitude
    list_users[message.chat.id].recommendations=[]
    
    rec_Accepted=list_users[message.chat.id].recommendations_aceptada
    
    # Hay que pedirle la photo al usuario
    # markup = ReplyKeyboardMarkup(one_time_keyboard=True, 
    #                                     input_field_placeholder="Enviar tu ubicación",
    #                                     resize_keyboard=True)
    # location_btn = types.KeyboardButton("Enviar ubicación",request_location=True)
    # markup.add(location_btn)
    markup=ReplyKeyboardRemove()
  
    msg=bot.send_message(message.chat.id, "Share the photo!", reply_markup=markup)
    #In the case we have the last position we delete this information! 
                   
    bot.register_next_step_handler(msg, subir_la_photo ) 
    
    
def subir_la_photo(message):    
    if list_users[message.chat.id].location_to_measure != None:
        red_acceptada=list_users[message.chat.id].recommendations_aceptada
        recomendation_aceptada_2=bot_auxiliar.recomendaciones_aceptadas(message.chat.id)
        #Todo! asegurate que cuando recomendacion_Aceptada_2 es vacia te devuelve None. 
        if red_acceptada != None and recomendation_aceptada_2!=None:
            # if recomendation_aceptada_2 != None:
                #TODO esto no se si esta bien
                data=bot_auxiliar.create_measurement(id_user=message.chat.id,  Latitud=list_users[message.chat.id].location_to_measure['Latitude'], Longitud=list_users[message.chat.id].location_to_measure['Longitude'])

                if data != None:
                    #Guardamos la photo. 
                    
                    if data['recommendation_id'] == None:
                        lat, long = bot_auxiliar.get_point(id_user=message.chat.id, latitud=list_users[message.chat.id].location_to_measure['Latitude'], longuitud=list_users[message.chat.id].location_to_measure['Longitude'])
                        if lat != None and long != None:
                                file_id = message.photo[-1].file_id
                                file_info = bot.get_file(file_id)
                                downloaded_file = bot.download_file(file_info.file_path)
                                file_path = f'Telegram_bot/Pictures/photo{data["id"]}.jpg'
                                measurement=MeasurementCreate(id=data['id'],url=file_path, location={ 'Longitude': list_users[message.chat.id].location_to_measure['Longitude'], 'Latitude': list_users[message.chat.id].location_to_measure['Latitude']})
                                with open(file_path, 'wb') as new_file:
                                            new_file.write(downloaded_file)
                                measuremenmt= Measurement_bot(list_users[message.chat.id].location_to_measure, file_path)
                                list_users[message.chat.id].measurement.append(measuremenmt)  
                                list_users[message.chat.id].recommendations_aceptada=[]

                                # bot.reply_to(message, "We are integrating your photo to the collage. This may take a few seconds." )
                                # crear_mapa(message)
                                #Calculado el punto de la celda donde ha ido la medicion. 
                                # file_id = message.photo[-1].file_id
                                # file_info = bot.get_file(file_id)
                                # downloaded_file = bot.download_file(file_info.file_path)
                                # file_path = f'telegram_bot/Pictures/photo{data["id"]}.jpg'
                                # with open(file_path, 'wb') as new_file:
                                #     new_file.write(downloaded_file)
                                # measuremenmt= Measurement_bot(list_users[message.chat.id].location_to_measure, file_path)
                                # list_users[message.chat.id].measurement.append(measuremenmt)  
                                # measurement=MeasurementCreate(id=data['id'],url=file_path, location={'Latitude':lat, 'Longitude':long})
                                # list_users[message.chat.id].recommendations_aceptada=[]

                                # lat, long = bot_auxiliar.get_point(id_user=message.chat.id, latitud=recomendation_aceptada_2['member_current_location']['Latitude'], longuitud=recomendation_aceptada_2['member_current_location']['Longitude'])
                                # crear_mapa(message)
                                # bot.reply_to( message, "Thanks for sending the photo!") 
                                bot.send_message(message.chat.id, "Please ensure that you take the photo at the agreed location. You can view the map with photos using the command /map.")
                                lat = red_acceptada[0].point['Latitude']
                                long = red_acceptada[0].point['Longitude']
                                bot.send_location(chat_id=message.chat.id, latitude=lat, longitude=long)
                        else:
                            bot.reply_to(message, "Your current position is outside the campaign area. Please send your location at the agreed-upon point.")

                    else:
                        #LA medicion es donde debe! 
                        # lat, long = accepted_recomendation.point['Latitude'], accepted_recomendation.point['Longitude']
                        file_id = message.photo[-1].file_id
                        file_info = bot.get_file(file_id)
                        downloaded_file = bot.download_file(file_info.file_path)
                        file_path = f'telegram_bot/Pictures/photo{data["id"]}.jpg'
                        measurement=MeasurementCreate(id=data['id'],url=file_path, location={ 'Longitude': list_users[message.chat.id].location_to_measure['Longitude'], 'Latitude': list_users[message.chat.id].location_to_measure['Latitude']})
                        with open(file_path, 'wb') as new_file:
                                    new_file.write(downloaded_file)
                        measuremenmt= Measurement_bot(list_users[message.chat.id].location_to_measure, file_path)
                        list_users[message.chat.id].measurement.append(measuremenmt)  
                        list_users[message.chat.id].recommendations_aceptada=[]

                        bot.reply_to(message, "We are integrating your photo to the collage. This may take a few seconds." )
                        crear_mapa(message)
                else:
                    bot.reply_to(message, "Please try again. Make sure that the location you send is within the accepted recommendation you selected.")
            # else:
            #     crud.recomendation.remove(db=db, db_obj=accepted_recomendation)
            #     bot.reply_to(message, "Please first send the comand /mesasurement or /recomendation to have your location. Thanks you! ")
        else:
                if recomendation_aceptada_2 == None:
                    list_users[message.chat.id].recommendations_aceptada=[]
                    bot.reply_to(message, "Has tardado demasiado, su recomendacion no puede ser integrada. Pôrfavor pìda otra recomendación ")
                                # crear_mapa(message)
                                
       
    else:
            bot.reply_to(message, "Please first send the command /recommendation to share your location. Thank you!")

    

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
        measuerements =bot_auxiliar.get_measurement()
        measu=[]
        for i in list_users:
            for j in list_users[i].measurement:
                measu.append(j)
        
        # Obtener el número de combinaciones diferentes de las dos primeras columnas
        campaign=bot_auxiliar.get_campaign_hive_1(id_user=message.chat.id)
        if campaign is None:
                bot.reply_to(message, "Error in the visualization. Perhaps there is no active campaign. Please contact @Maite314 for assistance.")
                return None
        else:
            radio=campaign['cells_distance']/2
            hipotenusa= math.sqrt(2*((radio)**2))
            dics={}
            if measu !=[]:
                for i in measu:
                    (lat, long ) = i.location['Latitude'], i.location['Longitude']
                    if (lat,long)  in list(dics.keys()):
                        dics[(lat,long)]=dics[(lat,long)]+1 
                        
                    else:
                        dics[(lat,long)]=0
                    
                    n_files=dics[(lat,long)]
                    

                    combinacion =  (lat, long )
                    datos_tercera_columna = i.url
                    grados = 90
                    lat, long =   (lat, long )
                    # print(n_files*grados, n_files)
                    if 0 <= (n_files*grados)%360 and 90 > (n_files*grados)%360:                    
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
                    elif(n_files*grados)%360 >= 270 and (n_files*grados)%360 < 360:
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
                    elif 180 <= (n_files*grados)%360 and 270 > (n_files*grados)%360:
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
                    elif  90 <= (n_files*grados)%360 and 180 > (n_files*grados)%360:
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
                            
            mapa.save('index.html')
                # Enviar el mapa al usuario
                # try:
            map_path = f'index.html'
            with open(map_path, 'rb') as map_file:
                bot.send_document(message.chat.id, document=map_file, parse_mode="html")

            # bot.send_photo(message.chat.id, photo=open('/recommendersystem/Telegram_bot/index.html', 'rb'), caption="Here is the collage of the photos taken.")
            # text='Your photo is part of the collague. \n Please visit  <a href="Deusto_collegue_picture_map">http://htmlpreview.github.io/?https:https://mpuerta004.github.io/RecommenderSystem/index.html</a> to see!\n'
    else:
        bot.reply_to(message, "There seems to be an issue with the representation, campaigns, or surface. Please contact @Maite314 for assistance.")


@bot.message_handler(commands=['map'])
def crear_mapa_bot(message):
    crear_mapa(message)
    actualizar_repositorio()


def definir_mensajes():
    "Bucle infinito que comprueba si hay nuevos mensajes en el bot"
    bot.infinity_polling()

if __name__ == "__main__":

    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Start the bot"), #Command, description
        # telebot.types.BotCommand("/general_info", "general information"),
        telebot.types.BotCommand("/recommendation", "get a recommendation"),
        telebot.types.BotCommand("/upload_photo", "Upload photo"),
        telebot.types.BotCommand("/map", "Generate the map"),
        telebot.types.BotCommand("/personal_information", "Change and consult your personal information")
    ])
    # bot.polling()
    hilo_bot= threading.Thread(name="hilo_bot", target=definir_mensajes)
    hilo_bot.start()
    
