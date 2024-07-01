
import math
import json
import requests
import telebot
from Telegram_bot.Token.Token  import TOKEN, radio_cell
from telebot import types
import datetime
from csv import writer
import folium
import threading
from vincenty import vincenty_inverse
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

from Telegram_bot.usuario import User
from Telegram_bot.measurement_bot import Measurement_bot
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
            User(chat_id=message.chat.id,list_users=list_users,data=data)
            user=list_users[message.chat.id]
            markup=ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Wellcome back {user.name}!👋\nReady to create the Duesto' collague?📸\nWhen you're ready, press /recommendation to begin",reply_markup=markup)
        else:
            data=bot_auxiliar.new_new_user(message=message)
            if data != None:
                # Vamos a conocer al usuario! 
                User(chat_id=message.chat.id,list_users=list_users)
                markup=ReplyKeyboardRemove()
                bar = '■' * 1+ '□' * 5
                msg=bot.send_message(message.chat.id, f"Hello!👋 I'm the MVE bot 🤖! Let's create the Deusto' collage together! 📸 \nBut first, 🤗 let's get to know each other!\n\n[{bar}] What's your name? 🤔",reply_markup=markup)
                bot.register_next_step_handler(msg, registrar_nombre) 
            else:
                print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
                bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314. Wait few minutes and try again.")
    
    except Exception as e:
        print("Error durante la conexion con la base de datos:", e)
        bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")

@bot.message_handler(commands=['personal_information'])
def personal_information(message):
    bot.send_chat_action(message.chat.id, 'typing')

    if message.chat.id  in list(list_users.keys()):
        markup=ReplyKeyboardRemove()
        user=list_users[message.chat.id]
        texto='<code>Actual informacion:</code>\n'
        texto+=f"<code>NAME...:</code> {user.name}\n"
        texto+=f"<code>SURNAME:</code> {user.surname}\n"
        texto+=f"<code>AGE....:</code> {user.age}\n"
        texto+=f"<code>MAIL...:</code> {user.mail}\n"
        texto+=f"<code>GENDER.:</code> {user.gender}\n"
        bot.send_message(message.chat.id, texto,parse_mode="html",reply_markup=markup)
            
        markup=ReplyKeyboardMarkup(one_time_keyboard=True, 
                                        resize_keyboard=True)
        markup.add('Yes','No')
        markup=InlineKeyboardMarkup(row_width=2)
        yes=InlineKeyboardButton("Yes", callback_data="Yes")
        no=InlineKeyboardButton("No", callback_data="No")
        markup.add(yes, no)
        bot.send_message(message.chat.id, "Would you like to change it?", reply_markup=markup) 
        # bot.register_next_step_handler(msg, change_personal_information) 
    else:
        markup=ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Please frist send the command /start or cleck in the comand. Thank you!",reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: (call.data=="Yes" or call.data=="No"))
def callback_query(call):
    cid=call.from_user.id #chat_id
    mid= call.message.id #message_id
    
    bot.send_chat_action(cid, 'typing')
    if cid in list(list_users.keys()):
        markup=InlineKeyboardMarkup(row_width=1)
        a=bot.delete_message(cid, mid)
        if call.data=="Yes":
            bar = '■' * 1+ '□' * 5
            msg=bot.send_message(cid, f"Let's start then!😊👍\n[{bar}] What's your name?")   
            bot.register_next_step_handler(msg, registrar_nombre)
        else:
            bot.send_message(cid, "Ok, no problem!😊")
    else:
        bot.delete_message(cid, mid)
        markup=ReplyKeyboardRemove()
        bot.send_message(cid, "Please frist click in the command /start. Thank you!",reply_markup=markup)

def registrar_nombre(message):
    global list_users  # Declaramos que vamos a usar la variable global
    bot.send_chat_action(message.chat.id, 'typing')
	#aqui en message.text tenemos la info del nombre. 
    nombre=message.text
    if type(nombre) != str or nombre == "" or nombre[0:1]=="/":
        markup=ReplyKeyboardRemove()
        msg=bot.reply_to(message, "Please provide a valid name",reply_markup=markup)
        bot.register_next_step_handler(msg, registrar_nombre) 
    else:
        # We look if the user is in the database.
        set_name=bot_auxiliar.set_name(member_id=message.chat.id, name=nombre)
        if set_name != None :
            user=list_users[message.chat.id]
            user.set_name( name=nombre,list_users=list_users)
            markup=ForceReply()
            bar = '■' * 2+ '□' * 3
            msg=bot.send_message(message.chat.id, f"[{bar}] What's your surname?", reply_markup=markup) 
            bot.register_next_step_handler(msg, registrar_apellido) 
            
        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
            return None
    

