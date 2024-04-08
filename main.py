import random
import time
import math
from geopy.geocoders import Nominatim
# from genetic_algorithm import generic_algorithm
import csv
import requests
from configurations.google_maps.credentials.api_key import API_KEY
from configurations.geopy.credentials.user_agent import USER_AGENT


def read_data():
    list_restaurants = {}
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
    return list_restaurants


def pruning(population, best, max_population):
    # deleted repeats
    key_unique = set()
    population_unique = []
    for individual in population:
        restaurants_tuple = tuple(tuple(restaurant.items()) for restaurant in individual["restaurants"])
        if restaurants_tuple not in key_unique:
            key_unique.add(restaurants_tuple)
            population_unique.append(individual)
    # check that the size of the list population_unique is less than the max_population
    while len(population_unique) > max_population:
        # pruning maintaining the best
        population_pruned = []
        for individual in population_unique:
            if individual != best:
                if round(random.uniform(0, 1.0001), 4) < 0.5:
                    population_pruned.append(individual)
        population_pruned.append(best)
        population_unique = population_pruned
    # return list population below the maximum population and keeping the best of the best
    return population_unique


def save_statistics(population, optimization):
    # obtained te fitness of individuals
    fitness = [p["fitness"] for p in population]
    # check if is max or min
    if optimization == "Maximización":
        worst = max(fitness)
        best = min(fitness)
    else:
        best = min(fitness)
        worst = max(fitness)
    # calculate the average
    average_evaluated = sum(fitness) / len(fitness)
    individual_best = None
    individual_worst = None
    # obtained the individual (best and worst)
    for p in population:
        if p["fitness"] == best:
            individual_best = p
        if p["fitness"] == worst:
            individual_worst = p
    # returned statistic
    return {"best": individual_best, "worst": individual_worst, "average": average_evaluated}


def mutation(children, prob_mut_gen, prob_mut_ind, list_restaurants, geolocation, geolocation_municipality, type_food):
    children_mutated = []
    for son in children:
        # check the probability of mutation of the individual that is better than prob_mut_ind
        if round(random.uniform(0, 1.0001), 4) >= prob_mut_ind:
            fitness = 0
            list_restaurants_mutated = []
            for restaurant in son["restaurants"]:
                # check the probability of mutation of each restaurant that is better than prob_mut_gen
                if round(random.uniform(0, 1.0001), 4) >= prob_mut_gen:
                    repeated = False
                    # repeat the process if present in son["restaurants"]
                    while not repeated:
                        # obtained one restaurant randomly
                        rest = random.sample(list_restaurants, 1)[0]
                        # added fitness individual and distance in km
                        fitness_individual, distance_km = individual_evaluation_function(rest, geolocation,
                                                                                         geolocation_municipality,
                                                                                         type_food, list_restaurants)
                        rest["fitness_individual"] = fitness_individual
                        rest["distance_km"] = distance_km
                        # checked that restaurant of db not present in son["restaurants"]
                        if rest not in son["restaurants"]:
                            if rest not in list_restaurants_mutated:
                                repeated = True
                                restaurant = {**restaurant, **rest}
                list_restaurants_mutated.append(restaurant)
                fitness += restaurant["fitness_individual"]
            son_mutated = {
                "fitness": fitness,
                "restaurants": list_restaurants_mutated
            }
            # update fitness of individual (son) and the list of restaurants of son (son["restaurants"])
            son = {**son, **son_mutated}
        children_mutated.append(son)
    # returned the children mutated
    return children_mutated


def cross(couples):
    children = []
    for (fc, sc) in couples:
        # point cross random
        point_cross = random.randint(0, len(fc))
        # do cross
        list_restaurants_fc = fc["restaurants"][:point_cross] + sc["restaurants"][point_cross:]
        list_restaurants_sc = sc["restaurants"][:point_cross] + fc["restaurants"][point_cross:]
        # update fitness global with new crosses
        fitness_fc = sum(restaurant["fitness_individual"] for restaurant in list_restaurants_fc)
        fitness_sc = sum(restaurant["fitness_individual"] for restaurant in list_restaurants_sc)
        # add sons to list children
        children.append({
            "fitness": fitness_fc,
            "restaurants": list_restaurants_fc
        })
        children.append({
            "fitness": fitness_sc,
            "restaurants": list_restaurants_sc
        })
    return children


def generation_couples(population, prob_cross):
    # population sorted from least to most fitness
    sorted_population = sorted(population, key=lambda x: x['fitness'])
    # population partitioning
    index_separation = len(sorted_population) - len(sorted_population) // 2
    first_part = sorted_population[:index_separation]
    second_part = sorted_population[index_separation:]
    # forming couples
    couples = []
    for fp in first_part:
        for sp in second_part:
            couples.append((fp, sp))
    return couples


