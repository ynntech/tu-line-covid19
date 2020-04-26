#-*- coding: utf-8 -*-
from utils import Superviser
from sites import BcpEn, GLC, EngEn
from database import DataBase


if __name__ == "__main__":
    db = DataBase()
    db.start()

    _bcp = BcpEn()
    _glc = GLC()
    _eng = EngEn()
    targets = [_bcp, _glc, _eng]

    supervise = Superviser(targets=targets, timers=[], posting=[])
    supervise.reload()
