from __future__ import annotations
from abc import ABC, abstractmethod
import datetime
import calendar
from re import S
import core.classes.doc as doc


class PaymentClassificationABC(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def calculate_pay(self, paycheck: doc.Paycheck) -> float:
        pass

class SalariedClassification(PaymentClassificationABC):
    def __init__(self, salary) -> SalariedClassification:
        if type(salary) is float:
            self.__salary = salary
        else:
            raise TypeError('Invalid type of argument \"salary\".')
        super().__init__()
    
    @property
    def salary(self) -> float:
        return self.__salary
    
    def calculate_pay(self, paycheck: doc.Paycheck) -> float:
        return self.__salary

class HourlyClassification(PaymentClassificationABC):
    def __init__(self, hourly_rate: float) -> HourlyClassification:
        self.__hourly_rate = hourly_rate
        self.__time_cards = {}
        super().__init__()

    @property
    def hourly_rate(self):
        return self.__hourly_rate

    def add_time_card(self, time_card: doc.TimeCard) -> None:
        if time_card.date in self.__time_cards:
            raise Exception('Time card for this date alredy excits')
        self.__time_cards[time_card.date] = time_card

    def get_time_card(self, date: datetime.date) -> doc.TimeCard:
        return self.__time_cards.get(date, None)
    
    def calculate_pay(self, paycheck: doc.Paycheck) -> float:
        total_pay = 0.0
        card_date = paycheck.pay_period.start_date
        while card_date <= paycheck.pay_period.end_date:
            time_card = self.__time_cards.get(card_date, None)
            if time_card is not None:
                total_pay += self.__calculate_pay_for_time_card(time_card)   
            card_date += datetime.timedelta(days=1)   
        return total_pay

    def __calculate_pay_for_time_card(self, time_card):
        overtime_hours = max(0.0, time_card.hours - 8.0)
        normal_hours = time_card.hours - overtime_hours
        return self.__hourly_rate * normal_hours + self.__hourly_rate * 1.5 * overtime_hours

class CommissionedClassification(PaymentClassificationABC):
    def __init__(self, commission_rate: float, salary: float) -> CommissionedClassification:
        self.__commission_rate = commission_rate
        self.__salary = salary
        self.__sales_receipts = {}
        super().__init__()
    
    @property
    def commission_rate(self):
        return self.__commission_rate
    
    @property
    def salary(self):
        return self.__salary

    def add_sales_receipt(self, sales_receipt: doc.SalesReceipt) -> None:
        if sales_receipt.date in self.__sales_receipts:
            raise Exception('Sales receipt for this date alredy excits')
        self.__sales_receipts[sales_receipt.date] = sales_receipt

    def get_sales_receipt(self, date: datetime.date) -> doc.SalesReceipt:
        return self.__sales_receipts.get(date, None)

    def calculate_pay(self, paycheck: doc.Paycheck) -> float:
        total_pay = self.__salary
        sales_receipt_date = paycheck.pay_period.start_date
        while sales_receipt_date <= paycheck.pay_period.end_date:
            sales_receipt = self.get_sales_receipt(sales_receipt_date)
            if sales_receipt is not None:
                total_pay += sales_receipt.amount * self.__commission_rate
            sales_receipt_date += datetime.timedelta(days=1)
        return total_pay