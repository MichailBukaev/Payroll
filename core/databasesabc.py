from __future__ import annotations
from abc import ABC, abstractmethod
from array import array
from multiprocessing.dummy import Array
from core.classes.employee import Employee



class PayrollDatabaseABC(ABC):
    @abstractmethod
    def add_emplyee(self, id: int, employee: Employee) -> None:
        pass

    @abstractmethod
    def get_employee(self, id: int) -> Employee:
        pass

    @abstractmethod
    def delete_employee(self, id: int) -> None:
        pass

    @abstractmethod
    def add_union_member(self, id: int, employee: Employee) -> None:
        pass

    @abstractmethod
    def get_union_member(self, id: int) -> Employee:
        pass

    @abstractmethod
    def delete_union_member(self, id: int) -> None:
        pass

    @abstractmethod
    def get_all_employee_ids(self) -> array:
        pass