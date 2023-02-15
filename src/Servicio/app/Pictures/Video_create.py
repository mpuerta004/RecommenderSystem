import cv2 
import os 

img_array = []

path = r"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Recomendaciones"
archivos = sorted(os.listdir(path))

for i in archivos: 
    dirArchivo = path + "/" + i
    print(i)
    img = cv2.imread(dirArchivo)
    cv2.putText(img, f"Recomendaciones con no popularidad en 3 o menos celdas", (80,180), cv2.FONT_HERSHEY_SIMPLEX , 1.5, (0,0,0))
    img_array.append(img)
    

video = cv2.VideoWriter('CVC-08.avi', cv2.VideoWriter_fourcc(*'DIVX'), 4, ( 1500, 1500))


for i in range(0, len(archivos)):
	video.write(img_array[i])

video.release()
