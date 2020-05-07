#-*- coding: utf-8 -*-
from utils import Superviser
from sites import (BCP, Sal, Sed, Econ, Sci, Med, Dent, Pharm,
                   Eng, Agri, Intcul, IS, Lifesci, Kankyo, Bme)


if __name__ == "__main__":
    _bcp = BCP()
    _sal = Sal()
    _sed = Sed()
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
    targets = [_bcp, _sal, _sed, _econ, _sci, _med, _dent, _pharm,
               _eng, _agri, _intcul, _is, _lifesci, _kankyo, _bme]
    timers = ["19:30"]
    posting = ["20:00"]

    supervise = Superviser(targets=targets, timers=timers, posting=posting)
    supervise.run()