def registrar_apellido(message):
    global list_users  # Declaramos que vamos a usar la variable global

    bot.send_chat_action(message.chat.id, 'typing')
    surname=message.text
    if type(surname) != str or surname == "" or surname[0:1]=="/":
        msg=bot.reply_to(message, "Please provide a valid surname")
        bot.register_next_step_handler(msg, registrar_apellido) 

    # if we have name:
    else:
        set_name=bot_auxiliar.set_surname(member_id=message.chat.id, surname=surname)
        if set_name != None :
            user=list_users[message.chat.id]
            user.set_surname(surname=surname,list_users=list_users)
            markup=ForceReply()
            bar = '■' * 3+ '□' * 2
            msg=bot.send_message(message.chat.id, f"[{bar}] How old are you?" , reply_markup=markup) 
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
            bar = '■' * 4+ '□' * 1
            msg=bot.send_message(message.chat.id, f"[{bar}] What is your email?", reply_markup=markup) 
            bot.register_next_step_handler(msg, registrar_email) 
           
        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
            return None


def registrar_email(message):
    global list_users  # Declaramos que vamos a usar la variable global

    bot.send_chat_action(message.chat.id, 'typing')

    mail=message.text
    if type(mail) != str or mail == "" or mail[0:1]=="/" or "@" not in mail or "." not in mail:
        bot.reply_to(message, "Please provide a valid mail")
        bot.register_next_step_handler(msg, registrar_email) 
    else:
        # We look if the user is in the database.
        set_name=bot_auxiliar.set_mail(member_id=message.chat.id, mail=mail)
        if set_name != None :
            user=list_users[message.chat.id]
            user.set_mail(mail=mail,list_users=list_users)
            markup=InlineKeyboardMarkup(row_width=2)
            male=InlineKeyboardButton("Male", callback_data="MALE")
            female=InlineKeyboardButton("Female", callback_data="FEMALE")
            no_binary=InlineKeyboardButton("Non binary", callback_data="NOBINARY")
            No_answer=InlineKeyboardButton("No answer", callback_data="NOANSWER")
            markup.add(male, female, no_binary, No_answer)
            bar = '■' * 5+ '□' * 0
            msg=bot.send_message(message.chat.id, f"[{bar}] What is your gender?", reply_markup=markup)            
        else:
            bot.send_message(message.chat.id,"Error with the system. please contact with @Maite314")
        
        
@bot.callback_query_handler(func=lambda call: (call.data=="NOBINARY" or call.data=="FEMALE" or call.data=="MALE" or call.data=="NOANSWER"))
def callback_query(call):
    global list_users
    cid=call.from_user.id #chat_id
    mid= call.message.id #message_id
    if cid in list(list_users.keys()):
        a=bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        bot.send_message(cid, f"You have chosen {call.data}")
        set_name=bot_auxiliar.set_gender(member_id=cid, gender=call.data)
        if set_name != None :
            user=list_users[cid]
            user.set_gender( gender=call.data,list_users=list_users)
            texto='<code>Personal Information:</code>\n'
            texto+=f"<code>NAME...:</code> {user.name}\n"
            texto+=f"<code>SURNAME:</code> {user.surname}\n"
            texto+=f"<code>AGE....:</code> {user.age}\n"
            texto+=f"<code>MAIL...:</code> {user.mail}\n"
            texto+=f"<code>GENDER.:</code> {user.gender}\n"
            bot.send_message(cid, texto,parse_mode="html")
            bot.send_message(cid, "send (or click) /recommendation to start the collague! ")
        else:
            bot.send_message(cid,"Error with the system. please contact with @Maite314")
    else:
        bot.delete_message(cid, mid)
        markup=ReplyKeyboardRemove()
        bot.send_message(cid, "Please frist send the command /start or cleck in the comand. Thank you!",reply_markup=markup)



