import random
from utilities.utlity import individual_evaluation_function


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
