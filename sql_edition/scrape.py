#-*- coding: utf-8 -*-
from utils import Superviser
from sites import (BCP, Sal, Sed, Law, Econ, Sci, Med, Dent, Pharm,
                   Eng, Agri, Intcul, IS, Lifesci, Kankyo, Bme)


if __name__ == "__main__":
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
    targets = [_bcp, _sal, _sed, _law, _econ, _sci, _med, _dent, _pharm,
               _eng, _agri, _intcul, _is, _lifesci, _kankyo, _bme]
    timers = ["09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30",
              "16:30", "17:30", "18:30", "19:30", "20:30","21:30"]
    posting = ["10:00", "15:00", "20:00"]

    supervise = Superviser(targets=targets, timers=timers, posting=posting)
    supervise.run()
