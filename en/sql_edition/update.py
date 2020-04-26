#-*- coding: utf-8 -*-
from utils import Superviser
from sites import BcpEn, EngEn


if __name__ == "__main__":
    _bcp = BcpEn()
    _eng = EngEn()
    targets = [_bcp, _eng]

    supervise = Superviser(targets=targets, timers=[], posting=[])
    supervise.update()
