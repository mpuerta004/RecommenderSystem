import Demo.variables as variables
from datetime import datetime, timedelta


def legend_generation_measurements_representation(time:str):
    
    # Create the legend with a white background and opacity 0.5
    legend_html = '''
        <div style="position: fixed; 
            bottom: 80px; left: 90px; width: 290px; height: 240px; 
            border:2px solid grey; z-index:9999;
            background-color: rgba(255, 255, 255, 0.75);
            font-size:15px;">
            <p style="margin:10px;"><b>Progress of measurements</b></p>
            '''
    # Add the colored boxes to the legend
    for i in range(len(variables.color_list_hex)):
        legend_html += '''
            <div style="background-color:{}; margin-left: 10px;
                width: 28px; height: 16px; border: 2px solid #999;
                display: inline-block;"></div>
            <p style="display: inline-block; margin-left: 10px;">{}</p>
            <br>
            '''.format(variables.color_list_[i], variables.names_legend_color[i])
    legend_html += '''
    <div ></div><p style=display: inline-block; margin-left: 5px;">time: {}</p>
    '''.format(time)
    legend_html += '</div>'
    return legend_html


def legend_generation_recommendation_representation(time:str):
    legend_html=legend_generation_measurements_representation(time)
#     # Create the legend with a white background and opacity 0.5
#     legend_html = '''
#         <div style="position: fixed; 
#             bottom: 80px; left: 90px; width: 290px; height: 240px; 
#             border:2px solid grey; z-index:9999;
#             background-color: rgba(255, 255, 255, 0.75);
#             font-size:15px;">
#             <p style="margin:10px;"><b>Progress of measurements</b></p>
#             '''
#     # Add the colored boxes to the legend
#     for i in range(len(variables.color_list_h)):
#         legend_html += '''
#             <div style="background-color:{}; margin-left: 10px;
#                 width: 28px; height: 16px; border: 2px solid #999;
#                 display: inline-block;"></div>
#             <p style="display: inline-block; margin-left: 5px;">{}</p>
#             <br> 
#             '''.format(variables.color_list_h[i], variables.names_legend_color[i])
#     legend_html += '''
#  <div ></div><p style=display: inline-block; margin-left: 10px;">time: {}</p>    '''.format(time)
#     legend_html += '</div>'
    
    legend_html_2 = '''
        <div style="position: fixed; 
            bottom: 350px; left: 90px; width: 290px; height: 170px; 
            border:2px solid grey; z-index:9999;
            background-color: rgba(255, 255, 255, 0.75);
            font-size:15px;">
            <p style="margin:10px;"><b>Marker Legend</b></p>
            '''
    # Add the map-legend symbols to the legend
    for i in range(len(variables.color_simbols_recomendations_feature_map)):
        legend_html_2 += '''
            <i class="fa fa-map-marker fa-2x"
                    style="color:{};icon:user;margin-left: 10px;"></i>
            <p style="display: inline-block; margin-left: 5px;">{}</p>
            <br>
            '''.format(variables.color_simbols_recomendations_feature_map[i], variables.names_simbols_recommendations[i])

    legend_html_2 += '</div>'
    return  legend_html, legend_html_2