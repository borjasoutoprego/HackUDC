
# MÓDULO PARA OBTENER DATOS CLIMÁTICOS DE LAS PLAYAS

import requests
import pandas as pd

def dms_to_dd(dms):
    raw = dms.split(" ")
    d = float(raw[0][:-1])
    m = float(raw[1][:-1])
    s = float(raw[2][:-2].replace(",","."))
    direction = raw[3]
    
    dd = d + float(m)/60 + float(s)/3600
    if direction in ("W", "S"):
        dd = -dd

    return str(dd)


def get_data(lat_dms, lon_dms, day_delay, hour):
    lat = dms_to_dd(lat_dms)
    lon = dms_to_dd(lon_dms)

    key = "090991a2a61a4c489b9103146232402"
    query = lat + "," + lon
    response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={key}&q={query}&days={day_delay+1}&hour={hour}")
    response_wave = requests.get(f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height")

    dict_data = response.json()['forecast']['forecastday'][-1]['hour'][0]
    dict_data["waves"] = response_wave.json()['hourly']['wave_height'][24*day_delay + hour]

    return dict_data


def table_processing(df_beach, day_delay, hour):
    df_climate = pd.DataFrame(columns=["time", "is_day", "temp", "feelslike", "wind", "cloud", "rain", "vis", "uv", "waves"])
    for _, row in df_beach.iterrows():
        lat = row['Coordena_3']
        lon = row['Coordena_2']
        dict_data =  get_data(lat, lon, day_delay, hour)
        df_climate.loc[len(df_climate.index)] = [dict_data["time"], dict_data["is_day"], dict_data["temp_c"], dict_data["feelslike_c"], dict_data["wind_kph"],
                                                 dict_data["cloud"], dict_data["will_it_rain"], dict_data["vis_km"],dict_data["uv"], dict_data["waves"]]
    return pd.concat((df_beach, df_climate), axis=1)

        


if __name__ == "__main__":
    
    df_beach = pd.DataFrame([["36º 30' 23,999'' N", "04º 53' 12,344'' W"],
                             ["42º 30' 34,263'' N", "08º 49' 01,086'' W"]], columns=["Coordena_3","Coordena_2"])
    day_delay = 1 # máx 6
    hour = 17
    print(table_processing(df_beach, day_delay, hour))


