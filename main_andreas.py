import random
import math
import numpy as np
import copy
from plotter import Plotter
import matplotlib.pyplot as plt

evolutionary_fitness = True

alwaysC = [1, 1]
tft = [0, 1]
reverseTft = [1, 0]
alwaysD = [0, 0]
# payoffMatrix = [[[0, 0], [2, 0]], [[0, 2], [1, 1]]] # För coffee game
payoffMatrix = [[[1, 1], [5, 0]], [[0, 5], [3, 3]]] # Prisoner's Dilemma

noise = 0.0001
rounds = 100
population = 1000
generations = 10000
max_memory = 4
growth_rate = 0.1
pp = 0.00002  # Chansen att "point mutation" för varje gen i varje genom
pd = 0.00001  # Chansen att "duplication" genom att kopiera samma genom och adderar den, alltså [0 1 1 0] -> [0 1 1 0 0 1 1 0]
ps = 0.00001  # Chansen att "split mutation", alltså dela den i två och väljer at random den första eller andra hälften

strategies = int(population / 4) * [alwaysC] + int(population / 4) * [alwaysD] + int(population / 4) * [tft] + int(population / 4) * [reverseTft]
#strategies = [alwaysC] + [alwaysD]
print("strategies: ", strategies)
#strategies = int(population/4)*[tft]

