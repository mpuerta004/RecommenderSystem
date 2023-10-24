import json

hive_id= 1 #Change this variable as in the simulation need. 
# Code to create the terminal lines to ejecute in the termineal and populate the database for the experiments. 
result = ''
number_users=10
inicio=3
with open('archivo.json', 'w') as file:

    for id in range(inicio, number_users):
        #Insert the line that create the user and his/her role in the hive
        element = f"insert into Member (name,surname,age,gender,city, mail,birthday,real_user,id) values (name,surname,0,'FEMALE',city, mail,   '2023-03-09 10:47:50',true,{id});"
        result = result + element #+ element2 + element3

    for id in range(inicio, number_users):
        #Insert the line that create the user and his/her role in the hive
        if id==1:
            role="QueenBee"
        else:
            role="WorkerBee"
        element= f"insert into Hive_Member (hive_id, member_id, role) values ({hive_id},{id},'{role}');"
        result = result + element 

    #Create the .json file to save all this mysql commant to ejecute in the terminal. 
    for id in range(inicio, number_users):
        #Insert the line that create the user and his/her role in the hive
        element= f"insert into Device (id) values ({id});"          
        result = result + element

    for id in range(inicio, number_users):
        #Insert the line that create the user and his/her role in the hive
        element =  f"insert into Member_Device (device_id, member_id) values ({id},{id});"
        result = result + element #+ element2 + element3

    #Create the .json file to save all this mysql commant to ejecute in the terminal. 
    json.dump(result, file, indent=4)
