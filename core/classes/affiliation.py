from __future__ import annotations
from datetime import date
import core.classes.doc as doc


class UnionAffiliation():
    def __init__(self, member_id: int, dues: float) -> None:
        self.__member_id = member_id
        self.__dues = dues
        self.__service_charges = {}

    @property
    def member_id(self):
        return self.__member_id

    @property
    def dues(self):
        return self.__dues    

    def get_service_charge(self, date: date) -> doc.ServiceCharge:
        return self.__service_charges.get(date, None)

    def add_service_charge(self, service_charge: doc.ServiceCharge) -> None:
        if service_charge.date in self.__service_charges:
            raise Exception('Service charge for this date alredy excits')
        self.__service_charges[service_charge.date] = service_charge

    def calcualte_deductions(self, paycheck: doc.Paycheck) -> float:
        pass