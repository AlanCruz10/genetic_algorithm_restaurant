import random


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
