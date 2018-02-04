import bah_simulator as bah
import sys
import os
import psutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_all_data_from_file

import concurrent.futures
import time

current_millis = lambda: int(round(time.time() * 1000))

print('starting to load data')
start_date = '1993-01-01'
end_date = '2017-12-31'
df_adj_close = load_all_data_from_file('etf_data_adj_close.csv', start_date, end_date)

inception = pd.read_csv('../etf_data/etf_inc_date.csv', sep=';')

with open('../etf_data/etfs.txt', 'r') as fd:
    etf_list = list(fd.read().splitlines())

etf_list = list(set(etf_list))

print('data loaded')


def rolling_mean(data, period):
    rm = pd.rolling_mean(data, period)
    rm = rm[~np.isnan(rm)]
    return rm


def mean(value):
    value = np.mean(value)
    if np.isnan(value):
        return 0.
    return value


def compute_one_etf(etf):

    inception_date = inception[inception.ticket == etf[0]].inc_date.values[0]
    data = df_adj_close[df_adj_close.Date > inception_date][etf]
    dca = bah.DCA(30, 300.)
    investor = bah.Investor(etf, np.full(len(etf), 1.0 / len(etf)), dca)
    sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
    sim.invest(data)
    investor.compute_means()
    investor.compute_rank()


    return data, investor


def print_results(investor):
    _, ax = plt.subplots(3, 1)
    for rms in investor.rms_list:
        ax[2].plot(rms)
    print('invested:' + str(investor.invested_history[-1]))
    print('value gained:' + str(investor.history[-1]))
    print('ror:' + str(investor.ror_history[-1]))
    print('mean:' + str(investor.m))
    print('std:' + str(investor.std))
    for rms in investor.means:
        print(str(rms))
    # ax[0].plot(np.log(df_adj_close))
    ax[0].plot(np.log(investor.invested_history))
    ax[0].plot(np.log(investor.history))
    ax[1].plot(investor.ror_history)
    ax[0].legend(['invested', 'value'])
    ax[1].legend(['RoR'])
    plt.show()


class QuantumParticle:
    def __init__(self, max, etfs, m=1):
        self.etfs = etfs
        self.M = m
        self.w = np.random.uniform(0., max, m)
        self.p_w = np.array(self.w)
        self.g_w = np.array(self.w)
        self.c = np.array(self.w)
        self.alpha = 0.75
        self.last_fitness = None
        self.fitness = None

    def compute_weights(self):
        phi = np.random.uniform(0., 1.)
        p = np.add(np.multiply(phi, self.p_w), np.multiply(np.subtract(1., phi), self.g_w))
        u = np.random.uniform(0., 1.)
        for i in range(len(self.w)):
            if np.random.uniform(0., 1.) < 0.5:
                self.w[i] = p[i] + self.alpha * np.abs(self.w[i] - self.c[i]) * np.log(1. / u)
            else:
                self.w[i] = p[i] - self.alpha * np.abs(self.w[i] - self.c[i]) * np.log(1. / u)

    def evaluate(self):
        index = int(np.round(self.w)[0])

        if index < 0:
            index = 0

        if index > len(self.etfs) - 1:
            index = len(self.etfs) - 1

        _, investor = compute_one_etf([self.etfs[index]])
        self.investor = investor

    def compute_fitness(self):
        self.evaluate()
        self.fitness = self.investor.rank

        if self.last_fitness is None or self.last_fitness < self.fitness:
            self.last_fitness = self.fitness
            self.p_w = self.w


class QPSOETFSearch:
    def __init__(self, population_size, iterations, etfs, m=1):
        self.M = m
        self.population_size = population_size
        self.iterations = iterations
        self.population = []
        for i in range(self.population_size):
            self.population.append(QuantumParticle(len(etfs), etfs, self.M))

    def run(self):

        for i in range(self.iterations):
            cur = current_millis()
            sum_of_weights = np.zeros(self.M)
            for p in self.population:
                sum_of_weights = np.add(sum_of_weights, p.p_w)
            c = np.divide(sum_of_weights, float(self.population_size))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                for p in self.population:
                    executor.submit(self.process_one, c, p)
                executor.shutdown(True)
            # for p in self.population:
            #     self.process_one(c, p)

            self.population.sort(key=lambda particle: particle.fitness, reverse=True)

            for p in self.population:
                p.g_w = self.population[0].w

            print('iteration(%d) = %f | %s | %f s' % (
            i, self.population[0].fitness, str(self.population[0].w), (current_millis() - cur) / 1000))

        return self.population[0]

    def process_one(self, c, p):
        p.c = c
        p.compute_weights()
        p.compute_fitness()


cur = current_millis()

qpso = QPSOETFSearch(10, 50, etf_list)
best = qpso.run()
print(str(best.investor.rank) + ':' + str(best.investor.ticket) + ':' + str(best.investor.m) + ":" + str(
    best.investor.std))
print('time = ' + str((current_millis() - cur) / 1000) + ' seconds')
print_results(best.investor)
