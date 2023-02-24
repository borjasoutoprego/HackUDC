
# MÓDULO PARA OBTENER DATOS CLIMÁTICOS DE LAS PLAYAS

import requests

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

    print(response.json()['forecast']['forecastday'][-1]['hour'][0])
    print(response_wave.json()['hourly']['wave_height'][24*day_delay + hour])
    print(response.json()['location']['name'])


if __name__ == "__main__":

    lat_dms = "36º 30' 23,999'' N"
    lon_dms = "04º 53' 12,344'' W"
    day_delay = 6 # máx 6
    hour = 23

    get_data(lat_dms, lon_dms, day_delay, hour)

# time
# temp
# is_day
# condition
# wind
# wind dir
# pressure
# precip
# humidity
# cloud
# feelslike
# windchill (cuanto enfria el viento)
# dew point (punto de rocio)
# rain
# chance of rain
# snow
# chance of snow
# visibility
# wind gust (rachas de viento)
# uv
# wave height



