import Demo.variables as variables
from datetime import datetime, timedelta
import crud
from datetime import datetime, timedelta
import math
import numpy as np
import io
from PIL import Image
import folium
from funtionalities import get_point_at_distance, prioriry_calculation
import numpy as np
from numpy import sin, cos, arccos, pi, round
from folium.features import DivIcon
import folium
from math import sin, cos, atan2, sqrt, radians, degrees, asin
from fastapi.responses import HTMLResponse
from folium.plugins import HeatMap
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from typing import Optional, Any, List
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Recommendation import state, Recommendation, RecommendationCreate, RecommendationUpdate, RecommendationCell
from schemas.Member import Member
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
import deps
from datetime import datetime, timezone
from datetime import datetime, timezone, timedelta
from vincenty import vincenty
# import folium.colormap as cm
import folium.plugins

import branca
import branca.colormap as cm
from bio_inspired_recommender.bio_agent import BIOAgent
import Demo.variables as variable

#Leyend and map funtions
def legend_measurements_scale(time:str):
    
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
            '''.format(variables.color_list_hex[i], variables.names_legend_color[i])
    legend_html += '''
    <div ></div><p style=display: inline-block; margin-left: 5px;">time: {}</p>
    '''.format(time)
    legend_html += '</div>'
    return legend_html



def legend_generation_recommendation(time:str):
    
    legend_html_2 = '''
        <div style="position: fixed; 
            bottom: 350px; left: 90px; width: 290px; height: 170px; 
            border:2px solid grey; z-index:9999;
            background-color: rgba(255, 255, 255, 0.75);
            font-size:15px;">
            <p style="margin:10px;"><b>Marker Legend</b></p>
            '''
    # Add the map-legend symbols to the legend
    index= list(variables.dict_color_simbols_recommendation.keys())
    for i in index:
        legend_html_2 += '''
            <i class="{} fa-2x"
                    style="color:{};margin-left: 10px;"></i>
            <p style="display: inline-block; margin-left: 5px;">{}</p>
            <br>
            '''.format(variables.dict_icon_simbols[i],variables.dict_color_simbols_recommendation[i],i)

    legend_html_2 += '</div>'
    return  legend_html_2


def show_recomendation(*, cam: Campaign, user: Member, result: list(), time: datetime, recomendation: Recommendation, db: Session = Depends(deps.get_db)) -> Any:
    if result is []:
        return True
    
    count = 0
    Cells_recomendadas = []
    for i in result:
        slot = crud.slot.get_slot(db=db, slot_id=i.slot_id)
        Cells_recomendadas.append(slot.cell_id)
    if recomendation is not None: 
        slot = crud.slot.get_slot(db=db, slot_id=recomendation.slot_id)
        Cells_recomendadas.append(slot.cell_id)
    cell_elejida = slot.cell_id
    
    user_position = result[0].member_current_location
    cell_distance = cam.cells_distance
    hipotenusa = math.sqrt(2*((cell_distance/2)**2))
    
    
    
    surface = crud.surface.get(db=db, id=cam.surfaces[0].id)
    mapObj = folium.Map(location=[surface.boundary.centre['Latitude'],
                        surface.boundary.centre['Longitude']], zoom_start=variable.zoom_start)
    List_campaign=crud.campaign.get_all_active_campaign_for_a_hive(db=db, hive_id=cam.hive_id,time=time)
    
    for cam in List_campaign:
        for i in cam.surfaces:
            count = count+1
            for j in i.cells:
                slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)
                # Ponermos el color en funcion de la cantidad de datos no de la prioridad.
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db,  time=time, slot_id=slot.id)
                expected_measurements= crud.recommendation.get_aceptance_state_of_cell(
                db=db, slot_id=slot.id)
                expected_measurements=len(expected_measurements)
                if Cardinal_actual >= cam.min_samples:
                    color = variables.color_list_hex[4]
                else:
                    numero = int((Cardinal_actual/cam.min_samples)//(1/4))
                    color = variables.color_list_hex[numero]
                lon1 = j.centre['Longitude']
                lat1 = j.centre['Latitude']

                # Desired distance in kilometers
                distance = hipotenusa
                list_direction = [45, 135, 225, 315]
                list_point = []
                for dir in list_direction:
                    lat2, lon2 = get_point_at_distance(
                        lat1=lat1, lon1=lon1, d=distance, bearing=dir)
                    # Direction in degrees

                    list_point.append([lat2, lon2])
                folium.Polygon(locations=list_point, color='black', fill_color=color,
                            weight=1, popup=(folium.Popup(str(j.id))), opacity=0.5, fill_opacity=0.85).add_to(mapObj)

                folium.Marker(list_point[3],popup=f"Number of Expected measurements: {expected_measurements}",
                            icon=DivIcon(
                    icon_size=(200, 36),
                    icon_anchor=(0, 0),
                    html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>'
                )
                ).add_to(mapObj)
                
                if j.id in Cells_recomendadas:
                        if j.id == cell_elejida:
                            folium.Marker(location=[j.centre['Latitude'], j.centre['Longitude']], 
                                        icon=
                                        DivIcon( icon_anchor=(19, 19), html='''
                                <i class="{} fa-4x"
                                    style="color:{};"></i>
                                <br>
                                '''.format(variables.dict_icon_simbols["Selected Point"],variables.dict_color_simbols_recommendation["Selected Point"])
                                    #   icon=folium.Icon(color=variables.dict_color_simbols_recommendation["Selected Point"], icon=variables.dict_icon_simbols["Selected Point"])
                                    )).add_to(mapObj)

                        else:
                            folium.Marker(location=[j.centre['Latitude'], j.centre['Longitude']],
                                            icon= DivIcon(icon_anchor=(19,19), html='''
                                <i class="{} fa-4x"
                                    style="color:{};"></i>
                                <br>
                                '''.format(variables.dict_icon_simbols["Rejected Points"], variables.dict_color_simbols_recommendation["Rejected Points"])
                                )
                                # icon=folium.Icon(color=variables.dict_color_simbols_recommendation["Recommended Points"], icon=variables.dict_icon_simbols["Recommended Points"]),
                                        ).add_to(mapObj)

                            

        # draw user position
        folium.Marker(location=[float(user_position['Latitude']), float(user_position['Longitude'])],
                    icon= DivIcon( icon_anchor=(19, 19),  html='''
                                <i class="{} fa-4x"
                                    style="color:{};"></i>
                                <br>
                                '''.format(variables.dict_icon_simbols["User's Position"],variables.dict_color_simbols_recommendation["User's Position"])
                                )).add_to(mapObj)
    direcion_html = f"/recommendersystem/src/Servicio/app/Pictures/Recomendaciones_html/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}Cam{cam.id}HI{cam.hive_id}.html"

    # direcion_png = f"/recommendersystem/src/Servicio/app/Pictures/Recomendaciones/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}.Cam{cam.id}Hi{cam.hive_id}.png"
    legend_html=legend_measurements_scale(time.strftime('%m/%d/%Y, %H:%M:%S'))
    
   
    # Add the map-legend symbols to the legend
    legend_html_2 = legend_generation_recommendation(time.strftime('%m/%d/%Y, %H:%M:%S'))
    mapObj.get_root().html.add_child(folium.Element(legend_html))

    mapObj.get_root().html.add_child(folium.Element(legend_html_2))
    mapObj.save(direcion_html)
    # img_data = mapObj._to_png(5)
    # img = Image.open(io.BytesIO(img_data))
    # img.save(direcion_png)
    return None




def show_recomendation_with_thesholes(*, bio:BIOAgent, cam: Campaign, user: Member, result: list(), time: datetime, recomendation: Recommendation, db: Session = Depends(deps.get_db)) -> Any:
    
    
    if result is []:
        return True
    
    count = 0
    Cells_recomendadas = []
    for i in result:
        slot = crud.slot.get_slot(db=db, slot_id=i.slot_id)
        Cells_recomendadas.append(slot.cell_id)
    if recomendation is not None: 
        slot = crud.slot.get_slot(db=db, slot_id=recomendation.slot_id)
        Cells_recomendadas.append(slot.cell_id)
    cell_elejida = slot.cell_id
    
    user_position = result[0].member_current_location
    cell_distance = cam.cells_distance
    hipotenusa = math.sqrt(2*((cell_distance/2)**2))
    
    linear=cm.linear.YlGnBu_03.scale(vmin=bio.get_0_min(), vmax=bio.get_0_max())
    # (vmin=bio.get_0_min(), vmax=bio.get_0_max())
    # linear=cm.LinearColormap(variables. vmin=bio.get_0_min(), vmax=bio.get_0_max())

    surface = crud.surface.get(db=db, id=cam.surfaces[0].id)
    # linear = cm.StepColormap(variable.color_list_hex, vmin=bio.get_0_min(), vmax=bio.get_0_max())

    mapObj = folium.Map(location=[surface.boundary.centre['Latitude'],
                        surface.boundary.centre['Longitude']], zoom_start=variables.zoom_start)
    List_campaign=crud.campaign.get_all_active_campaign_for_a_hive(db=db, hive_id=cam.hive_id,time=time)
  
    for cam in List_campaign:
        for i in cam.surfaces:
            count = count+1
            for j in i.cells:
                theshole= bio.get_thesthold_of_user_in_cell(member_id=user.id, cell_id=j.id)
                slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)
                # Ponermos el color en funcion de la cantidad de datos no de la prioridad.
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db,  time=time, slot_id=slot.id)
                expected_measurements= crud.recommendation.get_aceptance_state_of_cell(
                db=db, slot_id=slot.id)
                expected_measurements=len(expected_measurements)
                priority=crud.priority.get_by_slot_and_time(db=db, slot_id=slot.id, time= time)

                lon1 = j.centre['Longitude']
                lat1 = j.centre['Latitude']

                # Desired distance in kilometers
                distance = hipotenusa
                list_direction = [45, 135, 225, 315]
                list_point = []
                for dir in list_direction:
                    lat2, lon2 = get_point_at_distance(
                        lat1=lat1, lon1=lon1, d=distance, bearing=dir)
                    # Direction in degrees

                    list_point.append([lat2, lon2])
                folium.Polygon(locations=list_point, color='black', fill_color=linear(theshole),
                            weight=1, popup=(folium.Popup(str(j.id))), opacity=0.5, fill_opacity=0.9).add_to(mapObj)

                priority=crud.priority.get_by_slot_and_time(db=db, slot_id=slot.id, time= time)
                folium.Marker(list_point[3],popup=f"Theshole real: {theshole}, priority:{priority.temporal_priority}",
                            icon=DivIcon(
                    icon_size=(200, 36),
                    icon_anchor=(0, 0),
                    html=f'<div style="font-size: 20pt">{Cardinal_actual}, {expected_measurements}</div>'
                )
                ).add_to(mapObj)

                if j.id in Cells_recomendadas:
                    if j.id == cell_elejida:
                        folium.Marker(location=[j.centre['Latitude'], j.centre['Longitude']], 
                                       icon=
                                       DivIcon( icon_anchor=(19, 19), html='''
                             <i class="{} fa-4x"
                                style="color:{};"></i>
                            <br>
                            '''.format(variables.dict_icon_simbols["Selected Point"],variables.dict_color_simbols_recommendation["Selected Point"])
                                   #   icon=folium.Icon(color=variables.dict_color_simbols_recommendation["Selected Point"], icon=variables.dict_icon_simbols["Selected Point"])
                                   )).add_to(mapObj)

                    else:
                        folium.Marker(location=[j.centre['Latitude'], j.centre['Longitude']],
                                        icon= DivIcon(icon_anchor=(19,19), html='''
                             <i class="{} fa-4x"
                                style="color:{};"></i>
                            <br>
                            '''.format(variables.dict_icon_simbols["Rejected Points"], variables.dict_color_simbols_recommendation["Rejected Points"])
                            )
                            # icon=folium.Icon(color=variables.dict_color_simbols_recommendation["Recommended Points"], icon=variables.dict_icon_simbols["Recommended Points"]),
                                    ).add_to(mapObj)

                        

    # draw user position
    folium.Marker(location=[float(user_position['Latitude']), float(user_position['Longitude'])],
                  icon= DivIcon( icon_anchor=(19, 19),  html='''
                             <i class="{} fa-4x"
                                style="color:{};"></i>
                            <br>
                            '''.format(variables.dict_icon_simbols["User's Position"],variables.dict_color_simbols_recommendation["User's Position"])
                            )).add_to(mapObj)
                
                #  icon=folium.Icon( color=variables.dict_color_simbols_recommendation["User's Position"], icon=variables.dict_icon_simbols["User's Position"] )).add_to(mapObj)
    
    direcion_html = f"/recommendersystem/src/Servicio/app/Pictures/Recomendaciones_html_others/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}Cam{cam.id}HI{cam.hive_id}.html"
    
    linear.caption = 'Nevel of specialization'
    mapObj.add_child(linear)
    
    mapObj.get_root().html.add_child(folium.Element(legend_generation_recommendation(time.strftime('%m/%d/%Y, %H:%M:%S'))))
    mapObj.save(direcion_html)
    return None


def show_hive(
    *,
    hive_id: int,
    time: datetime,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Show a campaign
    """
    campañas_activas= crud.campaign.get_all_active_campaign_for_a_hive(db=db, hive_id=hive_id,time=time)
    
    if campañas_activas is None or campañas_activas is [] or len(campañas_activas)==0:
       return None
    count = 0
    
    
    lat_center=0
    lon_center=0
    n=0
    for i in campañas_activas:
        surfaces=crud.surface.get_multi_surface_from_campaign_id(db=db, campaign_id=i.id)
        for surface in surfaces:
            n=n+1
            lat_center=lat_center + surface.boundary.centre['Latitude']
            lon_center=lon_center + surface.boundary.centre['Longitude']
    
    
    print(lat_center/n, lon_center/n)
    
    mapObj = folium.Map(location=[lat_center/n,
                        lon_center/n], zoom_start=variables.zoom_start)
    for cam in campañas_activas:
        cell_distance = cam.cells_distance

        hipotenusa = math.sqrt(2*((cell_distance/2)**2))
        for i in cam.surfaces:

            count = count+1
            for j in i.cells:
                slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)

                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db, time=time, slot_id=slot.id)
                expected_measurements=len( crud.recommendation.get_aceptance_state_of_cell(
                db=db, slot_id=slot.id))
                if Cardinal_actual >= cam.min_samples:
                    numero = 4
                else:
                    numero = int((Cardinal_actual/cam.min_samples)//(1/4))
                # color= (color_list[numero][2],color_list[numero][1],color_list[numero][0])
                color = variables.color_list_hex[numero]
                lon1 = j.centre['Longitude']
                lat1 = j.centre['Latitude']

                # Desired distance in kilometers
                distance = hipotenusa
                list_direction = [45, 135, 225, 315]
                list_point = []
                for dir in list_direction:
                    lat2, lon2 = get_point_at_distance(
                        lat1=lat1, lon1=lon1, d=distance, bearing=dir)

                    list_point.append([lat2, lon2])

               
                folium.Polygon(locations=list_point, color='black', fill_color=color,
                            weight=1, popup=(folium.Popup(str(j.id))), opacity=0.5, fill_opacity=0.85).add_to(mapObj)

                folium.Marker(list_point[3],popup=f"Number of Expected measurements: {expected_measurements}",
                            icon=DivIcon(
                    icon_size=(200, 36),
                    icon_anchor=(0, 0),
                    html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>'
                )
                ).add_to(mapObj)

    direcion_html = f"/recommendersystem/src/Servicio/app/Pictures/Measurements_html/{time.strftime('%m-%d-%Y-%H-%M-%S')}Hi{hive_id}.html"
    # direcion_png = f"/recommendersystem/src/Servicio/app/Pictures/Measurements/{time.strftime('%m-%d-%Y-%H-%M-%S')}Hi{hive_id}.png"
    
    legend_html = legend_measurements_scale(time.strftime('%m/%d/%Y, %H:%M:%S'))
    mapObj.get_root().html.add_child(folium.Element(legend_html))
    mapObj.save(direcion_html)

    # img_data = mapObj._to_png(5)
    # img = Image.open(io.BytesIO(img_data))
    # img.save(direcion_png)
    return None

def show_a_campaign(
    *,
    hive_id: int,
    campaign_id: int,
    time: datetime,
    # request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Show a campaign
    """

    campañas_activas = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None or campañas_activas is []:
        raise HTTPException(
            status_code=404, detail=f"Campaign with campaign_id=={campaign_id}  and hive_id=={hive_id} not found"
        )
    count = 0
    surface = crud.surface.get(db=db, id=campañas_activas.surfaces[0].id)
    mapObj = folium.Map(location=[surface.boundary.centre['Latitude'],
                        surface.boundary.centre['Longitude']], zoom_start=variables.zoom_start)

    cell_distance = campañas_activas.cells_distance

    hipotenusa = math.sqrt(2*((cell_distance/2)**2))

    for i in campañas_activas.surfaces:
        count = count+1
        for j in i.cells:
            slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)

            Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                db=db, time=time, slot_id=slot.id)
            if Cardinal_actual >= campañas_activas.min_samples:
                numero = 4
            else:
                numero = int((Cardinal_actual/campañas_activas.min_samples)//(1/4))
            # color= (color_list[numero][2],color_list[numero][1],color_list[numero][0])
            color = variables.color_list_hex[numero]
            lon1 = j.centre['Longitude']
            lat1 = j.centre['Latitude']

            # Desired distance in kilometers
            distance = hipotenusa
            list_direction = [45, 135, 225, 315]
            list_point = []
            for dir in list_direction:
                lat2, lon2 = get_point_at_distance(
                    lat1=lat1, lon1=lon1, d=distance, bearing=dir)

                list_point.append([lat2, lon2])

            line_color = 'black'
            fill_color = color
            weight = 1
            text = 'text'
            folium.Polygon(locations=list_point, color=line_color, fill_color=color,
                           weight=weight, popup=(folium.Popup(text)), opacity=0.5, fill_opacity=0.85).add_to(mapObj)

            folium.Marker([lat1, lon1],
                          icon=DivIcon(
                icon_size=(200, 36),
                icon_anchor=(0, 0),
                html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>',
            )
            ).add_to(mapObj)

    # res, im_png = cv2.imencode(".png", imagen)
    direcion_html = f"/recommendersystem/src/Servicio/app/Pictures/Measurements_html/{time.strftime('%m-%d-%Y-%H-%M-%S')}Cam{campañas_activas.id}Hi{campañas_activas.hive_id}.html"
    # print(direcion)
    # cv2.imwrite(direcion, imagen)
    direcion_png = f"/recommendersystem/src/Servicio/app/Pictures/Measurements/{time.strftime('%m-%d-%Y-%H-%M-%S')}Cam{campañas_activas.id}Hi{campañas_activas.hive_id}.png"
    
    mapObj.get_root().html.add_child(folium.Element(legend_measurements_scale(time.strftime('%m/%d/%Y, %H:%M:%S'))))
    mapObj.save(direcion_html)

    # img_data = mapObj._to_png(5)
    # img = Image.open(io.BytesIO(img_data))
    # img.save(direcion_png)
    return None

