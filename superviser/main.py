#-*- coding: utf-8 -*-
from utils import Superviser
from sites import Bme, Kankyo


if __name__ == "__main__":
    bme = Bme()
    kankyo = Kankyo()
    targets = [bme, kankyo]
    timers = []

    supervise = Superviser(targets=targets, timers=timers)
    supervise.run()
