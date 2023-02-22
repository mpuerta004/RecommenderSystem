import cv2 
import os 

img_array = []

path = r"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Measurements"
archivos = sorted(os.listdir(path))
for i in archivos: 
    dirArchivo = path + "/" + i
    print(i)
    img = cv2.imread(dirArchivo)
    height, width  = img.shape[:2]

    cv2.putText(img, f"Recomendaciones con no popularidad en 3 o menos celdas", (80,180), cv2.FONT_HERSHEY_SIMPLEX , 1.5, (0,0,0))
    img_array.append(img)
    

video = cv2.VideoWriter('db0.wmv',cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))


for i in range(0, len(archivos)):
	video.write(img_array[i])

video.release()
