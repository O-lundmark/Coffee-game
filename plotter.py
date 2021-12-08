import matplotlib.pyplot as plt
import numpy as np
class Plotter:
    def __init__(self):
        self.un = []
        self.unfracs = []

    def update(self, unique, fraction):
        for strat in unique:
            if strat not in self.un:
                self.un.append(strat)
                if self.unfracs:
                    self.unfracs.append([0 for _ in range(len(self.unfracs[0]))])
                else:
                    self.unfracs.append([])


        for i, strat in enumerate(self.un):
            if strat in unique:
                self.unfracs[i].append(fraction[unique.index(strat)])
            else:
                self.unfracs[i].append(0)
            x=list(range(1, len(self.unfracs[i]) + 1))
            x = [h*100 for h in x]
            plt.plot(x , self.unfracs[i], label=strat)
        plt.xlabel("Generation")
        plt.ylabel("Fraction")
        plt.legend(bbox_to_anchor=(1, 1),
                         loc='upper left', borderaxespad=0)
        plt.draw()
        plt.pause(0.1)
        plt.clf()




