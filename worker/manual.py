#!/usr/bin/env python3
from refactor import *


if __name__ == '__main__':
    exm = ExploitManager()
    exm.start_round(only_me=[('prob1', 'ex1')])
