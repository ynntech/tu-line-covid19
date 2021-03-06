#-*- coding: utf-8 -*-
from utils import Superviser
from sites import BcpEn, GLC, EngEn


if __name__ == "__main__":
    _bcp = BcpEn()
    _glc = GLC()
    _eng = EngEn()
    targets = [_bcp, _glc, _eng]
    timers = ["19:30"]
    posting = ["20:00"]

    supervise = Superviser(targets=targets, timers=timers, posting=posting)
    supervise.run()
