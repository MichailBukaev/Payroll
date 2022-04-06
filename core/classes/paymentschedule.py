from __future__ import annotations
from abc import ABC, abstractmethod
from calendar import month
from datetime import date, timedelta
import math



class PaymentScheduleABC(ABC):
    @abstractmethod
    def is_pay_date(self, pay_data: date) -> bool:
        pass

    def get_pay_period_start_date(self, pay_data: date) -> date:
        pass

class MonthlySchedule(PaymentScheduleABC):
    def is_pay_date(self, pay_data: date) -> bool:
        return self.__is_last_day_of_month(pay_data)
    
    def get_pay_period_start_date(self, pay_data: date) -> date:
        next_day = pay_data + timedelta(days=1)
        last_day_of_prev_month = (pay_data.replace(day=1) - timedelta(days=1)).day
        if last_day_of_prev_month < next_day.day:
            return date(pay_data.year, pay_data.month, 1)
        if next_day.month == 1:
            return date(next_day.year - 1, 12, next_day.day)
        else:
            return date(pay_data.year, next_day.month - 1, next_day.day)

    def __is_last_day_of_month(self, pay_data: date):
        return pay_data.month != (pay_data + timedelta(days=1)).month
        

class WeeklySchedule(PaymentScheduleABC):
    def is_pay_date(self, pay_data: date) -> bool:
        return pay_data.weekday() == 4 #Friday
    
    def get_pay_period_start_date(self, pay_data: date) -> date:
        return pay_data - timedelta(weeks=1)

class BeweeklySchedule(PaymentScheduleABC):
    def is_pay_date(self, pay_data: date) -> bool:
        pass

    def get_pay_period_start_date(self, pay_data: date) -> date:
        return pay_data - timedelta(weeks=2)