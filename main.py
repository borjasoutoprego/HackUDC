from climate_data import table_processing, dms_to_dd
import pandas as pd
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

with open('activities.json') as file:
        ACTIVITIES = json.load(file)

def get_Longitud(longitud):
    for i in range(len(df['Longitud'])) :
        longitud[i] = longitud[i].split(' ')[0]
        longitud[i] = longitud[i].replace('.', '')
        if len(longitud[i].split('-')) == 2:
            longitud[i] = int(longitud[i].split('-')[0] + longitud[i].split('-')[1]) / 2
    return longitud

def menu():
    print("Actividades disponibles: ")
    print("1: Tomar el sol\n2: Nadar\n3: Surf\n4: Pasear\n5: Nudismo\n6: Deporte pelota")
    choice = int(input("Escoja su actividad: "))

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
    print(df)
    

def search_near(df):
    df["diff_lat"] = pd.Series(dtype='float')
    df["diff_lon"] = pd.Series(dtype='float')
    geolocator = Nominatim(user_agent="HackatonAPP")
    user_loc = geolocator.geocode('Ferrol') ##################
    
    for i, row in df.iterrows():
        lat = float(dms_to_dd(row['Coordena_3']))
        lon = float(dms_to_dd(row['Coordena_2']))
        df.at[i,'diff_lat'] = abs(lat-user_loc.latitude)
        df.at[i,'diff_lon'] = abs(lon-user_loc.longitude)

    df = df[df['diff_lat'] <= 0.5]
    df = df[df['diff_lon'] <= 0.5]

    return df


if __name__ == "__main__":


    df = pd.read_csv("playas.csv")
    ######## Limpieza de coordenadas mal expresadas
    for i, row in df.iterrows():
        if (len(row['Coordena_3'].split(" ")) != 4) or (len(row['Coordena_2'].split(" ")) != 4):
            df = df.drop(i)
        else:
            df.at[i,'Coordena_3'] = df.at[i,'Coordena_3'].replace(" \'", "\' ").replace("\'\'\'", "\"")
            df.at[i,'Coordena_2'] = df.at[i,'Coordena_2'].replace(" \'", "\' ").replace("\'\'\'", "\"")
    df = df.reset_index()
    ########

    df = df[["Nombre", "Longitud", "Grado_ocup", "Nudismo", "Bandera_az", "Auxilio_y_", "Forma_de_a",
            "Acceso_dis", "Autobús", "Aseos", "Zona_infan", "Submarinis", "Coordena_2", "Coordena_3"]]
    df['Longitud'] = get_Longitud(df['Longitud'])
    activity = menu()
    df_filtered1 = filter1(df, activity).reset_index()
    # UBICACION
    df_near = search_near(df_filtered1).reset_index()
    df_raw_clima = table_processing(df_near[:5], 0, 17)
    df_filtered2 = filter2(df_raw_clima, activity)

    order_dataframe(df_filtered2, activity)






