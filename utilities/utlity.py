import random
import math
import numpy as np
from utilities.geolocation.geolocation import get_localization_by_municipality_using_geopy
from geopy.distance import geodesic


def calculate_distance(lat_rest, lng_rest, lat_person, lng_person):
    # earth radius in kilometers
    '''
    R = 6371
    # haversine formula
    phi1 = math.radians(lat_rest)
    phi2 = math.radians(lat_person)
    delta_phi = math.radians(lat_person - lat_rest)
    delta_lambda = math.radians(lng_person - lng_rest)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    '''

    distance = geodesic((lat_rest, lng_rest), (lat_person, lng_person)).kilometers
    print("Distancia -> ", distance)

    return distance


def individual_evaluation_function(restaurant, geolocation, geolocation_municipality, type_food, list_restaurants):
    # weights
    weight_evaluation = 0.2
    weight_rating = 0.2
    weight_reservations = 0.17
    weight_location = 0.16
    weight_location_indeterminate = 0.16 / 2
    weight_food = 0.135
    weight_frequency = 0.135
    penalty = 0.5
    alpha = 0.1
    beta = 1

    # normalization from data
    min_reservations = min(rest["reservations"] for rest in list_restaurants)
    min_frequency = min(rest["frequency"] for rest in list_restaurants)
    max_reservations = max(rest["reservations"] for rest in list_restaurants)
    max_frequency = max(rest["frequency"] for rest in list_restaurants)
    evaluation = (restaurant["evaluation"] - 0) / (5 - 0)
    rating = (restaurant["rating"] - 0) / (5 - 0)

    # Apply alpha-beta normalization
    reservations = rating * (alpha + (beta - alpha) * ((restaurant["reservations"] - min_reservations) / (max_reservations - min_reservations)))
    frequency = rating * (alpha + (beta - alpha) * ((restaurant["frequency"] - min_frequency) / (max_frequency - min_frequency)))
    print("Reservations -> ", reservations)
    print("Frequency -> ", frequency)

    # Rest of the function...
    if restaurant["status"]:
        if geolocation["status"]:
            # normalization from distance with logarithmic transformation
            distance_km = calculate_distance(restaurant["lat"], restaurant["lng"], geolocation["lat"],
                                             geolocation["lng"])
            # distance_calculated = np.log(distance_km + 1)
            # distance = weight_location * distance_calculated
            distance = weight_location * distance_km
        elif geolocation_municipality["status"]:
            # normalization from distance with logarithmic transformation
            distance_km = calculate_distance(restaurant["lat"], restaurant["lng"], geolocation_municipality["lat"],
                                             geolocation_municipality["lng"])
            # distance_calculated = np.log(distance_km + 1)
            distance = weight_location * distance_km
            if distance != 0:
                distance = weight_location * distance_km
            else:
                distance = -1 * weight_location * penalty
        else:
            distance_km = None
            distance = 0
    else:
        distance_km = None
        distance = -1 * weight_location_indeterminate * penalty

    if restaurant["food"] != type_food:
        weight_food = 0

    # return weighted sum and distance in km
    return (weight_evaluation * evaluation + weight_rating * rating + weight_reservations * reservations + weight_food + weight_frequency * frequency)/distance, distance_km


def generate_initial_population(list_restaurants, initial_population, recommendations, geolocation,
                                geolocation_municipality, type_food):
    recommendation = []
    while len(recommendation) < initial_population:
        # list from 3 restaurants unique random
        list_restaurants_recommended = random.sample(list_restaurants, recommendations)
        # fitness global, individual and distance in km added
        fitness = 0
        for restaurant in list_restaurants_recommended:
            fitness_individual, distance_km = individual_evaluation_function(restaurant, geolocation,
                                                                             geolocation_municipality,
                                                                             type_food,
                                                                             list_restaurants)
            restaurant["fitness_individual"] = fitness_individual
            restaurant["distance_km"] = distance_km
            fitness += fitness_individual
        individual = {
            "fitness": fitness,
            "restaurants": list_restaurants_recommended[:]
        }
        # add if not is present before
        if individual not in recommendation:
            recommendation.append(individual)
        list_restaurants_recommended.clear()
    return recommendation


def geolocation_restaurants(list_restaurants):
    for restaurant in list_restaurants:
        localization = get_localization_by_municipality_using_geopy(restaurant["location"])
        restaurant["status"] = localization["status"]
        restaurant["lat"] = localization["lat"]
        restaurant["lng"] = localization["lng"]
    return list_restaurants
