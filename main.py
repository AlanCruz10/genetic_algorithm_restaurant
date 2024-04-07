import random
import time
import math
from genetic_algorithm import generic_algorithm
import csv
import requests
from credentials.google_maps.credentials.api_key import API_KEY


def calculate_distance(lat_rest, lng_rest, lat_person, lng_person):
        R = 6371

        phi1 = math.radians(lat_rest)
        phi2 = math.radians(lat_person)
        delta_phi = math.radians(lat_person - lat_rest)
        delta_lambda = math.radians(lng_person - lng_rest)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance


def individual_evaluation_function(restaurant, geolocation, geolocation_municipality, type_food, list_restaurants):
    weight_evaluation = 0.2
    weight_rating = 0.2
    weight_reservations = 0.17
    weight_location = 0.16
    weight_location_indeterminate = 0.16 / 2
    weight_food = 0.135
    weight_frequency = 0.135
    min_reservations = min(rest["reservations"] for rest in list_restaurants)
    min_frequency = min(rest["frequency"] for rest in list_restaurants)
    max_reservations = max(rest["reservations"] for rest in list_restaurants)
    max_frequency = max(rest["frequency"] for rest in list_restaurants)
    evaluation = (restaurant["evaluation"] - 0) / (5 - 0)
    rating = (restaurant["rating"] - 0) / (5 - 0)
    reservations = (restaurant["reservations"] - min_reservations) / (max_reservations - min_reservations)
    frequency = (restaurant["frequency"] - min_frequency) / (max_frequency - min_frequency)
    localization = get_localization_by_municipality(restaurant["location"])
    if localization["status"]:
        if geolocation["status"]:
            distance = weight_location * calculate_distance(localization["lat"], localization["lng"],
                                                            geolocation["lat"], geolocation["lng"])
        elif geolocation_municipality["status"]:
            distance = weight_location * calculate_distance(localization["lat"], localization["lng"],
                                                            geolocation_municipality["lat"],
                                                            geolocation_municipality["lng"])
        else:
            distance = 0
    else:
        distance = weight_location_indeterminate * -1

    if restaurant["food"] != type_food:
        weight_food = 0
    return weight_evaluation * evaluation + weight_rating * rating + weight_reservations * reservations + distance + weight_food + weight_frequency * frequency


# def create_individual(i, restaurant):
#     return {
#         "id": i,
#         "name": restaurant[0],
#         "rating": restaurant[1],
#         "reservations": restaurant[2],
#         "frequency": restaurant[3],
#         "evaluation": restaurant[4],
#         "location": restaurant[5],
#         "food": restaurant[6]
#     }


def generate_initial_population(list_restaurants, initial_population, recommendations, geolocation,
                                geolocation_municipality, type_food):
    recommendation = []
    while len(recommendation) < initial_population:
        list_restaurants_recommended = random.sample(list_restaurants, recommendations)
        fitness = 0
        for restaurant in list_restaurants_recommended:
            restaurant["fitness_individual"] = individual_evaluation_function(restaurant, geolocation,
                                                                              geolocation_municipality,
                                                                              type_food,
                                                                              list_restaurants)
            fitness += restaurant["fitness_individual"]
        individual = {
            "fitness": fitness,
            "restaurants": list_restaurants_recommended[:]
        }
        if individual not in recommendation:
            recommendation.append(individual)
        list_restaurants_recommended.clear()
    return recommendation


def gar(list_restaurants, geolocation, geolocation_municipality, type_food, init_population, recommendations,
        max_population,
        prob_mut_gen, prob_mut_ind, iterations, opt):
    print(generate_initial_population(list_restaurants, init_population, recommendations, geolocation,
                                geolocation_municipality, type_food))


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
                print("Error al obtener la información del municipio.")
                geolocation_municipality["status"] = False
                success = True
        else:
            print("Error al realizar la solicitud:", response.status_code)
            time.sleep(1)
    return geolocation_municipality


if __name__ == '__main__':
    geolocation = {}
    list_restaurants = []

    # selected municipality
    municipality = ""
    with open('municipios.csv', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for fila in lector_csv:
            if fila[0] == "Tonalá":
                municipality = fila[0]

    geolocation_municipality = get_localization_by_municipality(municipality)

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
            geolocation["status"] = True
        else:
            print("Error al obtener la ubicacion.")
            geolocation["status"] = True
    else:
        print("Error al obtener la ip publica.")

    type_food = ""

    with open('restaurantes chiapas.csv', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for i, fila in enumerate(lector_csv):
            if i != 0:
                list_restaurants.append({
                    "id": i - 1,
                    "name": fila[0],
                    "rating": float(fila[1].replace(",", ".")),
                    "reservations": int(fila[2]),
                    "frequency": int(fila[3]),
                    "evaluation": float(fila[4].replace(",", ".")),
                    "location": fila[5],
                    "food": fila[6]
                })
                if fila[6] == "Sushi":
                    type_food = fila[6]

    print(geolocation_municipality)
    print(geolocation)

    gar(list_restaurants, geolocation, geolocation_municipality, type_food, 10, 3, 5, 0.25, 0.35, 50, "max")
