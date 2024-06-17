

class Measurement_bot(object):
    def __init__(self, localizacion:dict()={}, url:str=None):
        self.location=localizacion
        self.url=url
        
        # global list_users  # Declaramos que vamos a usar la variable global