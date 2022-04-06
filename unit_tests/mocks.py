import array
from core.classes.employee import Employee
from core.databasesabc import PayrollDatabaseABC


class PayrollDatabaseMock(PayrollDatabaseABC):
    __employees = {}
    __union_members = {}

    def add_emplyee(self, id: int, employee: Employee) -> None:
        PayrollDatabaseMock.__employees[id] = employee
    
    def get_employee(self, id: int) -> Employee:
        return PayrollDatabaseMock.__employees.get(id, None)
    
    def delete_employee(self, id: int) -> None:
        if id in self.__employees:
            del self.__employees[id]

    def add_union_member(self, id: int, employee: Employee) -> None:
        PayrollDatabaseMock.__union_members[id] = employee

    def get_union_member(self, id: int) -> Employee:
        return PayrollDatabaseMock.__union_members.get(id, None)

    def delete_union_member(self, id: int) -> None:
        if id in self.__union_members:
            del self.__union_members[id]
    
    def get_all_employee_ids(self) -> array:
        return self.__employees.keys()
    
    def clear(self):
        self.__employees.clear()
        self.__union_members.clear()