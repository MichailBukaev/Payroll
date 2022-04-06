from __future__ import annotations
from abc import ABC, abstractmethod

from core.classes.doc import Paycheck


class PaymentMethodABC(ABC):
    @abstractmethod
    def pay(self, paycheck: Paycheck) -> None:
        pass

class HoldMethod(PaymentMethodABC):
    def pay(self, paycheck: Paycheck) -> None:
        paycheck.disposition = 'Hold'

class DirectMethod(PaymentMethodABC):
    def __init__(self, bank, account) -> DirectMethod:
        self.__bank = bank
        self.__account = account
        super().__init__()

    @property
    def account(self):
        return self.__account

    @property
    def bank(self):
        return self.__bank

    def pay(self, paycheck: Paycheck) -> None:
        pass

class MailMethod(PaymentMethodABC):
    def __init__(self, address) -> MailMethod:
        self.__address = address
        super().__init__()

    @property
    def address(self) -> str:
        return self.__address

    def pay(self, paycheck: Paycheck) -> None:
        pass