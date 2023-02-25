from climate_data import table_processing, dms_to_dd
import pandas as pd
import numpy as np
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from fastapi import FastAPI
import uvicorn

"""
Actividades disponibles:
    1: Tomar el sol
    2: Nadar
    3: Surf
    4: Pasear
    5: Nudismo
    6: Deporte pelota
    7: Submarinismo
    8: Volar cometa
    9: Excursión en familia
    10: Ver las estrellas
"""

app = FastAPI()

with open('activities.json') as file:
        ACTIVITIES = json.load(file)


def get_Longitud(longitud):
    for i in range(len(longitud)) :
        longitud[i] = longitud[i].split(' ')[0]
        longitud[i] = longitud[i].replace('.', '')
        if len(longitud[i].split('-')) == 2:
            longitud[i] = int(longitud[i].split('-')[0] + longitud[i].split('-')[1]) / 2
    return longitud


def menu(choice):
    if choice == 1:
        return("sol")
    elif choice == 2:
        return("nadar")
    elif choice == 3:
        return("surf")
    elif choice == 4:
        return("pasear")
    elif choice == 5:
        return("nudismo")
    elif choice == 6:
        return("deporte_pelota")
    elif choice == 7:
        return("submarinismo")
    elif choice == 8:
        return("cometa")
    elif choice == 9:
        return("familia")
    elif choice == 10:
        return("estrellas")


def filter1(df, activity):
    filters = ACTIVITIES[activity]["filtrado1"]
    for filter in filters.keys():
        if filters[filter] == "NULL":
            continue
        elif filter == "Longitud":
            min, max = filters[filter].split(",")
            df = df[df['Longitud'].astype(int) >= float(min)]
            df = df[df['Longitud'].astype(int) <= float(max)]
        else:
            column = filter
            value = filters[filter]
            if filter == "Grado_ocup" or filter == "Nudismo":
                df = df[df[column].isin(value)]
            elif filter == "Forma_de_a":
                df = df[~df[column].isin(value)]
            else:
                df = df[df[column] == value]
    return df


def filter2(df, activity):
    filters = ACTIVITIES[activity]["filtrado2"]
    final_columns = ["Nombre", "Coordena_2", "Coordena_3"]
    for filter in filters.keys():
        if filters[filter] != "False" :
            final_columns.append(filter)
    return df[final_columns]


def order_dataframe(df, activity):
    filters = ACTIVITIES[activity]["filtrado2"]
    df_points = pd.DataFrame()
    for d in df.iloc[:, 3:]:
        if filters[d] == "max":
            order = max
        elif filters[d] == "min":
            order = min
        df_points[f"points_{d}"] = (df[d] == order(df[d])).astype(int)
    df = df.assign(points=df_points.sum(axis=1))
    df = df.sort_values(by="points", ascending=False, ignore_index=True)
    return df
    

def search_near(df, location, dist):
    df["diff_lat"] = pd.Series(dtype='float')
    df["diff_lon"] = pd.Series(dtype='float')
    geolocator = Nominatim(user_agent="HackatonAPP")
    user_loc = geolocator.geocode(location)
    for i, row in df.iterrows():
        lat = float(dms_to_dd(row['Coordena_3']))
        lon = float(dms_to_dd(row['Coordena_2']))
        df.at[i,'diff_lat'] = abs(lat-user_loc.latitude)
        df.at[i,'diff_lon'] = abs(lon-user_loc.longitude)
    df = df[df['diff_lat'] <= dist]
    df = df[df['diff_lon'] <= dist]
    return df


@app.get("/HackUDC")
def main(dist:int, location:str, day_delay:int, hour:int, people_activities:str):
    
    ################################ Limpieza de datos ################################
    df = pd.read_csv("playas.csv")
    for i, row in df.iterrows():
        if (len(row['Coordena_3'].split(" ")) != 4) or (len(row['Coordena_2'].split(" ")) != 4):
            df = df.drop(i)
        else:
            df.at[i,'Coordena_3'] = df.at[i,'Coordena_3'].replace(" \'", "\' ").replace("\'\'\'", "\"")
            df.at[i,'Coordena_2'] = df.at[i,'Coordena_2'].replace(" \'", "\' ").replace("\'\'\'", "\"")
    df = df.reset_index()
    df = df[["Nombre", "Longitud", "Grado_ocup", "Nudismo", "Bandera_az", "Auxilio_y_", "Forma_de_a",
            "Acceso_dis", "Autobús", "Aseos", "Zona_infan", "Submarinis", "Coordena_2", "Coordena_3"]]
    df['Longitud'] = get_Longitud(df['Longitud'])
    #####################################################################################
    
    people = []
    for item in people_activities.split(";"):
        people.append(item.split(","))
    dist = int(dist)/100
    results = []
    for person in people:
        for activity_num in person:
            while True:
                try:
                    activity = menu(int(activity_num))
                    df_filtered1 = filter1(df, activity).reset_index()
                    df_near = search_near(df_filtered1, location, dist).reset_index()
                    df_raw_clima = table_processing(df_near, day_delay, hour)
                    df_filtered2 = filter2(df_raw_clima, activity)
                    assert(len(df_filtered2.index) != 0)
                except:    
                    print("Lo siento, no se han encontrado resultados 😕")
                    close = input("¿Quieres cerrar el programa? y/N ")
                    if close in ("Y", "y"):
                        return
                else:
                    break
            result = order_dataframe(df_filtered2, activity)
            if len(people) == 1 and len(people[0]) == 1:
                if len(result.index) >= 5:
                    return result[:5].to_dict('index')
                else:
                    return result.to_dict('index')
            else:
                results.append(result)

    df_final = results[0].copy()
    for result in results[1:]:
        df_final = pd.merge(df_final, result, how="outer", on=["Nombre", "Coordena_3", "Coordena_2"])
        df_final = df_final.replace(np.nan,0)
        df_final["points"] = df_final.loc[:,['points_x','points_y']].sum(axis = 1)
        df_final = df_final[["Nombre", "Coordena_3", "Coordena_2", "points"]]

    if len(df_final.index) >= 5:
        return df_final.sort_values(by="points", ascending=False, ignore_index=True)[:5].to_dict('index')
    else:
        return df_final.sort_values(by="points", ascending=False, ignore_index=True).to_dict('index')


if __name__ == "__main__":
    uvicorn.run(app, port=8080)







