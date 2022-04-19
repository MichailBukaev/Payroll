from __future__ import annotations
from datetime import date, timedelta
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
        total_dues = self.__calcualte_dues(paycheck)
        total_service_charge = self.__calcualte_service_charge(paycheck)
        return total_dues + total_service_charge

    def __calcualte_dues(self, paycheck):
        fridays_count = self.__number_of_fridays_in_pay_period(paycheck.pay_period.start_date, paycheck.pay_period.end_date)
        return self.__dues * fridays_count
    
    def __number_of_fridays_in_pay_period(self, start_date, end_date):
        fridays_count = 0
        day = start_date
        while day <= end_date:
            if day.weekday() == 4: #Friday
                fridays_count += 1
            day += timedelta(days=1)
        return fridays_count

    def __calcualte_service_charge(self, paycheck):
        total_service_charge = 0.0
        service_charge_date = paycheck.pay_period.start_date
        while service_charge_date <= paycheck.pay_period.end_date:
            service_charge = self.get_service_charge(service_charge_date)
            if service_charge is not None:
                total_service_charge += service_charge.amount
            service_charge_date += timedelta(days=1)
        return total_service_charge