import random


def split_genome(genome):
    if len(genome) == 2:  # Kan inte dela på den om den bara har längd 2
        return genome

    rand = random.uniform(0, 1)
    first_half = genome[:len(genome) // 2]
    second_half = genome[len(genome) // 2:]
    # print("first_half: ", first_half)
    # print("second_half: ", second_half)
    if rand < 0.5:
        return first_half

    else:
        return second_half


def duplicate_genome(genome, max_memory):
    if len(genome) >= 2 ** max_memory:
        return genome

    else:
        return genome + genome


def point_mutation(genome, pp):
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