# Envia una ubicación para pedir la recomendación!
@bot.message_handler(commands=['recommendation'])
def recommendation(message):
    global list_users
    # cid=call.from_user.id #chat_id
    # mid= call.message.id #message_id
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.id in list(list_users.keys()):
        user=list_users[message.chat.id]
        member_2 = bot_auxiliar.existe_user(id_user=message.chat.id)
        if user != None and member_2 != None:
            if list_users[message.chat.id].recommendations_aceptada==[]:
                list_users[message.chat.id].recommendations=[]
                markup = ReplyKeyboardMarkup(one_time_keyboard=True, 
                                            input_field_placeholder="Share your location",
                                            resize_keyboard=True)
                location_btn = types.KeyboardButton("Share your location 📍",request_location=True)
                markup.add(location_btn)
                
                msg=bot.send_message(message.chat.id, "To begin, please share your location by pressing the button of your keyboard. ", reply_markup=markup)
                #in the case we have the last position we delete this information! 
                
                
                bot.register_next_step_handler(msg, crear_la_Recomendacion) 
            else:
                markup=InlineKeyboardMarkup(row_width=1)
                yes=InlineKeyboardButton(f"I'm ready to take the photo!",callback_data="upload_photo")
                markup.add(yes)
                bot.send_message(message.chat.id, "You have already accepted a recommendation. Please go to this location and where you are here press the next botton 👇 ",reply_markup=markup)
                rec_Accepted=list_users[message.chat.id].recommendations_aceptada
                bot.send_location(chat_id=message.chat.id, latitude=rec_Accepted['Latitude'], longitude=rec_Accepted['Longitude'])
                
                
        else: 
            markup=ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "Please frist click in the command /start Thank you!",reply_markup=markup)

    else: 
        markup=ReplyKeyboardRemove()
        bot.send_message(message.chat.id,  "Please frist click in the command /start Thank you!",reply_markup=markup)

        

def crear_la_Recomendacion(message):
    global list_users
    if message.location is None:
        bot.send_message(message.chat.id, "Please write the command /recommendation and share your location. Thank you!")
    else:
        campaign = bot_auxiliar.get_campaign_hive_1()
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
                                message.chat.id, "There are no recommendations available. We apologize for the inconvenience.",reply_markup=markup)     
                                        
                else:
                    markup=InlineKeyboardMarkup(row_width=1)
                    
                    recommendations=[]
                    for i in range(0,len(data['results'])):
                        point = data['results'][i]['cell']['centre']
                        
                        # recomendation= RecommendationCreate(id=data['results'][i]['recommendation']['id'],member_id=message.chat.id, posicion=str(i), state="NOTIFIED",point={"Longitude":point['Longitude'],"Latitude":point['Latitude']})
                        
                        locations=locations+[{"latitude":point['Latitude'],"longitude":point['Longitude'],"title":f"Recommendation {i}"}]
                        yes=InlineKeyboardButton(f"Recommendation {i+1}", callback_data=f"Recommendation {i}")
                        markup.add(yes)
                        markup_remove=ReplyKeyboardRemove()
                        recommendations.append({"latitude":point['Latitude'],"longitude":point['Longitude'],"id":data['results'][i]['recommendation']['id']})
                        text=f"Recommendation {i+1}:"
                        bot.send_message(chat_id=message.chat.id, text=text,reply_markup=markup_remove)

                        b=bot.send_location(chat_id=message.chat.id, latitude=point['Latitude'], longitude=point['Longitude'])

                        # Generar el mapa con folium
                    # map = folium.Map(location=[message.location.latitude, message.location.longitude], zoom_start=17)
                    user=list_users[message.chat.id]
                    list_users[message.chat.id].recommendations=recommendations 
                    user.recommendations=recommendations
                    
                    # Añadir marcador para la ubicación del usuario
                    # folium.Marker(
                    #     [message.location.latitude, message.location.longitude],
                    #         popup="You are here",
                    #         icon=folium.Icon(color="blue")
                    #     ).add_to(map)

                    #     # Añadir marcadores para las localizaciones predefinidas
                    # for loc in locations:
                    #         folium.Marker(
                    #             [loc["latitude"], loc["longitude"]],
                    #             popup=loc["title"]
                    #         ).add_to(map)

                    #     # Guardar el mapa en un objeto BytesIO
                    #  # Guardar el mapa en un archivo local para depuración
                    # map.save("map.html")
                    # # Enviar el mapa al usuario
                    # # try:
                    # map_path = f'recommendation{message.chat.id}.html'
                    # map.save(map_path)
                    # with open(map_path, 'rb') as map_file:
                    msg=bot.send_message(message.chat.id, "Select the recommendation based on the place you want to visit to take a photo!📸📸 Remember to bring out the artist in you!",reply_markup=markup)
                            # bot.register_next_step_handler(msg, user_select_recomendations) 

                            
                    # except Exception as e:
                    #     print(f"Failed to send photo: {e}")
                    # bot.register_next_step_handler(msg, user_select_recomendations) 
            else:
                markup=ReplyKeyboardRemove()

                msg=bot.send_message(message.chat.id, "Unfortunately, there are no recommendations available for you at this time. We apologize for the inconvenience.",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: (call.data=="Recommendation 0" or call.data=="Recommendation 1" or call.data=="Recommendation 2"))
