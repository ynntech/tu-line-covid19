#-*- coding: utf-8 -*-
from utils import Superviser
from sites import (TU, Sal, Sed, Law, Econ, Sci, Med, Dent, Pharm,
                   Eng, Agri, Intcul, IS, Lifesci, Kankyo, Bme)


if __name__ == "__main__":
    _tu = TU()
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
    targets = [_tu, _sal, _sed, _law, _econ, _sci, _med, _dent, _pharm,
               _eng, _agri, _intcul, _is, _lifesci, _kankyo, _bme]
    timers = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
              "16:00", "17:00", "18:00", "19:00", "20:00","21:00"]

    supervise = Superviser(targets=targets, timers=timers)
    supervise.run()
