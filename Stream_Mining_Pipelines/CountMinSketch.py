from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
import math
import random



class CountMinSketch:
    def __init__(self, d, w, universe=['0','1']):

        self.d = d 
        self.w = w
        self.universe = universe

        self.p = 1223543677 # a (relatively) large prime
        self.epsilon = math.e/self.w
        self.delta = 1/math.exp(self.d)

        self.a = [random.randrange(self.p) for i in range(d)]
        self.b = [random.randrange(self.p) for i in range(d)]

        self.array_init()

    def array_init(self):

        self.array = [[0 for x in range(self.w)] for y in range(self.d)] 

    def hash(self, x, a, b):

        return ((a*hash(x)+b)%self.p)%self.w

    def in_universe(self, x):
 
        if x in self.universe:
            return True
        else:
            print(f"ERROR: {x} is not in the universe")
            return False
    def get_hashes(self, x):

        hashes = []
        for a, b in zip(self.a, self.b):
            hashes.append(self.hash(x, a, b))
        return hashes

    def __str__(self):
        header = [[f'h{d}']+self.array[d] for d in range(self.d)]
        return tabulate(header,tablefmt='grid')

    def update(self, x, show=False):

        if self.in_universe(x):
            hashes = self.get_hashes(x)
            for i, h in enumerate(hashes):
                self.array[i][h] += 1

            if show:
                print(self)

    def query(self, x):

        if self.in_universe(x):
            hashes = self.get_hashes(x)
            counts = [self.array[i][h] for i, h in enumerate(hashes)]
            return min(counts)
    