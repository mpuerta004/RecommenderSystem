# MAP features ###########################################################################################

# Color measurements subsection
zoom_start=18
color_list = [
    (255, 195, 195),
    (255, 219, 167),
    (248, 247, 187),
    (203, 255, 190),
    (138, 198, 131)
]
color_list_hex = ['#fff5eb', '#fdd0a2', '#fd8c3b', '#d84801', '#7f2704'] #Oranges
#['#f7fcfd', '#bfd3e6', '#8c95c6', '#88409c', '#4d004b']
#['#8e0152', '#e897c4', '#f7f7f6', '#9acd61', '#276419'] 
#['#b3e2cd', '#cbd5e8', '#e6f5c9', '#f1e2cc', '#cccccc'] #Pastel2
#['#fbb4ae', '#ccebc5', '#fed9a6', '#e5d8bd', '#f2f2f2'] #pastel1
#['#ffffd9', '#c6e9b4', '#40b5c4', '#225da8', '#081d58'] YlGnBu
#['#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683']
names_legend_color = ['Initial', 'Almost Midway',
                      'Midway', 'Almost Finished', 'Finished']

# Color recommendation subsection
dict_color_simbols_recommendation={"User's Position":'#000000',"Rejected Points": '#000000', "Selected Point":'#00FF00' }
dict_icon_simbols={"User's Position":'fa-solid fa-user', "Rejected Points": 'fa-sharp fa-regular fa-circle-xmark', "Selected Point":'fa-solid fa-location-dot' }
                   #'fa-solid fa-user',
                   #
# color_simbols_recomendations_feature_map = ['#ff8315', 'blue', 'red']
# names_simbols_recommendations = ["User's Position", "Recommended Points",
#                                  "Selected Point"]


# Color gradients
color_list_gradient_green_distribution = ['#94C58C', '#64AD62', ' #429B46', '#0A6921', '#094F29']

# User behaviour ########################################################################################


variables_comportamiento = {"user_aceptance": 0.5, "user_realize": 0.3, "user_availability": 0.5,
                            "popularidad_cell": 0.85, "number_of_unpopular_cells": 5}

