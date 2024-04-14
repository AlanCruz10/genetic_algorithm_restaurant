import random


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
