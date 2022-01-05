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
        plt.rcParams['font.family'] = "Times New Roman"
        plt.rcParams.update({'font.size': 15})
        csfont = {'fontname': 'Times New Roman'}

        for i, strat in enumerate(self.un):
            if strat in unique:
                self.unfracs[i].append(fraction[unique.index(strat)])
            else:
                self.unfracs[i].append(0)
            x=list(range(1, len(self.unfracs[i]) + 1))
            x = [h*100 for h in x]
            if self.unfracs[i][-1]==0:
                ax[1].plot(x, self.unfracs[i], label='_nolegend_', linewidth=2.5)
            else:
                ax[1].plot(x, self.unfracs[i], label=strat, linewidth=2.5)
        ax[1].set_xlabel("Generation", fontsize=14, font="Times New Roman")
        ax[1].set_ylabel("Fraction", fontsize=14, font="Times New Roman")
        ax[1].legend(#bbox_to_anchor=(0, 1),
                         loc='best', borderaxespad=0)
        ax[1].set_ylim([-0.01, 1.01])


        ax[0].plot(x, self.av, linewidth=2.5)
        ax[0].set_xlabel("Generation", fontsize=14, font="Times New Roman")
        ax[0].set_ylabel("Average Score", fontsize=14, font="Times New Roman")
        plt.draw()
        plt.pause(0.001)




