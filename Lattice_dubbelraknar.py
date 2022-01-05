import matplotlib.pyplot as plt
import matplotlib.colors as mcolor
import numpy as np
import matplotlib.patches as mpatches
import random
from functions import duplicate_genome, split_genome, point_mutation
import copy
import collections
import seaborn as sns
import matplotlib.colors as colors1
import matplotlib.colors as cl


class Plotter:
    def __init__(self):
        self.un = []
        self.unfracs = []
        cmaps = plt.get_cmap('tab20c')
        cmaps2 = plt.get_cmap('tab20b')
        cmaps3 = plt.get_cmap('Paired')
        cmaps4 = plt.get_cmap('Set1')
        self.num_colors = 20
        self.colors = [cmaps(i / self.num_colors) for i in range(0, self.num_colors)] + \
                      [cmaps2(i / self.num_colors) for i in range(0, self.num_colors)] + \
                        [cmaps3(i / 12) for i in range(0, 12)] + [cmaps4(i / 50) for i in range(0, 50)]

    def update(self, unique, fraction, fig, ax, plot_every, dict):
        for strat in unique:
            if strat not in self.un:
                self.un.append(strat)
                if self.unfracs:
                    self.unfracs.append([0 for _ in range(len(self.unfracs[0]))])
                else:
                    self.unfracs.append([])
        ax[1].clear()
        for i, strat in enumerate(self.un):
            if strat in unique:
                self.unfracs[i].append(fraction[unique.index(strat)])
            else:
                self.unfracs[i].append(0)
            values_list = list(dict.values())
            key_list = list(dict.keys())
            pos = values_list.index(strat)
            color_value = int(key_list[pos])
            x = list(range(1, len(self.unfracs[i]) + 1))
            x = [h * plot_every for h in x]
            if self.unfracs[i][-1]==0:
                ax[1].plot(x, self.unfracs[i], label='_nolegend_', c=self.colors[color_value], linewidth=2.5)
            else:
                ax[1].plot(x, self.unfracs[i], label=strat, c=self.colors[color_value], linewidth=2.5)
        ax[1].set_xlabel("Generation", fontsize=14, font="Times New Roman")
        ax[1].set_ylabel("Fraction", fontsize=14, font="Times New Roman")

        ax[1].set_ylim([-0.01, 1.01])
        #ax[1].legend(bbox_to_anchor=(1, 1),
        #             loc='best', borderaxespad=0)
        plt.draw()
        plt.pause(0.000001)


def mutations(better_strategy, mut_parameters):
    rand_mutation = random.uniform(0, 1)
    if rand_mutation <= mut_parameters['pd']:
        mut_strategy = duplicate_genome(better_strategy, mut_parameters['max_memory'])
        return mut_strategy

    if rand_mutation >= (1 - mut_parameters['ps']):
        mut_strategy = split_genome(better_strategy)
        return mut_strategy

    genome = copy.copy(better_strategy)
    mut_strategy = point_mutation(genome, mut_parameters['pp'])
    return mut_strategy


