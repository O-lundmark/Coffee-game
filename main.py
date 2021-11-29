import alwaysDeflect, alwaysCooperate, titForTat, reverseTitForTat
import axelrod as axl
import random
import math
import numpy as np

alwaysC = [1, 1]
tft = [0, 1]
reverseTft = [1, 0]
alwaysD = [0, 0]
payoffMatrix = [[[0, 0], [2, 0]], [[0, 2], [1, 1]]]

noise = 0.01
rounds = 100
population = 1000
max_memory = 2
pp = 0.00002 # Chansen att "point mutation" för varje gen i varje genom
pd = 0.00001 # Chansen att "duplication" genom att kopiera samma genom och adderar den, alltså [0 1 1 0] -> [0 1 1 0 0 1 1 0]
ps = 0.00001 # Chansen att "split mutation", alltså dela den i två och väljer at random den första eller andra hälften

strategies = int(population/4)*[alwaysC] + int(population/4)*[alwaysD] + int(population/4)*[tft] + int(population/4)*[reverseTft]


lookup_table1 = [[0], [1]]
lookup_table2 = [[0, 0], [0, 1], [1, 0], [1, 1]]
lookup_table3 = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [0, 1, 1], [1, 1, 1]]
lookup_table4 = [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0],
                 [1, 0, 0, 1], [1, 0, 1, 0], [1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 0],
                 [0, 0, 1, 1], [1, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
lookup_table = [lookup_table1] + [lookup_table2] + [lookup_table3] + [lookup_table4]

"""
game = axl.game.Game()
print(game.score((axl.Action.C, axl.Action.C)))

coffeeGame = axl.game.Game(r=1, p=0, s=1, t=2)
print("AA: ", coffeeGame.score((axl.Action.C, axl.Action.C)))
print("AB: ", coffeeGame.score((axl.Action.C, axl.Action.D)))
print("BA: ", coffeeGame.score((axl.Action.D, axl.Action.C)))
print("BB: ", coffeeGame.score((axl.Action.D, axl.Action.D)))

players = [axl.Cooperator(), axl.Defector(), axl.TitForTat(), axl.Bully()] # Bully är reverse titfortat, inklusive första movet, börjar alltså med Deflect

tournament = axl.Tournament(players, noise=noise, turns=rounds, repetitions=1)

results = tournament.play()
print("Total score (payoff) for the ", rounds, " number of rounds for strategy always cooperate, always deflect, "
                                                 "titfortat and reverse titfortat respectively: ", results.scores)
print("Total normalised score (payoff) for the ", rounds, " number of rounds for strategy always cooperate, always deflect, "
                                                 "titfortat and reverse titfortat respectively: ", results.normalised_scores)

"""

def split_genome(genome):

    if len(genome) == 2: # Kan inte dela på den om den bara har längd 2
        return genome

    rand = random.uniform(0, 1)
    first_half = genome[:len(genome)//2]
    second_half = genome[len(genome)//2:]
    print("first_half: ", first_half)
    print("second_half: ", second_half)
    if rand < 0.5:
        return first_half

    else:
        return second_half


def duplicate_genome(genome):

    if len(genome) >= 2**max_memory:
        return genome

    else:
        return genome + genome


def point_mutation(genome):

    for i in range(len(genome)):
        rand = random.uniform(0, 1)

        if rand <= 0.5:

            if genome[i] == 0:
                genome[i] = 1
            else:
                genome[i] = 0

    return genome


def get_strategies(strategies):

    unique_strategies = [list(x) for x in set(tuple(x) for x in strategies)]
    strategies_occurance = []

    for i in range(len(unique_strategies)):
        strategies_occurance.append(strategies.count(unique_strategies[i]))

    return unique_strategies, strategies_occurance


# Ska spela spelet här, alla i unique_strategies ska möta varande x antal gånger, får kolla upp hur många gånger det är i PDFen
# Hittade inte hur många gånger alla strategier ska möta varandra. Sätter det till 100 gånger för tillfället

def game(strategies, rounds):

    unique_strategies, strategies_occurance = get_strategies(strategies)
    strategy_points = np.zeros(len(unique_strategies))
    print("unique_strategies: ", unique_strategies)
    print("strategy_points: ", strategy_points)

    for i in range(len(unique_strategies)):
        for j in range(i,len(unique_strategies)):

            strategy1 = unique_strategies[i]
            strategy2 = unique_strategies[j]
            strategy1_history = []
            strategy2_history = []
            history_length1 = int(math.log(len(strategy1), 2))
            history_length2 = int(math.log(len(strategy2), 2))
            print("\n")
            print("strategy 1: ", strategy1, "           strategy 2: ", strategy2)
            print("history_length1: ", history_length1, "           history_length2: ", history_length2)

            for k in range(rounds): # Spelar strategi1 mot strategi2 rounds antal gånger
                player1_choice, player2_choice = play_game(strategy1, strategy2, strategy1_history, strategy2_history, history_length1, history_length2)
                strategy1_history.append(player1_choice)
                strategy2_history.append(player2_choice)

            # Lägg till något sätt att räkna ut poängen här, kan jämföra strategy1_history med strategy2_history.
            print("Choices for strategy ", i+1, " versus strategy ", j+1)
            print("strategy1_history: ", strategy1_history)
            print("strategy2_history: ", strategy2_history)


def play_game(strategy1, strategy2, strategy1_history, strategy2_history, history_length1, history_length2):

    if len(strategy2_history) < history_length1: # Om vi ej har fått tillräckligt många val av spelare två väljer vi att Cooperate
        return 1, 1                              # Detta stämmer inte. Måste också kolla hur lång "history_length" strategi 2 har, då
                                                 # den kanske kan börja spela på sin strategi innan spelare ett gör det !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                                                 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    else:
        history2 = strategy2_history[-history_length1:] # Tar ut historiken för strategi 2 beroende på hur lång history vi ska kolla på
        history1 = strategy1_history[-history_length2:] # Samma som ovan fast för strategi 1. Det är "history_length2" inom [] eftersom
                                                        # beroende på hur lång historik strategi 2 kollar på måste vi plocka ut den
                                                        # historiken från spelare1 historik

        index1 = lookup_table[history_length1-1].index(history2) # Tar ut vilket index som den historiken representerar för att sedan kunna
                                                                 # välja vilket val som ska göras m.a.p. den historiken
        index2 = lookup_table[history_length2-1].index(history1)

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
        print(i)
    return strategy1_points, strategy2_points


strats = [[1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0], [1, 1]]
game(strats, 10)


"""
alwaysC = [1, 1]
tft = [0, 1]
reverseTft = [1, 0]
alwaysD = [0, 0]

payoffMatrix = [[1, 1], [0, 2], [2, 0], [0, 0]]
"""