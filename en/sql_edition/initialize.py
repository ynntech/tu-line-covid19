#-*- coding: utf-8 -*-
from utils import Superviser
from sites import BcpEn, EngEn
from database import DataBase


if __name__ == "__main__":
    db = DataBase()
    db.start()

    _bcp = BcpEn()
    _eng = EngEn()
    targets = [_bcp, _eng]

    supervise = Superviser(targets=targets, timers=[], posting=[])
    supervise.reload()
