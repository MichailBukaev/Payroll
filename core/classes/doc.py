from __future__ import annotations
from abc import ABC, abstractmethod
import datetime as dt
from tkinter.messagebox import NO
from tracemalloc import start

class DocABC(ABC):
    @abstractmethod
    def __init__(self, date: dt.date):
        if isinstance(date, dt.date):
            self.__date = date
        else:
            raise TypeError('Invalid type of argument \"date\".')
        super().__init__()
    
    @property
    def date(self):
        return self.__date

class TimeCard(DocABC):
    def __init__(self, date: dt.date, hours: float) -> TimeCard:
        self.__hours = hours
        super().__init__(date)

    @property
    def hours(self):
        return self.__hours

class SalesReceipt(DocABC):
    def __init__(self, date: dt.date, amount: float) -> SalesReceipt:
        self.__amount = amount
        super().__init__(date)

    @property
    def amount(self):
        return self.__amount

class ServiceCharge(DocABC):
    def __init__(self, date: dt.date, amount: float) -> ServiceCharge:
        self.__amount = amount
        super().__init__(date)

    @property
    def amount(self):
        return self.__amount

class Paycheck(DocABC):
    class Period():
        def __init__(self, start_date, end_date) -> None:
            self.__start_date = start_date
            self.__end_date = end_date
        
        @property 
        def start_date(self) -> dt.date:
            return self.__start_date

        @property
        def end_date(self) -> dt.date:
            return self.__end_date

    def __init__(self, date: dt.date, pay_period_start_date: dt.date):
        self.__pay_date = date
        self.__gross_pay = None
        self.__deductions = None
        self.__net_pay = None
        self.__pay_period = Paycheck.Period(pay_period_start_date, date)
        super().__init__(date)

    @property
    def pay_date(self):
        return self.__pay_date

    @property
    def gross_pay(self):
        return self.__gross_pay
    
    @gross_pay.setter
    def gross_pay(self, gross_pay):
        self.__gross_pay = gross_pay

    @property
    def deductions(self):
        return self.__deductions

    @deductions.setter
    def deductions(self, deductions):
        self.__deductions = deductions
    
    @property
    def net_pay(self):
        return self.__net_pay

    @net_pay.setter
    def net_pay(self, net_pay):
        self.__net_pay = net_pay

    @property
    def pay_period(self) -> Paycheck.Period:
        return self.__pay_period