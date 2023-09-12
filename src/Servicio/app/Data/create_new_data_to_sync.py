import json

hive_id= 1 #Change this variable as in the simulation need. 
# Code to create the terminal lines to ejecute in the termineal and populate the database for the experiments. 
result = ''
for id in range(1, 2):
    #Insert the line that create the user and his/her role in the hive
    if id==1:
        role="QueenBee"
    else:
        role="WorkerBee"
    #element = f"insert into Member (name,surname,age,gender,city,mail,birthday,real_user,id) values (name,surname,0,'FEMALE',city, mail,'2023-03-09 10:47:50',true,{id});insert into Hive_Member (hive_id, member_id, role) values ({hive_id},{id},'{role}');"
    #Insert the line that create a new device
    #3element= f"insert into Device (id) values ({id});"            
    #Insert the live that create the Member_device entity to associete the member with the device
    element =  f"insert into Member_Device (device_id, member_id) values ({id},{id});"
    result = result + element #+ element2 + element3

#Create the .json file to save all this mysql commant to ejecute in the terminal. 
with open('archivo.json', 'w') as file:
    json.dump(result, file, indent=4)
