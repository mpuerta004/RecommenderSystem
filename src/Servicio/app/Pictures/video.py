import os
from html2image import Html2Image
import moviepy.video.io.ImageSequenceClip

input_folder =  'C:/Users/mpuer/Desktop/recommendersystem/src/Servicio/app/Pictures/Measurements_html'

output_folder = 'C:/Users/mpuer/Desktop/RecommenderSystem/src/Servicio/app/Pictures/Measurements_html_pictures'

hti = Html2Image(output_path=output_folder)

html_files = sorted(os.listdir(input_folder))

for html_file in html_files:
    if html_file.endswith(".html"):
        hti.screenshot(url=input_folder+'/'+html_file, save_as=html_file+'.png')

############# CRªEATE VIDEO #################
fps=1
#more fps means faster video speed
# if we want a video for a spoken presentation (In the background) -> 1 fps
# if we want a video for a focus presentation on this -> 2 or 3 fps
   
#List of pictures of the folder.
image_files = [os.path.join(output_folder,img)
               for img in os.listdir(output_folder)
               if img.endswith(".png")]
#create the video. w
clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
clip.write_videofile('C:/Users/mpuer/Desktop/RecommenderSystem/src/Servicio/app/Pictures/bio-inspired_measurements.mp4')

