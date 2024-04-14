import requests
import time
from configurations.google_maps.credentials.api_key import API_KEY
from configurations.geopy.credentials.user_agent import USER_AGENT
from geopy.geocoders import Nominatim


def get_localization_by_municipality(municipality):
    geolocation_municipality = {}
    success = False
    while not success:
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
                geolocation_municipality["status"] = True
                success = True
            else:
                print("Error al obtener la informacion del municipio.")
                geolocation_municipality["status"] = False
                success = True
        else:
            print("Error al realizar la solicitud:", response.status_code)
            time.sleep(1)
    return geolocation_municipality


def get_localization_by_municipality_using_geopy(municipality):
    geolocator = Nominatim(user_agent=USER_AGENT)
    geolocation_municipality = {}
    success = False
    attempts = 0
    while not success and attempts < 5:
        try:
            location = geolocator.geocode(municipality)
            if location:
                geolocation_municipality["address"] = location.address
                geolocation_municipality["lat"] = location.latitude
                geolocation_municipality["lng"] = location.longitude
                geolocation_municipality["status"] = True
                success = True
            else:
                print("Error al obtener la informacion del municipio.")
                geolocation_municipality["status"] = False
                success = True
        except Exception:
            geolocation_municipality["status"] = False
            attempts += 1
    return geolocation_municipality

