import matplotlib.pyplot as plt
import numpy as np
class Plotter:
    def __init__(self):
        self.un = []
        self.unfracs = []
        self.av = []


    def update(self, unique, fraction, average, fig, ax):
        self.av.append(average)
        for strat in unique:
            if strat not in self.un:
                self.un.append(strat)
                if self.unfracs:
                    self.unfracs.append([0 for _ in range(len(self.unfracs[0]))])
                else:
                    self.unfracs.append([])


        ax[0].clear()
        ax[1].clear()

        for i, strat in enumerate(self.un):
            if strat in unique:
                self.unfracs[i].append(fraction[unique.index(strat)])
            else:
                self.unfracs[i].append(0)
            x=list(range(1, len(self.unfracs[i]) + 1))
            x = [h*100 for h in x]
            ax[1].plot(x , self.unfracs[i], label=strat)
        ax[1].set_xlabel("Generation")
        ax[1].set_ylabel("Fraction")
        ax[1].legend(bbox_to_anchor=(1, 1),
                         loc='upper left', borderaxespad=0)
        ax[0].plot(x, self.av)
        ax[0].set_xlabel("Generation")
        ax[0].set_ylabel("Average Score")
        plt.draw()
        plt.pause(0.1)