def callback_query(call):
    global list_users

    cid=call.from_user.id #chat_id
    mid= call.message.id #message_id
    bot.send_chat_action(cid, 'typing')
    if cid in list(list_users.keys()):
        if list_users[cid].recommendations != []:
            a=bot.edit_message_reply_markup(cid, mid, reply_markup=None)
            bot.reply_to(a, f"You have chosen the recommendation {int(call.data[-1])+1}")
            
            recommendation=list_users[cid].recommendations[int(call.data[-1])]
            list_users[cid].recommendations=[]
            list_users[cid].recommendations_aceptada=[]
            list_users[cid].recommendations_aceptada.append(recommendation)
            accepted_recomendation=bot_auxiliar.update_recomendation(id_user=cid, recomendation_id=recommendation['id'])
            markup=InlineKeyboardMarkup(row_width=1)
            yes=InlineKeyboardButton(f"I'm ready to take the picture! 📸",callback_data="upload_photo")
            markup.add(yes)
            bot.send_message(cid, f"This is the place you select👇! Please go there to take a photo!📸 When you are there, please press the button!",reply_markup=markup)
            bot.send_location(chat_id=cid, latitude=recommendation['latitude'], longitude=recommendation['longitude'])
            # markup=InlineKeyboardMarkup(row_width=1)
            # yes=InlineKeyboardButton(f"Estoy ready para hacer la foto!",callback_data="upload_photo")
            # markup.add(yes)
            # bot.send_message(cid, f"¨Porfavor cuando llegues al punto press this botton. ",reply_markup=markup)
        else:
            markup=ReplyKeyboardRemove()
            bot.send_message(cid, "Please frist send the command /recommendation or click in the comand. Thank you!",reply_markup=markup)
            
    else:
        bot.delete_message(cid, mid)
        markup=ReplyKeyboardRemove()
        bot.send_message(cid, "Please frist send the command /start or cleck in the comand. Thank you!",reply_markup=markup)


@bot.callback_query_handler(func=lambda call: (call.data=="upload_photo"))
# @bot.message_handler(commands=['upload_photo'])
def medicion(call):
    global list_users

    cid=call.from_user.id #chat_id
    list_users[cid].recommendations=[]
    mid= call.message.id #message_id
    bot.send_chat_action(cid, 'typing')
    if cid in list(list_users.keys()):
        user=list_users[cid]
        member_2 = bot_auxiliar.existe_user(id_user=cid)
        a=bot.edit_message_reply_markup(cid, mid, reply_markup=None)
                # bot.reply_to(a, f"")
        if member_2 != None:       
            if list_users[cid].recommendations_aceptada!=[]:
                list_users[cid].recommendations=[]
                markup = ReplyKeyboardMarkup(one_time_keyboard=True, 
                                                    input_field_placeholder="Share your location 📍",
                                                    resize_keyboard=True)
                location_btn = types.KeyboardButton("Share your location 📍",request_location=True)
                markup.add(location_btn)
                msg=bot.send_message(cid, "To begin, please share your location by pressing the button of your keyboard.", reply_markup=markup)
                bot.register_next_step_handler(msg, verificar_posicion_correcta) 
                        
            else:
                bot.delete_message(cid, mid)
                bot.send_message(cid, "Please first send the command /recommendation to start the process. Thank you!",reply_markup=markup)
                             
        else:
            bot.delete_message(cid, mid)
            markup=ReplyKeyboardRemove()
            bot.send_message(cid, "Please frist send the command /start or cleck in the comand. Thank you!",reply_markup=markup)

           
    else: 
        bot.delete_message(cid, mid)
        markup=ReplyKeyboardRemove()
        bot.send_message(cid, "Please frist send the command /start or cleck in the comand. Thank you!",reply_markup=markup)
    
    
