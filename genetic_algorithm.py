from utilities.utlity import generate_initial_population, geolocation_restaurants
from services.statistics import save_statistics
from services.couples import generation_couples
from services.cross import cross
from services.mutation import mutation
from services.pruning import pruning


def genetic_algorithm_restaurant(list_restaurants, geolocation, geolocation_municipality, type_food, init_population,
                                 recommendations, max_population, prob_cross, prob_mut_gen, prob_mut_ind, iterations,
                                 opt):
    population_by_generation = {}
    list_statistics_by_generation = []
    # calculate lat and lng of restaurants
    restaurants = geolocation_restaurants(list_restaurants)
    # generate initial population
    population = generate_initial_population(restaurants, init_population, recommendations, geolocation,
                                             geolocation_municipality, type_food)
    print("Individuo -> ", population[0])
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
