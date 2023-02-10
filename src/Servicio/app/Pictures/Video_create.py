import cv2 
import os 

img_array = []

path = r"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Recomendaciones"
archivos = sorted(os.listdir(path))

for i in archivos: 
    dirArchivo = path + "/" + i
    print(i)
    img = cv2.imread(dirArchivo)
    img_array.append(img)
    

video = cv2.VideoWriter('CVC-08.avi', cv2.VideoWriter_fourcc(*'DIVX'), 4, ( 1500, 1500))

for i in range(0, len(archivos)):
	video.write(img_array[i])

video.release()
