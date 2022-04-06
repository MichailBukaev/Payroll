import email
import unittest
import datetime
from core.classes.affiliation import *
import core.classes.transaction as t
from core.classes.employee import *
from core.classes.paymentclassification import *
from core.classes.paymentmethod import *
from core.classes.paymentschedule import *
from unit_tests.mocks import PayrollDatabaseMock


class Test_TestAddEmployee(unittest.TestCase):
    def setUp(self) -> None:
        self.__db = PayrollDatabaseMock()
        super().setUp()

    def tearDown(self):
        self.__db.clear()

    def test_add_salaried_employee(self):
        emp_id = 1
        add_salaried_employee = t.AddSalariedEmployeeTransaction(emp_id, 'Bob', 'Home', self.__db, 1000.00)
        add_salaried_employee.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertEqual('Bob', employee.name)

        payment_classification = employee.classification
        self.assertIs(type(payment_classification), SalariedClassification)
        self.assertEqual(1000.00, payment_classification.salary)
        self.assertIs(type(employee.schedule), MonthlySchedule)
        self.assertIs(type(employee.method), HoldMethod)

    def test_add_hourly_empoyee(self):
        emp_id = 2
        add_hourly_employee = t.AddHourlyEmployeeTransaction(emp_id, 'Tom', 'Home', self.__db, 20.00)
        add_hourly_employee.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertEqual('Tom', employee.name)

        payment_classification = employee.classification
        self.assertIs(type(payment_classification), HourlyClassification)
        self.assertEqual(20.00, payment_classification.hourly_rate)
        self.assertIs(type(employee.schedule), WeeklySchedule)
        self.assertIs(type(employee.method), HoldMethod)

    def test_add_commissioned_empoyee(self):
        emp_id = 3
        add_commissioned_employee = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Sam', 'Home', self.__db, 0.1, 1500.00
        )
        add_commissioned_employee.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertEqual('Sam', employee.name)

        payment_classification = employee.classification
        self.assertIs(type(payment_classification), CommissionedClassification)
        self.assertEqual(1500.00, payment_classification.salary)
        self.assertEqual(0.1, payment_classification.commission_rate)
        self.assertIs(type(employee.schedule), BeweeklySchedule)
        self.assertIs(type(employee.method), HoldMethod)

    def test_delete_employee(self):
        emp_id = 4
        add_emp_transaction = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 3.2, 2500
        )
        add_emp_transaction.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee, Employee)

        delete_eml_transaction = t.DeleteEmployeeTransaction(emp_id, self.__db)
        delete_eml_transaction.execute()

        employee = self.__db.get_employee(emp_id)
        self.assertIsNone(employee)

    def test_add_time_card(self):
        emp_id = 5
        date = datetime.date(2005, 7, 31)
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        add_time_card_t = t.AddTimeCardTransaction(date, 8.0, emp_id, self.__db)
        add_time_card_t.execute()

        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        classification = employee.classification
        self.assertIsInstance(classification, HourlyClassification)
        time_card = classification.get_time_card(date)
        self.assertIsNotNone(time_card)
        self.assertIs(time_card.hours, 8.0)
        self.assertIs(time_card.date, date)

    def test_add_sales_receipt(self):
        emp_id = 6
        date = datetime.date(2006, 5, 15)
        add_commissioned_emp_t = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Tom', 'Home', self.__db, 0.1, 1500.00
        )
        add_commissioned_emp_t.execute()
        add_sales_receipt_t = t.AddSalesReceiptTransaction(self.__db, date, 150.00, emp_id)
        add_sales_receipt_t.execute()

        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        classification = employee.classification
        self.assertIsInstance(classification, CommissionedClassification)
        sales_receipt = classification.get_sales_receipt(date)
        self.assertIsNotNone(sales_receipt)
        self.assertIs(sales_receipt.amount, 150.00)
        self.assertIs(sales_receipt.date, date)

    def test_add_service_charge(self):
        emp_id = 7
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Tom', 'Home', self.__db, 25
        )
        add_hourly_emp_t.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        member_id = 86
        union_affiliation = UnionAffiliation(member_id, 99.42)
        employee.affiliation = union_affiliation
        self.__db.add_union_member(member_id, employee)
        date = datetime.date(2005, 8, 8)
        service_cahrge_t = t.AddServiceChargeTransaction(self.__db, date, 12.95, member_id)
        service_cahrge_t.execute()
        service_charge = union_affiliation.get_service_charge(date)
        self.assertIsNotNone(service_charge)
        self.assertIs(service_charge.amount, 12.95)

    def test_change_name_transaction(self):
        emp_id = 8
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        change_name_transaction = t.ChangeNameTransaction(self.__db, emp_id, 'Bob')
        change_name_transaction.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIs('Bob', employee.name)

    def test_change_address_transaction(self):
        emp_id = 9
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        change_addres_transaction = t.ChangeAddressTransaction(self.__db, emp_id, 'New home')
        change_addres_transaction.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIs('New home', employee.address)

    def test_change_hourly_transaction(self):
        emp_id = 10
        add_commissioned_emp = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Lance', 'Home', self.__db, 2500, 3.2
        )
        add_commissioned_emp.execute()
        change_hourly_transaction = t.ChangeHourlyTransaction(self.__db, emp_id, 27.52)
        change_hourly_transaction.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee.classification, HourlyClassification)
        self.assertIs(27.52, employee.classification.hourly_rate)
        self.assertIsInstance(employee.schedule, WeeklySchedule)

    def test_change_salaried_transaction(self):
        emp_id = 11
        add_commissioned_emp = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Lance', 'Home', self.__db, 2500, 3.2
        )
        add_commissioned_emp.execute()
        change_salaried_transaction = t.ChangeSalariedTransaction(self.__db, emp_id, 6000.00)
        change_salaried_transaction.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee.classification, SalariedClassification)
        self.assertIs(6000.00, employee.classification.salary)
        self.assertIsInstance(employee.schedule, MonthlySchedule)

    def test_change_commissioned_transaction(self):
        emp_id = 12
        add_salaried_emp = t.AddSalariedEmployeeTransaction(
            emp_id, 'Lance', 'Home', self.__db, 3000.00
        )
        add_salaried_emp.execute()
        change_commissioned_transaction = t.ChangeCommissionedTransaction(self.__db, emp_id, 2500.00, 3.2)
        change_commissioned_transaction.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee.classification, CommissionedClassification)
        self.assertIs(2500.00, employee.classification.salary)
        self.assertIs(3.2, employee.classification.commission_rate)
        self.assertIsInstance(employee.schedule, BeweeklySchedule)


    def test_change_direct_transaction(self):
        emp_id = 13
        add_salaried_emp = t.AddSalariedEmployeeTransaction(
            emp_id, 'Bob', 'Home', self.__db, 3000.00
        )
        add_salaried_emp.execute()
        change_direct_t = t.ChangeDirectTransaction(self.__db, emp_id, 'Bank', '1234-5678-9101-1123')
        change_direct_t.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee.method, DirectMethod)
        self.assertIs('Bank', employee.method.bank)
        self.assertIs('1234-5678-9101-1123', employee.method.account)

    def test_change_mail_transaction(self):
        emp_id = 14
        add_salaried_emp = t.AddSalariedEmployeeTransaction(
            emp_id, 'Bob', 'Home', self.__db, 3000.00
        )
        add_salaried_emp.execute()
        change_direct_t = t.ChangeMailTransaction(self.__db, emp_id, 'Home')
        change_direct_t.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee.method, MailMethod)
        self.assertIs('Home', employee.method.address)

    def test_change_hold_transaction(self):
        emp_id = 15
        add_salaried_emp = t.AddSalariedEmployeeTransaction(
            emp_id, 'Bob', 'Home', self.__db, 3000.00
        )
        add_salaried_emp.execute()

        change_direct_t = t.ChangeMailTransaction(self.__db, emp_id, 'Home')
        change_direct_t.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee.method, MailMethod)

        self.assertIs('Home', employee.method.address)
        change_hold_t = t.ChangeHoldransaction(self.__db, emp_id)
        change_hold_t.execute()
        self.assertIsInstance(employee.method, HoldMethod)

    def test_change_union_member_transaction(self):
        emp_id = 16
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        member_id = 7743
        change_member_t = t.ChangeMemberTransaction(
            self.__db, emp_id, member_id, 99.42
        )
        change_member_t.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsNotNone(employee.affiliation)
        self.assertIsInstance(employee.affiliation, UnionAffiliation)
        self.assertIs(99.42, employee.affiliation.dues)
        union_member = self.__db.get_union_member(member_id)
        self.assertIsNotNone(union_member)
        self.assertEqual(employee, union_member)

    def test_change_unaffiliated_transaction(self):
        emp_id = 17
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        member_id = 7745

        change_member_t = t.ChangeMemberTransaction(
            self.__db, emp_id, member_id, 99.42
        )
        change_member_t.execute()
        employee = self.__db.get_employee(emp_id)
        union_member = self.__db.get_union_member(member_id)
        self.assertIsNotNone(union_member)
        self.assertEqual(employee, union_member)
        
        change_unaffiliated_t = t.ChangeUnaffiliatedTransaction(self.__db, emp_id)
        change_unaffiliated_t.execute()
        self.assertIsNone(employee.affiliation)
        union_member = self.__db.get_union_member(union_member)
        self.assertIsNone(union_member)

    def test_pay_single_salaried_employee(self):
        emp_id = 18
        add_salaried_emp_t = t.AddSalariedEmployeeTransaction(
            emp_id, 'Bob', 'Hom', self.__db, 1000.00
        )
        add_salaried_emp_t.execute()
        pay_date = date(2001, 11, 30)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        paycheck = payday_t.get_paycheck(emp_id)
        self.assertIsNotNone(paycheck)
        self.assertEqual(pay_date, paycheck.pay_date)
        self.assertEqual(1000.00, paycheck.gross_pay)
        self.assertEqual('Hold', paycheck.disposition)
        self.assertEqual(0.0, paycheck.deductions)
        self.assertEqual(1000.00, paycheck.net_pay)
        self.assertEqual(date(2001, 11, 30), paycheck.pay_period.end_date)
        self.assertEqual(date(2001, 11, 1), paycheck.pay_period.start_date)

    def test_pay_single_salaried_employee_on_wrong_date(self):
        emp_id = 19
        add_salaried_emp_t = t.AddSalariedEmployeeTransaction(
            emp_id, 'Bob', 'Hom', self.__db, 1000.00
        )
        add_salaried_emp_t.execute()
        pay_date = date(2001, 11, 29)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        paycheck = payday_t.get_paycheck(emp_id)
        self.assertIsNone(paycheck)

    def test_paying_single_hourly_employee_no_time_card(self):
        emp_id = 20
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        pay_date = date(2001, 11, 9)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        self.__validate_hourly_pay_check(payday_t, emp_id, pay_date, 0.0)

    def __validate_hourly_pay_check(self, payday_t : t.PaydayTransaction, emp_id: int, pay_date: date, pay: float):
        paycheck = payday_t.get_paycheck(emp_id)
        self.assertIsNotNone(paycheck)
        self.assertEqual(pay_date, paycheck.date)
        self.assertEqual(pay, paycheck.gross_pay)
        self.assertEqual('Hold', paycheck.disposition)
        self.assertEqual(0.0, paycheck.deductions)
        self.assertEqual(pay, paycheck.net_pay)


if __name__ == '__main__':
    unittest.main()