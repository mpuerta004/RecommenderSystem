

class User(object):
    def __init__(self, chat_id:int,list_users:dict(),data={}):
        # global list_users  # Declaramos que vamos a usar la variable global

        for id in list(list_users.keys()):
            if id==chat_id:
                if data !={}:
                    self.chat_id=chat_id
                    self.name=data['name']
                    self.birthday=data['birthday']
                    self.surname=data['surname']
                    self.age=data['age']
                    self.mail=data['mail']
                    self.gender=data['gender']
                    self.location_to_measure={}
                    self.recommendations=[]
                    list_users[chat_id]=self
                    self.measurement=[]
                    self.recommendations_aceptada=[]
                    
                else:
                    self= list_users[chat_id]
                return None
        if data !={}:
                    self.chat_id=chat_id
                    self.name=data['name']
                    self.birthday=data['birthday']
                    self.surname=data['surname']
                    self.age=data['age']
                    self.mail=data['mail']
                    self.gender=data['gender']
                    self.recommendations=[]
                    recommendations_Accepted=[]
                    self.location_to_measure={}
                    self.recommendations_aceptada=[]
                    self.measurement=[]
                    list_users[chat_id]=self

        else:
            self.chat_id=chat_id
            self.name=None
            self.birthday=None
            self.surname=None
            self.age=None
            self.mail=None
            self.gender=None
            self.location_to_measure={}
            self.recommendations=[]
            self.recommendations_aceptada=[]
            self.measurement=[]
            list_users[chat_id]=self
        return None

    
    def set_name(self, name:str,list_users:dict()):
        # global list_users  # Declaramos que vamos a usar la variable global
        self.name=name
        list_users[self.chat_id]=self
        return self
    
    def set_age(self, age:int,list_users:dict()):        
        self.age=age
        list_users[self.chat_id]=self
        return self
    
    def set_surname(self, surname:str,list_users:dict()):
        self.surname=surname
        list_users[self.chat_id]=self

        return self
    
    def set_birthday(self, birthday:str,list_users:dict()):
        self.birthday=birthday
        list_users[self.chat_id]=self
        return self
    
    def set_mail(self, mail:str,list_users:dict()):
        self.mail=mail
        list_users[self.chat_id]=self
        return self
    
    
    def set_gender(self, gender:str,list_users:dict()):
        self.gender=gender
        list_users[self.chat_id]=self
        return self
    
    