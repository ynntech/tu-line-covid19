#-*- coding: utf-8 -*-
from utils import Superviser
from sites import (TU, BCP, Sal, Sed, Law, Econ, Sci, Med, Dent, Pharm,
                   Eng, Agri, Intcul, IS, Lifesci, Kankyo, Bme)
from database import DataBase


if __name__ == "__main__":
    db = DataBase()
    db.start()

    _tu = TU()
    _bcp = BCP()
    _sal = Sal()
    _sed = Sed()
    _law = Law()
    _econ = Econ()
    _sci = Sci()
    _med = Med()
    _dent = Dent()
    _pharm = Pharm()
    _eng = Eng()
    _agri = Agri()
    _intcul = Intcul()
    _is = IS()
    _lifesci = Lifesci()
    _kankyo = Kankyo()
    _bme = Bme()
    targets = [_tu, _bcp, _sal, _sed, _law, _econ, _sci, _med, _dent,
               _pharm, _eng, _agri, _intcul, _is, _lifesci, _kankyo, _bme]

    supervise = Superviser(targets=targets, timers=[], posting=[])
    supervise.reload()