def verificar_posicion_correcta(message): 
    global list_users
    if message.location is None:
        markup=InlineKeyboardMarkup(row_width=1)

        yes=InlineKeyboardButton(f"I'm ready to take the picture! 📸",callback_data="upload_photo")
        markup.add(yes)
        bot.send_message(message.chat.id, f"Please press the button! and share the location when the system ask for it",reply_markup=markup)
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        if message.chat.id in list(list_users.keys()):
            list_users[message.chat.id].location_to_measure={"Longitude": message.location.longitude,"Latitude": message.location.latitude}
            list_users[message.chat.id].recommendations=[]
            # if list_users[message.chat.id].location_to_measure != None:
                #No tenem,os su ubicacion (Esto no es posible!)
            red_acceptada=list_users[message.chat.id].recommendations_aceptada
            recomendation_aceptada_2=bot_auxiliar.recomendaciones_aceptadas(message.chat.id)
            if red_acceptada != None and recomendation_aceptada_2!=None:
                    #Que la base de datos sigue reguistrando que tienes una recopmendacion aceptada y ell bot tambien la tiene registrada. 
                    # if recomendation_aceptada_2 != None:
                        #TODO esto no se si esta bien
                        # data=bot_auxiliar.create_measurement(id_user=message.chat.id,  Latitud=list_users[message.chat.id].location_to_measure['Latitude'], Longitud=list_users[message.chat.id].location_to_measure['Longitude'])
                Latitud_user=list_users[message.chat.id].location_to_measure['Latitude']
                Longitud_user=list_users[message.chat.id].location_to_measure['Longitude']
                lat = red_acceptada[0]['latitude']
                long = red_acceptada[0]['longitude']
                distance = vincenty_inverse((Latitud_user, Longitud_user), (lat, long))
                if distance <= radio_cell:
                    markup=ReplyKeyboardRemove()
                    msg=bot.send_message(message.chat.id, "Please share your photo", reply_markup=markup)
                            #in the case we have the last position we delete this information! 
                    bot.register_next_step_handler(msg, pedir_photo) 
                            
                            # El usuario esta donde debe para hacer la medicion!
                                    
                else:
                    
                    markup=InlineKeyboardMarkup(row_width=1)
                    yes=InlineKeyboardButton(f"I'm ready to take the picture! 📸",callback_data="upload_photo")
                    markup.add(yes)
                    
                    bot.send_message(message.chat.id, "Please ensure that you take the photo at the correct location you select. I send to you the location!👇When you are there, please press the button!", reply_markup=markup)
                    lat = red_acceptada[0]['latitude']
                    long = red_acceptada[0]['longitude']
                    bot.send_location(chat_id=message.chat.id, latitude=lat, longitude=long)
                    # markup=InlineKeyboardMarkup(row_width=1)
                    # yes=InlineKeyboardButton(f"I'm ready to take the picture! 📸",callback_data="upload_photo")
                    # markup.add(yes)
                    # bot.send_message(message.chat.id, f"Please go there to take a photo!📸 When you are there, please press the button!", reply_markup= markup)
                                            
            else:
                if recomendation_aceptada_2 == None:
                    list_users[message.chat.id].recommendations_aceptada=[]
                    markup=ReplyKeyboardRemove()
                    bot.reply_to(message, "You have taken too long, your recommendation cannot be integrated. Please ask for another recommendation using the /recommendation command." ,reply_markup=markup)                          
            
            # else:
            #     markup=ReplyKeyboardRemove()
            #     bot.reply_to(message, "Please first send the command /recommendation to share your location. Thank you!",reply_markup=markup)
        else:
            markup=ReplyKeyboardRemove()
            bot.reply_to(message, "Please, first prees /start botton. Thanks you!",reply_markup=markup)
        

