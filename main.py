from genetic_algorithm import generic_algorithm
import csv
import requests
from credentials.google_maps.credentials.api_key import API_KEY

if __name__ == '__main__':
    geolocation = {}
    geolocation_municipality = {}

    # selected municipality
    municipality = ""
    with open('municipios.csv', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for fila in lector_csv:
            if fila[0] == "Tuxtla Gutiérrez":
                municipality = fila[0]

    # lat and lng of municipality
    endpoint = f'https://maps.googleapis.com/maps/api/geocode/json?address={municipality}&region=chp&key={API_KEY}'
    # endpoint = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&region=chp&key={API_KEY}'
    response = requests.get(endpoint)
    if response:
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            geolocation_municipality["address"] = data['results'][0]['formatted_address']
            geolocation_municipality["lat"] = location['lat']
            geolocation_municipality["lng"] = location['lng']
        else:
            print("Error al obtener la información del municipio.")
    else:
        print("Error al realizar la solicitud:", response.status_code)

    # ip_public
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    if data:
        # geolocation
        response = requests.get(f"http://ip-api.com/json/{data['ip']}")
        response_json = response.json()
        if response_json["status"] == "success":
            geolocation["city"] = response_json["city"]
            geolocation["country"] = response_json["country"]
            geolocation["regionName"] = response_json["regionName"]
            geolocation["lat"] = response_json["lat"]
            geolocation["lng"] = response_json["lon"]
        else:
            print("Error al obtener la ubicacion.")
    else:
        print("Error al obtener la ip publica.")

    print(geolocation_municipality)
    print(geolocation)
