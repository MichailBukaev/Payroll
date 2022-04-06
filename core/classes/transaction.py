from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from core.classes.employee import Employee
from core.classes.paymentclassification import *
from core.classes.paymentmethod import *
from core.classes.paymentschedule import *
from core.classes.doc import *
from core.classes.affiliation import *
from core.databasesabc import PayrollDatabaseABC



class TransactionABC(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

class DatabaseBoundTransactionABC(TransactionABC, ABC):
    @abstractmethod
    def __init__(self, database) -> None:
        if isinstance(database, PayrollDatabaseABC):
            self.__database = database
        else:
            raise TypeError('Invalid type of argument \"database\".')
        super().__init__()
    
    @property
    def _database(self):
        return self.__database


class AddEmployeeTransactionABC(DatabaseBoundTransactionABC, ABC):
    def __init__(self, emp_id: int, name: str, address: str, database: PayrollDatabaseABC) -> None:
        self.__emp_id = emp_id
        self.__name = name
        self.__address = address 
        super().__init__(database)
    
    @abstractmethod
    def _make_clasification(self):
        pass

    @abstractmethod
    def _make_schedule(self):
        pass

    def execute(self) -> None:
        payment_clasification = self._make_clasification()
        payment_schedule = self._make_schedule()
        payment_method = HoldMethod()
        employee = Employee(self.__emp_id, self.__name, self.__address)
        employee.classification = payment_clasification
        employee.schedule = payment_schedule
        employee.method = payment_method
        self._database.add_emplyee(self.__emp_id, employee)

class AddSalariedEmployeeTransaction(AddEmployeeTransactionABC):
    def __init__(self, emp_id: int, name: str, address: str, database: PayrollDatabaseABC, salary: float) -> AddSalariedEmployeeTransaction:
        self.__salary = salary
        super().__init__(emp_id, name, address, database)

    def _make_clasification(self):
        return SalariedClassification(self.__salary)

    def _make_schedule(self):
        return MonthlySchedule()

class AddHourlyEmployeeTransaction(AddEmployeeTransactionABC):
    def __init__(self, emp_id: int, name: str, address: str, database: PayrollDatabaseABC, hourly_rate: float) -> AddHourlyEmployeeTransaction:
        self.__hourly_rate = hourly_rate
        super().__init__(emp_id, name, address, database)
    
    def _make_clasification(self):
        return HourlyClassification(self.__hourly_rate)
    
    def _make_schedule(self):
        return WeeklySchedule()

class AddCommissionedEmployeeTransaction(AddEmployeeTransactionABC):
    def __init__(self, emp_id: int, name: str, address: str, database: PayrollDatabaseABC, commission_rate: float, salary: float) -> AddCommissionedEmployeeTransaction:
        self.__commission_rate = commission_rate
        self.__salary = salary
        super().__init__(emp_id, name, address, database)

    def _make_clasification(self):
        return CommissionedClassification(self.__commission_rate, self.__salary)
    
    def _make_schedule(self):
        return BeweeklySchedule()

class AddTimeCardTransaction(DatabaseBoundTransactionABC):
    def __init__(self, date: date, hours: float, emp_id: int, database: PayrollDatabaseABC) -> AddTimeCardTransaction:
        self.__date = date
        self.__hours = hours
        self.__emp_id = emp_id
        super().__init__(database)

    def execute(self) -> None:
        employee = self._database.get_employee(self.__emp_id)
        if employee is not None:
            if isinstance(employee.classification, HourlyClassification):
                employee.classification.add_time_card(TimeCard(self.__date, self.__hours))
            else:
                raise Exception('Attempt to add time card for not hourly rated employee')
        else:
            raise Exception('Employee not found')

class AddSalesReceiptTransaction(DatabaseBoundTransactionABC):
    def __init__(self, database: PayrollDatabaseABC, date: date, amount: float, emp_id: int) -> AddSalesReceiptTransaction:
        self.__date = date
        self.__amount = amount
        self.__emp_id = emp_id
        super().__init__(database)
    
    def execute(self) -> None:
        employee = self._database.get_employee(self.__emp_id)
        if employee is not None:
            if isinstance(employee.classification, CommissionedClassification):
                employee.classification.add_sales_receipt(SalesReceipt(self.__date, self.__amount))
            else:
                raise Exception('Attempt to add sales receipt for not commissioned employee')
        else:
            raise Exception('Employee not found')

class AddServiceChargeTransaction(DatabaseBoundTransactionABC):
    def __init__(self, database: PayrollDatabaseABC, date: date, amount: float, union_member_id: int) -> AddServiceChargeTransaction:
        self.__date = date
        self.__amount = amount
        self.__union_member_id = union_member_id
        super().__init__(database)

    def execute(self) -> None:
        employee = self._database.get_union_member(self.__union_member_id)
        if employee is not None:
            if isinstance(employee.affiliation, UnionAffiliation):
                employee.affiliation.add_service_charge(ServiceCharge(self.__date, self.__amount))
            else:
                raise Exception('Attempt to add service receipt for a union member with an unregistered membership')
        else:
            raise Exception('Union member not found')


class DeleteEmployeeTransaction(DatabaseBoundTransactionABC):
    def __init__(self, emp_id: int, database: PayrollDatabaseABC) -> None:
        self.__emp_id = emp_id      
        super().__init__(database)

    def execute(self) -> None:
        self._database.delete_employee(self.__emp_id)


class ChangeEmployeeTransactionABC(DatabaseBoundTransactionABC, ABC):
    @abstractmethod
    def __init__(self, database, emp_id: int) -> None:
        self.__emp_id = emp_id
        super().__init__(database)

    def execute(self) -> None:
        employee = self._database.get_employee(self.__emp_id)
        if employee is not None:
            self._change(employee)
        else:
            raise Exception('Employee not found')

    @abstractmethod    
    def _change(self, employee: Employee) -> None:
        pass

class ChangeNameTransaction(ChangeEmployeeTransactionABC):
    def __init__(self, database, emp_id: int, new_name: str) -> ChangeNameTransaction:
        self.__new_name = new_name
        super().__init__(database, emp_id)
        
    def _change(self, employee: Employee) -> None:
        employee.name = self.__new_name

class ChangeAddressTransaction(ChangeEmployeeTransactionABC):
    def __init__(self, database, emp_id: int, new_address: str) -> None:
        self.__new_address = new_address
        super().__init__(database, emp_id)

    def _change(self, employee: Employee) -> None:
        employee.address = self.__new_address


class ChangeClassificationTransactionABC(ChangeEmployeeTransactionABC, ABC):
    @abstractmethod
    def __init__(self, database, emp_id: int) -> None:
        super().__init__(database, emp_id)

    def _change(self, employee: Employee) -> None:
        employee.classification = self._get_classification()
        employee.schedule = self._get_schedule()

    @abstractmethod 
    def _get_classification(self) -> PaymentClassificationABC:
        pass

    @abstractmethod
    def _get_schedule(self) -> PaymentScheduleABC:
        pass

class ChangeHourlyTransaction(ChangeClassificationTransactionABC):
    def __init__(self, database, emp_id: int, hourly_rate: float) -> ChangeHourlyTransaction:
        self.__hourly_rate = hourly_rate
        super().__init__(database, emp_id)
    
    def _get_classification(self) -> PaymentClassificationABC:
        return HourlyClassification(self.__hourly_rate)
    
    def _get_schedule(self) -> PaymentScheduleABC:
        return WeeklySchedule()

class ChangeSalariedTransaction(ChangeClassificationTransactionABC):
    def __init__(self, database, emp_id: int, salary: float) -> None:
        self.__salary = salary
        super().__init__(database, emp_id)
    
    def _get_classification(self) -> PaymentClassificationABC:
        return SalariedClassification(self.__salary)

    def _get_schedule(self) -> PaymentScheduleABC:
        return MonthlySchedule()

class ChangeCommissionedTransaction(ChangeClassificationTransactionABC):
    def __init__(self, database, emp_id: int, salary: float, commission_rate: float) -> None:
        self.__salary = salary
        self.__commission_rate = commission_rate
        super().__init__(database, emp_id)

    def _get_classification(self) -> PaymentClassificationABC:
        return CommissionedClassification(self.__commission_rate, self.__salary)

    def _get_schedule(self) -> PaymentScheduleABC:
        return BeweeklySchedule()

class ChageMethodTransactionABC(ChangeEmployeeTransactionABC, ABC):
    def __init__(self, database, emp_id: int) -> ChageMethodTransactionABC:
        super().__init__(database, emp_id)
    
    def _change(self, employee: Employee) -> None:
        employee.method = self._get_method()

    @abstractmethod
    def _get_method(self) -> PaymentMethodABC:
        pass 
        

class ChangeDirectTransaction(ChageMethodTransactionABC):
    def __init__(self, database, emp_id: int, bank: str, account) -> ChageMethodTransactionABC:
        self.__bank = bank
        self.__account = account
        super().__init__(database, emp_id)

    def _get_method(self) -> PaymentMethodABC:
        return DirectMethod(self.__bank, self.__account)

class ChangeMailTransaction(ChageMethodTransactionABC):
    def __init__(self, database, emp_id: int, address: str) -> ChageMethodTransactionABC:
        self.__address = address
        super().__init__(database, emp_id)

    def _get_method(self) -> PaymentMethodABC:
        return MailMethod(self.__address)

class ChangeHoldransaction(ChageMethodTransactionABC):
    def __init__(self, database, emp_id: int) -> ChageMethodTransactionABC:
        super().__init__(database, emp_id)

    def _get_method(self) -> PaymentMethodABC:
        return HoldMethod()

class ChangeAffiliationTransactionABC(ChangeEmployeeTransactionABC, ABC):
    @abstractmethod
    def __init__(self, database, emp_id: int) -> None:
        super().__init__(database, emp_id)
    
    def _change(self, employee: Employee) -> None:
        self._record_membership(employee)
        employee.affiliation = self._get_affiliation()
    
    @abstractmethod
    def _record_membership(self, employee: Employee) -> None:
        pass

    @abstractmethod
    def _get_affiliation(self):
        pass

class ChangeMemberTransaction(ChangeAffiliationTransactionABC):
    def __init__(self, database, emp_id: int, member_id: int, dues: float) -> ChangeMemberTransaction:
        self.__dues = dues
        self.__member_id = member_id
        super().__init__(database, emp_id)
    
    def _record_membership(self, employee: Employee) -> None:
        self._database.add_union_member(self.__member_id, employee)

    def _get_affiliation(self) -> UnionAffiliation:
        return UnionAffiliation(self.__member_id, self.__dues)

class ChangeUnaffiliatedTransaction(ChangeAffiliationTransactionABC):
    def __init__(self, database, emp_id: int) -> None:
        super().__init__(database, emp_id)

    def _record_membership(self, employee: Employee):
        if isinstance(employee.affiliation, UnionAffiliation):
            self._database.delete_union_member(employee.affiliation.member_id)
    
    def _get_affiliation(self) -> None:
        return None

class PaydayTransaction(DatabaseBoundTransactionABC):
    def __init__(self, database, pay_data) -> None:
        self.__pay_data = pay_data
        self.__paychecks = {}
        super().__init__(database)
    
    def execute(self) -> None:
        emp_ids = self._database.get_all_employee_ids()
        for emp_id in emp_ids:
            employee = self._database.get_employee(emp_id)
            if employee.is_pay_date(self.__pay_data):
                pay_period_start_date = employee.get_pay_period_start_date(self.__pay_data)
                paycheck = Paycheck(self.__pay_data, pay_period_start_date)
                self.__paychecks[emp_id] = paycheck
                employee.payday(paycheck)

    def get_paycheck(self, emp_id: int) -> Paycheck:
        return self.__paychecks.get(emp_id, None)