def calculate_distance(lat_rest, lng_rest, lat_person, lng_person):
    # earth radius in kilometers
    R = 6371
    # haversine formula
    phi1 = math.radians(lat_rest)
    phi2 = math.radians(lat_person)
    delta_phi = math.radians(lat_person - lat_rest)
    delta_lambda = math.radians(lng_person - lng_rest)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
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
    # standardization from data
    min_reservations = min(rest["reservations"] for rest in list_restaurants)
    min_frequency = min(rest["frequency"] for rest in list_restaurants)
    max_reservations = max(rest["reservations"] for rest in list_restaurants)
    max_frequency = max(rest["frequency"] for rest in list_restaurants)
    evaluation = (restaurant["evaluation"] - 0) / (5 - 0)
    rating = (restaurant["rating"] - 0) / (5 - 0)
    reservations = (restaurant["reservations"] - min_reservations) / (max_reservations - min_reservations)
    frequency = (restaurant["frequency"] - min_frequency) / (max_frequency - min_frequency)
    localization = get_localization_by_municipality_using_geopy(restaurant["location"])
    if localization["status"]:
        if geolocation["status"]:
            # normalization from distance with logarithmic transformation
            distance_km = calculate_distance(localization["lat"], localization["lng"], geolocation["lat"],
                                             geolocation["lng"])
            # distance_calculated = np.log(distance_km + 1)
            # distance = weight_location * distance_calculated
            distance = weight_location * distance_km
        elif geolocation_municipality["status"]:
            # normalization from distance with logarithmic transformation
            distance_km = calculate_distance(localization["lat"], localization["lng"], geolocation["lat"],
                                             geolocation["lng"])
            # distance_calculated = np.log(distance_km + 1)
            # distance = weight_location * distance_calculated
            distance = weight_location * distance_km
        else:
            distance_km = None
            distance = 0
    else:
        distance_km = None
        distance = -1 * weight_location_indeterminate

    if restaurant["food"] != type_food:
        weight_food = 0
    # return weighted sum and distance in km

    return weight_evaluation * evaluation + weight_rating * rating + weight_reservations * reservations + distance + weight_food + weight_frequency * frequency, distance_km


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


def print_list(list_rest):
    for r in list_rest:
        print(r)


def gar(list_restaurants, geolocation, geolocation_municipality, type_food, init_population, recommendations,
        max_population, prob_cross, prob_mut_gen, prob_mut_ind, iterations, opt):
    population_by_generation = {}
    list_statistics_by_generation = []
    # generate initial population
    population = generate_initial_population(list_restaurants, init_population, recommendations, geolocation,
                                             geolocation_municipality, type_food)
    print("statistic 0")
    population_by_generation[0] = population
    # save statistics from generation initial
    statistics = save_statistics(population, opt)
    print(statistics)
    list_statistics_by_generation.append(statistics)
    population_copy = population
    for i in range(iterations):
        if len(population_copy) > 1:
            # generate couples
            print("couples")
            couples = generation_couples(population_copy, prob_cross)
            # print_list(couples)
            # making crosses
            children = cross(couples)
            print("cross")
            # print_list(children)
            # do mutation
            children_mutated = mutation(children, prob_mut_gen, prob_mut_ind, list_restaurants, geolocation,
                                        geolocation_municipality, type_food)
            print("mutation")
            # print_list(children_mutated)
            # add children to population
            population_copy = population_copy + children_mutated
            population_by_generation[i + 1] = population_copy
            # save statistics
            statistics = save_statistics(population_copy, opt)
            list_statistics_by_generation.append(statistics)
            print("statistics ", i + 1)
            print(statistics)
            # do pruning
            population_pruned = pruning(population_copy, statistics["best"], max_population)
            print("pruning")
            population_copy = population_pruned
    return population_copy, population_by_generation, list_statistics_by_generation


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
                print("Error al obtener la información del municipio.")
                geolocation_municipality["status"] = False
                success = True
        except Exception:
            geolocation_municipality["status"] = False
            attempts += 1
    return geolocation_municipality


if __name__ == '__main__':
    geolocation = {}
    list_restaurants = []

    # selected municipality
    municipality = ""
    with open('municipios.csv', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for fila in lector_csv:
            if fila[0] == "Tuxtla Gutiérrez":
                municipality = fila[0]

    # geolocation_municipality = get_localization_by_municipality(municipality)

    geolocation_municipality = get_localization_by_municipality_using_geopy(municipality)

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
    # print(geolocation_municipality_by_geopy)
    print(geolocation)

    population, population_by_generation, statistics = gar(list_restaurants, geolocation, geolocation_municipality,
                                                           type_food, 10, 3, 5, 0.25, 0.20, 0.35, 10,
                                                           "Maximización")
    print("------------------------------------------")
    print("population")
    print_list(population)
    print("by generation")
    for x in population_by_generation:
        print(x)
        print_list(population_by_generation[x])
    print("statistics")
    print_list(statistics)