lookup_table1 = [[0], [1]]
lookup_table2 = [[0, 0], [0, 1], [1, 0], [1, 1]]
lookup_table3 = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [0, 1, 1], [1, 1, 1]]
lookup_table4 = [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0],
                 [1, 0, 0, 1], [1, 0, 1, 0], [1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 0],
                 [0, 0, 1, 1], [1, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
lookup_table = [lookup_table1] + [lookup_table2] + [lookup_table3] + [lookup_table4]



def split_genome(genome):
    if len(genome) == 2:  # Kan inte dela på den om den bara har längd 2
        return genome

    rand = random.uniform(0, 1)
    first_half = genome[:len(genome) // 2]
    second_half = genome[len(genome) // 2:]
    #print("first_half: ", first_half)
    #print("second_half: ", second_half)
    if rand < 0.5:
        return first_half

    else:
        return second_half


def duplicate_genome(genome):
    if len(genome) >= 2 ** max_memory:
        return genome

    else:
        return genome + genome


def point_mutation(genome):
    for i in range(len(genome)):
        rand = random.uniform(0, 1)

        if rand <= pp:
            # print("När händer detta?????")
            # print("genome: ", genome)
            if genome[i] == 0:
                genome[i] = 1
            else:
                genome[i] = 0

    return genome


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


# Ska spela spelet här, alla i unique_strategies ska möta varande x antal gånger, får kolla upp hur många gånger det är i PDFen
# Hittade inte hur många gånger alla strategier ska möta varandra. Sätter det till 100 gånger för tillfället
def game(strategies, rounds, generations):
    count = 0
    fig, ax = plt.subplots(1, 2, figsize=(13, 9))
    fig.tight_layout(pad=15.0)
    while count < generations:
        unique_strategies, strategies_occurance = get_strategies(strategies)
        # print("unique strategies for generation ", count + 1, ": ", unique_strategies)
        average_score_i = np.zeros(len(unique_strategies))
        strategies_fraction = np.array(strategies_occurance) / sum(strategies_occurance)
        strategy_points = np.zeros([len(unique_strategies), len(unique_strategies)])
        # print("unique_strategies: ", unique_strategies)
        # print("strategy_occurance: ", strategies_occurance)

        for i in range(len(unique_strategies)):
            for j in range(i, len(unique_strategies)):

                strategy_loop_points = np.zeros(len(unique_strategies))
                strategy1 = unique_strategies[i]
                strategy2 = unique_strategies[j]
                strategy1_history = []
                strategy2_history = []
                history_length1 = int(math.log(len(strategy1), 2))
                history_length2 = int(math.log(len(strategy2), 2))

                # Måste köra alla strategier mot varandra så många gånger strategierna finns med i listan av strategier.
                # T.ex. om vi bara har always cooperate 1000 gånger måste de alla möta varandra eftersom vi har en lite chans
                # att få mistake. Detta medför att vi måste gå igenom att genes i alla genomes så att de alla får en chans att bli fel.
                # for _ in range(strategies_occurance[i]):
                    # Jag måste gör om strategy_history i denna loopen, det är pga detta som len(strategy_history) blir längre för det
                    # strategier som spelas flera gånger får mycket mer poäng, kanske faktiskt är detta som är stora felet.
                    # Kanske är löst nu genom att bara lägga in dessa två rader under här.
                    #strategy2_history = []
                    #strategy1_history = []
                for k in range(rounds):  # Spelar strategi1 mot strategi2 i rounds antal ronder
                    player1_choice, player2_choice = play_game(strategy1, strategy2, strategy1_history,
                                                               strategy2_history, history_length1, history_length2)

                    player1_choice = mistake(player1_choice)
                    player2_choice = mistake(player2_choice)
                    strategy1_history.append(player1_choice)
                    strategy2_history.append(player2_choice)

                strategy1_points, strategy2_points = get_points(strategy1_history, strategy2_history)
                strategy_loop_points[i] += sum(strategy1_points)
                strategy_loop_points[j] += sum(strategy2_points)

                # Efter att vi har gått igenom en strategi så många gånger den finns, så vill vi lösa ekvation (3) från PDFen.
                # Här kommer vi nu att ha en matris som vi vill fylla med gij*xj från ekvation (3). Med detta kan vi sen lätt
                # beräkna si och sen s. Tänker att strategy_points nu kommer vara gij*xj
                if i != j:
                    strategy_points[i, j] = strategy_loop_points[i] * strategies_fraction[j]
                    strategy_points[j, i] = strategy_loop_points[j] * strategies_fraction[i]
                else:
                    # Dessa blir fortfarande fel??
                    #print("strategy_loop_points: ", strategy_loop_points[j]/2, " with index: ", j)
                    strategy_points[j, j] = strategy_loop_points[j]/2 * strategies_fraction[j]
                #print("strategy1: ", strategy1, "  len(strategy1_points):", len(strategy1_points), "      points: ", strategy1_points)
                #print("strategy2: ", strategy2, "  len(strategy2_points):", len(strategy2_points), "      points: ", strategy2_points)
            if i == (len(unique_strategies) - 1):
                strategy_points[i, i] = strategy_loop_points[i]/2 * strategies_fraction[i]
                #print("strategy_points:")
                #print(strategy_points)
                #strategy_points = strategy_points/strategy_points.sum()
                #print("strategy_point/strategy_points.sum()", strategy_points)
            #strategy_points = strategy_points / strategy_points.sum()
            #print("strategy_point/strategy_points.sum()", strategy_points)
            #print("strategy_points: ", strategy_points)
            average_score_i[i] = sum(strategy_points[i, :]) #* strategies_fraction[i]
        #     print("strategy_points[i, :]: ", strategy_points[i, :])
        #     print("strategies_fraction[i]: ", strategies_fraction[i])
        # print("strategy_points: ")
        # print(strategy_points)
        strategies = get_new_strategies(average_score_i, strategies_fraction, unique_strategies)
        count += 1
        #print("\n")
        if count % 100 == 0:
            average = sum(average_score_i)/len(average_score_i)/rounds
            color.update(unique_strategies, strategies_fraction, average, fig, ax)
            print(f"unique strategies:{unique_strategies}")
            print(f"fraction:{strategies_fraction}")
            print(f"average score:{average}")


def play_game(strategy1, strategy2, strategy1_history, strategy2_history, history_length1, history_length2):
    if len(strategy2_history) < history_length1 or len(strategy1_history) < history_length2:
        a=0
        b=0
        if 1 in strategy1[:2]:
            a +=1
        if 1 in strategy2[:2]:
            b +=1
        return a, b  # Detta stämmer inte. Måste också kolla hur lång "history_length" strategi 2 har, då
        # den kanske kan börja spela på sin strategi innan spelare ett gör det !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    else:
        history2 = strategy2_history[-history_length1:]  # Tar ut historiken för strategi 2 beroende på hur lång history vi ska kolla på
        history1 = strategy1_history[-history_length2:]  # Samma som ovan fast för strategi 1. Det är "history_length2" inom [] eftersom
        # beroende på hur lång historik strategi 2 kollar på måste vi plocka ut den
        # historiken från spelare1 historik

        # Tar ut vilket index som den historiken representerar för att sedan kunna
        # välja vilket val som ska göras m.a.p. den historiken
        index1 = lookup_table[history_length1 - 1].index(history2)
        index2 = lookup_table[history_length2 - 1].index(history1)

        choice1 = strategy1[index1]
        choice2 = strategy2[index2]

        return choice1, choice2


# Vill beräkna hur många poäng som strategi 1 får mot strategi 2. Måste också lägga in hur många poäng strategi 2 får då
# Detta måste jag göra efter varje iteration i dubbel-loopen i "def game" då alla strategier ska möta varandra och alla dessa poäng ska räknas med
# Måste sedan multiplicera deta värdet med hur många som har den här strategin, tror jag. Får kolla det i PDFen i ekvationerna
def get_points(strategy1_history, strategy2_history):
    strategy1_points = []
    strategy2_points = []

    for i in range(len(strategy1_history)):
        strategy1_payoff = payoffMatrix[strategy1_history[i]][strategy2_history[i]][0]
        strategy2_payoff = payoffMatrix[strategy1_history[i]][strategy2_history[i]][1]
        strategy1_points.append(strategy1_payoff)
        strategy2_points.append(strategy2_payoff)
    return strategy1_points, strategy2_points


def get_fitness_value(average_score_i, average_score):

    fitness = np.zeros(len(average_score_i))
    for i in range(len(fitness)):
        fitness[i] = average_score_i[i] - average_score

    return fitness


def get_mutations(strategies, strategies_fraction_next_generation, unique_strategies):

    for i in range(len(unique_strategies)):
        strategies += (int(strategies_fraction_next_generation[i] * population) * [unique_strategies[i]])

    missing_individuals = population - len(strategies)

    if missing_individuals > 0:
        for i in range(missing_individuals):
            strategies.append(unique_strategies[np.argmax(strategies_fraction_next_generation)])
    #print("strategies: ", strategies)
    for k in range(len(strategies)):

        rand_mutation = random.uniform(0, 1)

        if rand_mutation <= pd:
            strategies[k] = duplicate_genome(strategies[k])

        if rand_mutation >= (1 - ps):
            strategies[k] = split_genome(strategies[k])

        genome = copy.copy(strategies[k])
        strategies[k] = point_mutation(genome)

    return strategies


def fitness_evolution(average_score_i, strategies_fraction, strategies_fraction_next_generation):

    average_score = average_score_i.dot(strategies_fraction)
    # Beräknar fitnessvärdet w_i for de olika strategierna som finns, ekvation (5) i PDFen
    fitness = get_fitness_value(average_score_i, average_score)

    #print("fitness: ", fitness)
    # Beräknar nu ekvation (7) i PDFen, hur stor andel av nästa generation som ska vara av en viss strategi
    for i in range(len(fitness)):

        strategies_fraction_next_generation[i] = max(0, strategies_fraction[i] * (growth_rate * fitness[i] + 1))

    strategies_fraction_next_generation = strategies_fraction_next_generation / np.sum(strategies_fraction_next_generation)
    #print("strategies_fraction_next_generation: ", strategies_fraction_next_generation)

    return strategies_fraction_next_generation


def get_new_strategies(average_score_i, strategies_fraction, unique_strategies):

    strategies_fraction_next_generation = np.zeros(len(unique_strategies))

    if evolutionary_fitness:
        strategies_fraction_next_generation = fitness_evolution(average_score_i, strategies_fraction, strategies_fraction_next_generation)

    strategies = []

    strategies = get_mutations(strategies, strategies_fraction_next_generation, unique_strategies)

    return strategies


#strats = 99*[alwaysC] + [alwaysD]
color = Plotter()
game(strategies, rounds, generations)
#game(strats, rounds, generations)

#mistakes = mistake([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
#print("Testar mistake för att se hur ofta den används ungefär: ", mistakes)

#poang1, poang2, = get_points([0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0])
#print("poäng strategi 1: ", sum(poang1))
#print("poäng strategi 2: ", sum(poang2))

# Det är något fel med fitnessgrejen, hur man väljer vilka som ska med till nästa generation.
# Tror inte att det är några fel på beräkningarna för g_ij, x_i, s_i eller s längre, tror bara att det är hur man beräknar vilka som
# ska med till nästa generation som är felet... Kanske kolla på att normalisera strategy_points så att den summeras till ett innan
# man beräknar fitnessfunktionen. Har lite sånt i koden men bortkommenterat

# Tror nästan på att hitta på ett eget sätt att beräkna hur stor andel ska med till nästa generation.
# Vet dock inte hur det ska se ut riktigt. Just nu tycker jag att