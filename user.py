import json


result=""
for ie in range(3, 231):
    element =  f"insert into Member_Device (device_id, member_id) values ({ie},{ie});"
    result =result + element


with open('archivo.json', 'w') as file:
    json.dump(result, file, indent=4)