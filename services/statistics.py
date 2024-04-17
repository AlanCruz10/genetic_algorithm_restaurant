import matplotlib.pyplot as plt

def save_statistics(population, optimization):
    # obtained the fitness of individuals
    fitness = [p["fitness"] for p in population]
    # check if it is max or min
    if optimization == "Maximizacion":
        best = max(fitness)
        worst = min(fitness)
    else:
        best = min(fitness)
        worst = max(fitness)
        
    # calculate the average
    average_evaluated = sum(fitness) / len(fitness)
    individual_best = None
    individual_worst = None
    
    # obtain the individual (best and worst)
    for p in population:
        if p["fitness"] == best:
            individual_best = p
        if p["fitness"] == worst:
            individual_worst = p

    # return statistics
    return {"best": individual_best, "worst": individual_worst, "average": average_evaluated}
