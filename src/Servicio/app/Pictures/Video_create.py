import os 
import os
import moviepy.video.io.ImageSequenceClip
from selenium import webdriver  
import time

driver = webdriver.Chrome()

path = r"C:/Users/mpuer/Desktop/RecommenderSystem/src/Servicio/app/Pictures/Measurements"

archivos = sorted(os.listdir(path))
for i in archivos: 
    dirArchivo = path + "/" + i
    print(i)
    driver.get(dirArchivo)
    time.sleep(2)
    driver.save_screenshot(path + "/" + i[:-5]+".png")
driver.quit()
fps=7
image_files = [os.path.join(path,img)
               for img in os.listdir(path)
               if img.endswith(".png")]

clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
clip.write_videofile('C:/Users/mpuer/Desktop/RecommenderSystem/src/Servicio/app/Pictures/my_video.mp4')