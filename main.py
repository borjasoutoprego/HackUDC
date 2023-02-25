from climate_data import table_processing, dms_to_dd
import pandas as pd
import numpy as np
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import sys

with open('activities.json') as file:
        ACTIVITIES = json.load(file)

def get_Longitud(longitud):
    for i in range(len(df['Longitud'])) :
        longitud[i] = longitud[i].split(' ')[0]
        longitud[i] = longitud[i].replace('.', '')
        if len(longitud[i].split('-')) == 2:
            longitud[i] = int(longitud[i].split('-')[0] + longitud[i].split('-')[1]) / 2
    return longitud

def menu(person):
    print("Actividades disponibles: ")
    print("1: Tomar el sol\n2: Nadar\n3: Surf\n4: Pasear\n5: Nudismo\n6: Deporte pelota")
    choice = int(input(f"Escoja la actividad de la persona {person+1}: "))

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




def main(df):
    n = int(input("¿Cuántas personas vais a ir a la playa?: "))
    location = input("Elige la ubicación: ")
    dist = int(input("Introduce la distancia máxima de búsqueda (en km): "))/100
    day_delay = int(input("En cuantos dias vas a ir a la playa (hoy:0, mañana:1 ... [max(6)]: "))
    hour = int(input("Indica la hora (en formato 24h): "))
    
    results = []

    for person in range(n):
        activity = menu(person)
        df_filtered1 = filter1(df, activity).reset_index()
        df_near = search_near(df_filtered1, location, dist).reset_index()
        df_raw_clima = table_processing(df_near, day_delay, hour)
        df_filtered2 = filter2(df_raw_clima, activity)
        result = order_dataframe(df_filtered2, activity)
        if n == 1:
            print(result)
            sys.exit()
        else:
            results.append(result)
            print(result)



    df_final = results[0].copy()

    for result in results[1:]:

        df_final = pd.merge(df_final, result, how="outer", on=["Nombre", "Coordena_3", "Coordena_2"])
        df_final = df_final.replace(np.nan,0)

        df_final["points"] = df_final.loc[:,['points_x','points_y']].sum(axis = 1)
        df_final = df_final[["Nombre", "Coordena_3", "Coordena_2", "points"]]

    print("----------")
    print("FINAL")
    print("----------")
    print(df_final.sort_values(by="points", ascending=False, ignore_index=True))
        


if __name__ == "__main__":


    df = pd.read_csv("playas.csv")
    ######## Limpieza de datos
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
    #########################
    main(df)







