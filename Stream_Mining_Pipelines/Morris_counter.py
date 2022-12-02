import random

class counter():
    def __init__(self):
        self.c = 0
    def update(self):
        p = 2**(0-self.c)
        if random.random() <= p: 
            self.c += 1
    def query(self):
        return 2**self.c - 1 