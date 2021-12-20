import random
import math
import numpy as np
import copy

from matplotlib import pyplot as plt

from Lattice_dubbelraknar import Plotter, Lattice

evolutionary_fitness = True

alwaysC = [1, 1]
tft = [0, 1]
reverseTft = [1, 0]
alwaysD = [0, 0]
payoffMatrix = [[[0, 0], [2, 1]], [[1, 2], [1, 1]]] # För coffee game
#payoffMatrix = [[[1, 1], [5, 0]], [[0, 5], [3, 3]]]  # Prisoner's Dilemma, R = 1, S = 0, T = 1.7, P = 0.7
#payoffMatrix = [[[1, 1], [0, 1.6]], [[1.6, 0], [0.3, 0.3]]]
lattice_size = 32

noise = 0.001
rounds = 20
population = lattice_size*lattice_size

generations = 10000
max_memory = 3
pp = 0.002  # Chansen att "point mutation" för varje gen i varje genom
pd = 0.001  # Chansen att "duplication" genom att kopiera samma genom och adderar den, alltså [0 1 1 0] -> [0 1 1 0 0 1 1 0]
ps = 0.001  # Chansen att "split mutation", alltså dela den i två och väljer at random den första eller andra hälften


mutation_rates = {'pp': pp, 'pd': pd, 'ps': ps, 'max_memory': max_memory}
strategies = int(population / 4) * [alwaysC] + int(population / 4) * [alwaysD] + int(population / 4) * [tft] + int(
    population / 4) * [reverseTft]
#print("strategies: ", strategies)

lookup_table1 = [[0], [1]]
lookup_table2 = [[0, 0], [0, 1], [1, 0], [1, 1]]
lookup_table3 = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [0, 1, 1], [1, 1, 1]]
lookup_table4 = [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0],
                 [1, 0, 0, 1], [1, 0, 1, 0], [1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 0],
                 [0, 0, 1, 1], [1, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
lookup_table = [lookup_table1] + [lookup_table2] + [lookup_table3] + [lookup_table4]


def mistake(gene):
    rand = random.uniform(0, 1)

    if rand <= noise:

        if gene == 0:
            gene = 1
        else:
            gene = 0

    return gene


def get_strategies(strategies):
    unique_strategies = [list(x) for x in set(tuple(x) for x in strategies)]
    strategies_occurance = []

    for i in range(len(unique_strategies)):
        strategies_occurance.append(strategies.count(unique_strategies[i]))

    return unique_strategies, strategies_occurance


def play_game(strategy1, strategy2, strategy1_history, strategy2_history, history_length1, history_length2):
    if len(strategy2_history) < history_length1 or len(strategy1_history) < history_length2:
        a = 0
        b = 0
        if 1 in strategy1[:2]:
            a += 1
        if 1 in strategy2[:2]:
            b += 1
        return a, b  # Detta stämmer inte. Måste också kolla hur lång "history_length" strategi 2 har, då
        # den kanske kan börja spela på sin strategi innan spelare ett gör det !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    else:
        history2 = strategy2_history[
                   -history_length1:]  # Tar ut historiken för strategi 2 beroende på hur lång history vi ska kolla på
        history1 = strategy1_history[
                   -history_length2:]  # Samma som ovan fast för strategi 1. Det är "history_length2" inom [] eftersom

        index1 = lookup_table[history_length1 - 1].index(history2)
        index2 = lookup_table[history_length2 - 1].index(history1)

        choice1 = strategy1[index1]
        choice2 = strategy2[index2]

        return choice1, choice2


def get_points(strategy1_history, strategy2_history):
    strategy1_points = []
    strategy2_points = []

    for i in range(len(strategy1_history)):
        strategy1_payoff = payoffMatrix[strategy1_history[i]][strategy2_history[i]][0]
        strategy2_payoff = payoffMatrix[strategy1_history[i]][strategy2_history[i]][1]
        strategy1_points.append(strategy1_payoff)
        strategy2_points.append(strategy2_payoff)
    return strategy1_points, strategy2_points


def game(strategies, rounds, generations):
    count = 0
    fig, ax = plt.subplots(1, 2, figsize=(13,9))
    fig.tight_layout(pad=15.0)
    unique_strategies, strategies_occurance = get_strategies(strategies)
    strategies_fraction = np.array(strategies_occurance) / sum(strategies_occurance)
    lattice.init_lattice_random(unique_strategies, strategies_fraction)
    lattice.plot_lattice(fig, ax, title_text=f'Generation{count}')
    #color.update(unique_strategies, strategies_fraction, fig, ax, plot_every)

    while count < generations:
        # DEN DUBBELRÄKNAR MYCKET NU, FIXA DET eller??
        # för varje position i matris, kollar neumann neighbours och spelar mot dom.
        for i, coord in enumerate(lattice.all_coord):
            neighbours = lattice.neumann_neighbours(coord)
            corresponding_value_in_lattice = lattice.lattice_matrix[coord[0], coord[1]]
            strategy1 = lattice.dict_unique_strategies_values.get(str(corresponding_value_in_lattice))

            strategy_loop_points = np.zeros((2, len(neighbours)))

            for j, neighbour_coord in enumerate(neighbours):
                corresponding_value_in_lattice2 = lattice.lattice_matrix[neighbour_coord[0], neighbour_coord[1]]
                strategy2 = lattice.dict_unique_strategies_values.get(str(corresponding_value_in_lattice2))

                strategy1_history = []
                strategy2_history = []

                history_length1 = int(math.log(len(strategy1), 2))
                history_length2 = int(math.log(len(strategy2), 2))

                for k in range(rounds):  # Spelar strategi1 mot strategi2 i rounds antal ronder
                    player1_choice, player2_choice = play_game(strategy1, strategy2, strategy1_history,
                                                               strategy2_history, history_length1, history_length2)

                    player1_choice = mistake(player1_choice)
                    player2_choice = mistake(player2_choice)
                    strategy1_history.append(player1_choice)
                    strategy2_history.append(player2_choice)

                strategy1_points, strategy2_points = get_points(strategy1_history, strategy2_history)
                strategy_loop_points[0, j] += sum(strategy1_points)
                strategy_loop_points[1, j] += sum(strategy2_points)

            # när en person mött alla sina grannar så uppdateras spel-matrisen.
            lattice.update_lattice(strategy_loop_points, coord, neighbours, mutation_rates)

        count += 1
        # när alla spelat mot alla så uppdateras allt synchronous.
        lattice.lattice_matrix = lattice.updated_lattice

        # print("\n")
        plot_every = 5
        if count % plot_every == 0:
            strategies_fraction, unique_strategies = lattice.get_strategy_fractions()
            lattice.plot_lattice(fig, ax, title_text=f'Generation {count}')
            color.update(unique_strategies, strategies_fraction, fig, ax, plot_every)
            #print(f"unique strategies:{unique_strategies}")
            #print(f"fraction:{strategies_fraction}")


lattice = Lattice(lattice_size)
color = Plotter()
game(strategies, rounds, generations)
