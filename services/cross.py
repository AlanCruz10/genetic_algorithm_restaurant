import random


def cross(couples):
    children = []
    for (fc, sc) in couples:
        # point cross random
        point_cross = random.randint(0, len(fc["restaurants"]))

        # fc["restaurants"][:point_cross] in sc["restaurants"][point_cross:]
        fc_before_cross = fc["restaurants"][:point_cross]
        sc_after_cross = sc["restaurants"][point_cross:]
        should_cross = not any(restaurant in sc_after_cross for restaurant in fc_before_cross)

        if should_cross:
            # do cross
            list_restaurants_fc = fc_before_cross + sc_after_cross
            list_restaurants_sc = sc["restaurants"][:point_cross] + fc["restaurants"][point_cross:]

            fitness_fc = sum(restaurant["fitness_individual"] for restaurant in list_restaurants_fc)
            fitness_sc = sum(restaurant["fitness_individual"] for restaurant in list_restaurants_sc)

            # Add sons to list children
            new_individual_fc = {
                "fitness": fitness_fc,
                "restaurants": list_restaurants_fc
            }
            new_individual_sc = {
                "fitness": fitness_sc,
                "restaurants": list_restaurants_sc
            }
            # Check if new individuals already exist in children
            if new_individual_fc not in children:
                children.append(new_individual_fc)
            if new_individual_sc not in children:
                children.append(new_individual_sc)

    return children
