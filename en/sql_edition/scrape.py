#-*- coding: utf-8 -*-
from utils import Superviser
from sites import BcpEn, EngEn


if __name__ == "__main__":
    _bcp = BcpEn()
    _eng = EngEn()
    targets = [_bcp, _eng]
    timers = ["09:30", "14:30", "19:30"]
    posting = ["10:00", "15:00", "20:00"]

    supervise = Superviser(targets=targets, timers=timers, posting=posting)
    supervise.run()
