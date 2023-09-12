import os 
import os
import moviepy.video.io.ImageSequenceClip
from selenium import webdriver  
import time
#open the explorer website
driver = webdriver.Chrome()
#direction of the pictures
path = r"C:/Users/mpuer/Desktop/RecommenderSystem/src/Servicio/app/Pictures/Measurements"
#sort the pictures by name 
archivos = sorted(os.listdir(path))
# for each picture, take a screenshot and save it in the same folder with the same name
for i in archivos: 
    dirArchivo = path + "/" + i
    print(i)
    driver.get(dirArchivo)
    time.sleep(2)
    driver.save_screenshot(path + "/" + i[:-5]+".png")
#close the explorer website
driver.quit()

############# CRªEATE VIDEO #################
fps=1
#more fps means faster video speed
# if we want a video for a spoken presentation (In the background) -> 1 fps
# if we want a video for a focus presentation on this -> 2 or 3 fps

#List of pictures of the folder.
image_files = [os.path.join(path,img)
               for img in os.listdir(path)
               if img.endswith(".png")]
#create the video. w
clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
clip.write_videofile('C:/Users/mpuer/Desktop/RecommenderSystem/src/Servicio/app/Pictures/my_video.mp4')