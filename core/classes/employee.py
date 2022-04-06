from __future__ import annotations
from datetime import date, timedelta
import re
from tkinter.messagebox import NO
from core.classes.affiliation import UnionAffiliation
from core.classes.doc import Paycheck
from core.classes.paymentclassification import PaymentClassificationABC
from core.classes.paymentschedule import PaymentScheduleABC
from core.classes.paymentmethod import PaymentMethodABC


class Employee():
    def __init__(self, emp_id, name, address) -> None:
        self.__emp_id = emp_id
        self.__name = name
        self.__address = address
        self.__affiliation = None
        self.__classification = None
        self.__method = None
        self.__schedule = None
    
    @property
    def emp_id(self):
        return self.__emp_id
    
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name    

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, address):
        self.__address = address

    @property
    def classification(self) -> PaymentClassificationABC:
        return self.__classification
    
    @classification.setter
    def classification(self, classification: PaymentClassificationABC):
        if isinstance(classification, PaymentClassificationABC):
             self.__classification = classification
        else:
            raise TypeError('Invalid type of argument \"classification\".')

    @property
    def schedule(self):
        return self.__schedule
    
    @schedule.setter
    def schedule(self, schedule):
        if isinstance(schedule, PaymentScheduleABC):
             self.__schedule = schedule
        else:
            raise TypeError('Invalid type of argument \"schedule\".')

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, method):
        if isinstance(method, PaymentMethodABC):
            self.__method = method
        else:
            raise TypeError('Invalid type of argument \"method\".')
    
    @property
    def affiliation(self):
        return self.__affiliation

    @affiliation.setter
    def affiliation(self, affiliation):
        if isinstance(affiliation, UnionAffiliation) or affiliation is None:
            self.__affiliation = affiliation
        else:
            raise TypeError('Invalid type of argument \"affiliation\".')

    def is_pay_date(self, pay_data: date) -> bool:
        return self.__schedule.is_pay_date(pay_data)
    
    def get_pay_period_start_date(self, pay_data: date) -> date:
        return self.__schedule.get_pay_period_start_date(pay_data)

    def payday(self, paycheck: Paycheck) -> None:
        gross_pay = self.__classification.calculate_pay(paycheck)
        deductions = (self.__affiliation.calcualte_deductions(paycheck) 
                     if self.__affiliation is not None else 
                     0.00)
        net_pay = gross_pay - deductions
        paycheck.gross_pay = gross_pay
        paycheck.deductions = deductions
        paycheck.net_pay = net_pay
        self.__method.pay(paycheck)