class Lattice:
    def __init__(self, lattice_size):
        self.lattice_size = lattice_size
        self.lattice_matrix = None
        self.dict_unique_strategies_values = {}
        self.max_value = 0
        self.all_coord = [(x, y) for x in range(lattice_size) for y in range(lattice_size)]
        self.updated_lattice = None
        cmaps = plt.get_cmap('tab20c')
        cmaps2 = plt.get_cmap('tab20b')
        cmaps3 = plt.get_cmap('Paired')
        cmaps4 = plt.get_cmap('Set1')
        self.num_colors = 20
        self.colors = [cmaps(i / self.num_colors) for i in range(0, self.num_colors)] + \
                      [cmaps2(i / self.num_colors) for i in range(0, self.num_colors)] + \
                        [cmaps3(i / 12) for i in range(0, 12)] + [cmaps4(i / 50) for i in range(0, 50)]
        self.cmap = cl.LinearSegmentedColormap.from_list('', self.colors, self.num_colors*2+12+50)

    # initierar random, kanske vill göra någon annan som initerar på annat sätt?
    def init_lattice_random(self, unique_init_strategies, init_strategy_frac):
        self.lattice_matrix = np.random.choice(len(unique_init_strategies), (self.lattice_size, self.lattice_size),
                                               p=init_strategy_frac)
        self.updated_lattice = self.lattice_matrix
        for i in range(len(unique_init_strategies)):
            self.dict_unique_strategies_values[f"{i}"] = unique_init_strategies[i]
        self.max_value = len(unique_init_strategies) - 1

    def plot_lattice(self, fig, ax, title_text='lattice'):
        """ func som plottar upp spel-matrisen """

        ax[0].clear()

        frac, strat = self.get_strategy_fractions()
        unique = np.unique(self.lattice_matrix)
        print(self.max_value)
        sns.heatmap(self.lattice_matrix, ax=ax[0], cmap=self.cmap, vmin=0, vmax=self.num_colors*2+12+50, square=True,
                    cbar=False, yticklabels=False, xticklabels=False)

        patches = [mpatches.Patch(color=self.colors[i], label=f"{self.dict_unique_strategies_values.get(str(i))}") for i
                   in
                   unique]
        legends = ax[1].legend(handles=patches, loc=2, borderaxespad=0., bbox_to_anchor=(1.05, 1))
        fig.tight_layout()
        #plt.subplots_adjust(right=0.65)
        ax[0].set_title(title_text)
        plt.draw()
        plt.pause(0.00001)
        return legends

    # BYT TILL ROLL OM VI ORKAR, säkert snabbare. kopierade bara denna från annan kurs vi haft
    def neumann_neighbours(self, position):  # with periodic boundary conditiions
        x_position = position[0]
        y_position = position[1]
        possible_neighbours = [(x_position - 1, y_position), (x_position + 1, y_position), (x_position, y_position + 1),
                               (x_position, y_position - 1)]

        for i, pos in enumerate(possible_neighbours):
            if -1 in pos:
                if pos[0] == -1:
                    possible_neighbours[i] = (self.lattice_size - 1, pos[1])
                if pos[1] == -1:
                    possible_neighbours[i] = (pos[0], self.lattice_size - 1)
            if self.lattice_size in pos:
                if pos[0] == self.lattice_size:
                    possible_neighbours[i] = (0, pos[1])
                if pos[1] == self.lattice_size:
                    possible_neighbours[i] = (pos[0], 0)
        return possible_neighbours

    # uppdaterar en ny lattice med förändringarna i strategi. Muterar när den bästa strat byter till mitten-positionen.
    def update_lattice(self, strategy_loop_points, coord, coord_neighbours, mut_parameters):
        # strat-loop-points innehåller spel-poängen när mittenspelare kört mot sina 4 grananr.
        # rad 0 är mittenspellaren och rad 1 är grannarna.
        diff = strategy_loop_points[0, :] - strategy_loop_points[1, :]
        if any(diff < 0):
            # TIES ARE BROKEN BY ADDING SMALL NOISE TO EACH VALUE.
            noise = np.random.normal(0, 0.2, len(diff))
            switch_to_index = np.argmin(diff + noise)

            better_strategy_coord = coord_neighbours[switch_to_index]
            better_strategy_value = self.lattice_matrix[better_strategy_coord[0], better_strategy_coord[1]]
            better_strategy = self.dict_unique_strategies_values.get(str(better_strategy_value))

            possible_mutated_better_strategy = mutations(better_strategy, mut_parameters)
            # om det muterats till någon ny finns strat finns den inte med i vår dict --> måste ge den nytt värde och
            # stoppa in i dict
            if possible_mutated_better_strategy not in self.dict_unique_strategies_values.values():
                self.max_value += 1
                self.dict_unique_strategies_values[f'{self.max_value}'] = possible_mutated_better_strategy

            # om vår strategi har muterats så kommer ju också värdet som ska stoppas in i spel-matrisen ändras.
            # hittar den såhär xD
            if possible_mutated_better_strategy != better_strategy:
                values_list = list(self.dict_unique_strategies_values.values())
                key_list = list(self.dict_unique_strategies_values.keys())
                pos = values_list.index(possible_mutated_better_strategy)
                better_strategy_value = int(key_list[pos])

            # notera att vanliga spelmatrisen inte uppdateras nu, utan den uppdateras när alla mött alla
            self.updated_lattice[coord[0], coord[1]] = better_strategy_value

    def get_strategy_fractions(self):
        population = self.lattice_size ** 2

        info_matrix = collections.Counter(self.lattice_matrix.ravel())
        fractions = [int(i) / population for i in info_matrix.values()]
        strategies = [self.dict_unique_strategies_values[f"{i}"] for i in info_matrix.keys()]
        return fractions, strategies