def pedir_photo(message):
    global list_users
    bot.send_chat_action(message.chat.id, 'typing')

    if message.photo[-1] is None:
        markup=ReplyKeyboardRemove()
        msg=bot.send_message(message.chat.id, "Please share your photo. Press the📎icon to take a picture", reply_markup=markup)
                            #in the case we have the last position we delete this information! 
        bot.register_next_step_handler(msg, pedir_photo) 
    else:
        data=bot_auxiliar.create_measurement(id_user=message.chat.id,  Latitud=list_users[message.chat.id].location_to_measure['Latitude'], Longitud=list_users[message.chat.id].location_to_measure['Longitude'])
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = f'/recommendersystem/src/Servicio/app/Telegram_bot/Pictures/photo{data["id"]}.jpg'
                            # measurement=MeasurementCreate(id=data['id'],url=file_path, location={ 'Longitude': list_users[message.chat.id].location_to_measure['Longitude'], 'Latitude': list_users[message.chat.id].location_to_measure['Latitude']})
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        measuremenmt= Measurement_bot(list_users[message.chat.id].location_to_measure, file_path)
        list_users[message.chat.id].measurement.append(measuremenmt)  
        list_users[message.chat.id].recommendations_aceptada=[]

        bot.reply_to(message, "Your photo has been registered! In a few minutes you will be able to see it by clicking the following button!" )
        markup=InlineKeyboardMarkup(row_width=1)
        b1=InlineKeyboardButton("Deusto collage picture map", url="https://raw.githack.com/mpuerta004/RecommenderSystem/Bot/index.html")
        markup.add(b1)
        bot.send_message(message.chat.id, "Please visit the following link to see the collage of the photos taken.", reply_markup=markup)

   
    
def actualizar_repositorio():
    # Ejecutar el comando para agregar, hacer commit y hacer push del archivo HTML
    subprocess.run(['git', 'add', '-f', 'index.html'])
    subprocess.run(['git', 'commit', '-m', 'Actualizar HTML'])
    subprocess.run(['git', 'push'])



def crear_mapa():

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
        campaign=bot_auxiliar.get_campaign_hive_1()
        if campaign is None:
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
            return True
        return None
    return None
                # Enviar el mapa al usuario
                # try:
            #map_path = f'index.html'
            #with open(map_path, 'rb') as map_file:
            #     bot.send_document(message.chat.id, document=map_file, parse_mode="html")
    #         markup=InlineKeyboardMarkup(row_width=1)
    #         b1=InlineKeyboardButton("Deusto collage picture map", url="https://raw.githack.com/mpuerta004/RecommenderSystem/Bot/index.html")
    #         #https://raw.githack.com/mpuerta004/RecommenderSystem/Bot/index.html
    #         markup.add(b1)
    #         bot.send_message(message.chat.id, "Please visit the following link to see the collage of the photos taken.", reply_markup=markup)

    #         # bot.send_photo(message.chat.id, photo=open('/recommendersystem/Telegram_bot/index.html', 'rb'), caption="Here is the collage of the photos taken.")
    #         # text='Your photo is part of the collague. \n Please visit  <a href="Deusto_collegue_picture_map">http://htmlpreview.github.io/?https:https://mpuerta004.github.io/RecommenderSystem/index.html</a> to see!\n'
    # else:
    #     bot.reply_to(message, "There seems to be an issue with the representation, campaigns, or surface. Please contact @Maite314 for assistance.")

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


    
    

@bot.message_handler(commands=['map'])
def enviar_map(message):
    markup=InlineKeyboardMarkup(row_width=1)
    b1=InlineKeyboardButton("Deusto collage picture map", url="https://raw.githack.com/mpuerta004/RecommenderSystem/Bot/index.html")
    #https://raw.githack.com/mpuerta004/RecommenderSystem/Bot/index.html
    markup.add(b1)
    bot.send_message(message.chat.id, "Please visit the following link to see the collage of the photos taken.", reply_markup=markup)



def definir_mensajes():
    "Bucle infinito que comprueba si hay nuevos mensajes en el bot"
    bot.infinity_polling()



# if __name__ == "__main__":
#     bot.set_my_commands([
#         telebot.types.BotCommand("/start", "Start the bot"), #Command, description
#         # telebot.types.BotCommand("/general_info", "general information"),
#         telebot.types.BotCommand("/recommendation", "get a recommendation"),
#         telebot.types.BotCommand("/map", "Deusto Collague link"),
#         telebot.types.BotCommand("/personal_information", "Change and consult your personal information")
#     ])
#     # bot.polling()
#     hilo_bot= threading.Thread(name="hilo_bot", target=definir_mensajes)
#     hilo_bot.start()
    