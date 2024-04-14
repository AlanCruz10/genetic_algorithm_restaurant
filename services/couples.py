
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
