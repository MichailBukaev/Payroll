from ast import Assert
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
            emp_id, 'Sam', 'Home', self.__db, 0.1, 1500.00, datetime.date(2005, 7, 31) 
        )
        add_commissioned_employee.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertEqual('Sam', employee.name)

        payment_classification = employee.classification
        self.assertIs(type(payment_classification), CommissionedClassification)
        self.assertEqual(1500.00, payment_classification.salary)
        self.assertEqual(0.1, payment_classification.commission_rate)
        self.assertIs(type(employee.schedule), BeweeklySchedule)
        self.assertEqual(datetime.date(2005, 7, 31), employee.schedule.work_start_date)
        self.assertIs(type(employee.method), HoldMethod)

    def test_delete_employee(self):
        emp_id = 4
        add_emp_transaction = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 3.2, 2500, datetime.date(2005, 7, 31)
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
            emp_id, 'Tom', 'Home', self.__db, 0.1, 1500.00, datetime.date(2005, 7, 31)
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
            emp_id, 'Lance', 'Home', self.__db, 2500, 3.2, datetime.date(2005, 7, 31)
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
            emp_id, 'Lance', 'Home', self.__db, 2500, 3.2, datetime.date(2005, 7, 31)
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
        change_commissioned_transaction = t.ChangeCommissionedTransaction(self.__db, emp_id, 2500.00, 3.2, datetime.date(2005, 7, 31))
        change_commissioned_transaction.execute()
        employee = self.__db.get_employee(emp_id)
        self.assertIsNotNone(employee)
        self.assertIsInstance(employee.classification, CommissionedClassification)
        self.assertEqual(2500.00, employee.classification.salary)
        self.assertEqual(3.2, employee.classification.commission_rate)
        self.assertIsInstance(employee.schedule, BeweeklySchedule)
        self.assertEqual(datetime.date(2005, 7, 31), employee.schedule.work_start_date)


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
        self.assertEqual('Bank', employee.method.bank)
        self.assertEqual('1234-5678-9101-1123', employee.method.account)

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
        pay_date = date(2001, 11, 9) #friday
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        self.__validate_pay_check(payday_t, emp_id, pay_date, date(2001, 11, 3), 0.0, 0.0, 0.0)

    def test_pay_single_hourly_employee_one_timme_card(self):
        emp_id = 21
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        pay_date = date(2001, 11, 9) #friday
        add_time_card_t = t.AddTimeCardTransaction(pay_date, 2.0, emp_id, self.__db)
        add_time_card_t.execute()
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        expected_pay = 30.5
        self.__validate_pay_check(payday_t, emp_id, pay_date, date(2001, 11, 3), expected_pay, expected_pay, 0.0)

    def test_pay_single_hourly_employee_overtime_one_time_card(self):
        emp_id = 22
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        pay_date = date(2001, 11, 9) #friday
        add_time_card_t = t.AddTimeCardTransaction(pay_date, 9.0, emp_id, self.__db)
        add_time_card_t.execute()
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        expected_pay = (8 + 1.5) * 15.25
        self.__validate_pay_check(payday_t, emp_id, pay_date, date(2001, 11, 3), expected_pay, expected_pay, 0.0)

    def test_pay_single_hourly_employee_on_wrong_date(self):
        emp_id = 23
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        pay_date = date(2001, 11, 8) #thursday
        add_time_card_t = t.AddTimeCardTransaction(pay_date, 9.0, emp_id, self.__db)
        add_time_card_t.execute()
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        paycheck = payday_t.get_paycheck(emp_id)
        self.assertIsNone(paycheck)

    def test_pay_single_hourly_employee_three_time_cards(self):
        emp_id = 24
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        pay_date = date(2001, 11, 9) #friday
        add_time_card_ts = [
            t.AddTimeCardTransaction(date(2001, 11, 3), 2.0, emp_id, self.__db),
            t.AddTimeCardTransaction(date(2001, 11, 6), 5.0, emp_id, self.__db),
            t.AddTimeCardTransaction(date(2001, 11, 9), 9.0, emp_id, self.__db)
        ]
        for add_time_card_t in add_time_card_ts:
            add_time_card_t.execute()
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        expected_pay = (8 + 1.5 + 5 + 2) * 15.25
        self.__validate_pay_check(payday_t, emp_id, pay_date, date(2001, 11, 3), expected_pay, expected_pay, 0.0)

    def test_pay_single_hourly_employee_with_time_cards_cpanning_three_pay_periods(self):
        emp_id = 25
        add_hourly_emp_t = t.AddHourlyEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 15.25
        )
        add_hourly_emp_t.execute()
        pay_date = date(2001, 11, 9) #friday
        add_time_card_ts = [
            t.AddTimeCardTransaction(date(2001, 11, 2), 5.0, emp_id, self.__db),
            t.AddTimeCardTransaction(date(2001, 11, 6), 2.0, emp_id, self.__db),
            t.AddTimeCardTransaction(date(2001, 11, 10), 5.0, emp_id, self.__db)
        ]
        for add_time_card_t in add_time_card_ts:
            add_time_card_t.execute()
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        expected_pay = 2 * 15.25
        self.__validate_pay_check(payday_t, emp_id, pay_date, date(2001, 11, 3), expected_pay, expected_pay, 0.0)

    def test_pay_commissioned_employee_no_sales_receipt_first_pay_day(self):
        emp_id = 26
        add_commissioned_emp_t = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 0.2, 500, date(2022, 4, 4)
        )
        add_commissioned_emp_t.execute()
        pay_date = date(2022, 4, 15)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        expected_pay = 500
        self.__validate_pay_check(payday_t, emp_id, pay_date, date(2022, 4, 4), expected_pay, expected_pay, 0.0)

    def test_pay_commissioned_employee_no_sales_receipt_any_pay_day(self):
        emp_id = 27
        add_commissioned_emp_t = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 0.2, 500, date(2022, 4, 4)
        )
        add_commissioned_emp_t.execute()
        pay_date = date(2022, 5, 13)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        expected_pay = 500
        self.__validate_pay_check(payday_t, emp_id, pay_date, date(2022, 4, 30), expected_pay, expected_pay, 0.0)

    def test_pay_commissioned_employee_on_wrong_date(self):
        emp_id = 28
        add_commissioned_emp_t = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 0.2, 500, date(2022, 4, 4)
        )
        add_commissioned_emp_t.execute()
        pay_date = date(2022, 4, 18)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        paycheck = payday_t.get_paycheck(emp_id)
        self.assertIsNone(paycheck)

    def test_pay_commissioned_employee_one_sales_receipt(self):
        emp_id = 29
        add_commissioned_emp_t = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 0.2, 500, date(2022, 4, 4)
        )
        add_commissioned_emp_t.execute()
        pay_date = date(2022, 5, 13)
        period_start_date = date(2022, 4, 30)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        add_sales_receipt_t = t.AddSalesReceiptTransaction(self.__db, pay_date, 150.00, emp_id)
        add_sales_receipt_t.execute()
        payday_t.execute()
        expected_pay = 530
        self.__validate_pay_check(payday_t, emp_id, pay_date, period_start_date, expected_pay, expected_pay, 0.0)

    def test_pay_commissioned_employee_three_sales_receipts(self):
        emp_id = 30
        add_commissioned_emp_t = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 0.2, 500, date(2022, 4, 4)
        )
        add_commissioned_emp_t.execute()
        pay_date = date(2022, 5, 13)
        period_start_date = date(2022, 4, 30)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        add_sales_receipt_ts = [
            t.AddSalesReceiptTransaction(self.__db, date(2022, 4, 30), 100.00, emp_id),
            t.AddSalesReceiptTransaction(self.__db, date(2022, 5, 6), 200.00, emp_id),
            t.AddSalesReceiptTransaction(self.__db, date(2022, 5, 13), 150.00, emp_id)
        ]
        for add_sales_receipt_t in add_sales_receipt_ts:
            add_sales_receipt_t.execute()
        payday_t.execute()
        expected_pay = 500 + ((150 + 200 + 100) * 0.2)
        self.__validate_pay_check(payday_t, emp_id, pay_date, period_start_date, expected_pay, expected_pay, 0.0)

    def test_pay_commissioned_employee_three_sales_receipts_cpanning_three_pay_periods(self):
        emp_id = 31
        add_commissioned_emp_t = t.AddCommissionedEmployeeTransaction(
            emp_id, 'Bill', 'Home', self.__db, 0.2, 500, date(2022, 4, 4)
        )
        add_commissioned_emp_t.execute()
        pay_date = date(2022, 5, 13)
        period_start_date = date(2022, 4, 30)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        add_sales_receipt_ts = [
            t.AddSalesReceiptTransaction(self.__db, date(2022, 4, 29), 100.00, emp_id),
            t.AddSalesReceiptTransaction(self.__db, date(2022, 5, 6), 200.00, emp_id),
            t.AddSalesReceiptTransaction(self.__db, date(2022, 5, 14), 150.00, emp_id)
        ]
        for add_sales_receipt_t in add_sales_receipt_ts:
            add_sales_receipt_t.execute()
        payday_t.execute()
        expected_pay = 540
        self.__validate_pay_check(payday_t, emp_id, pay_date, period_start_date, expected_pay, expected_pay, 0.0)

    def test_salaried_union_member_dues(self):
        emp_id = 32
        add_salaried_emp_t = t.AddSalariedEmployeeTransaction(emp_id, 'Bill', 'Home', self.__db, 1000.00)
        add_salaried_emp_t.execute()
        member_id = 7734
        change_member_t = t.ChangeMemberTransaction(self.__db, emp_id, member_id, 9.42)
        change_member_t.execute()
        pay_date = date(2001, 11, 30)
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        self.__validate_pay_check(
            payday_t=payday_t,
            emp_id=emp_id,
            pay_date=pay_date,
            start_date=date(2001, 11, 1),
            gross_pay=1000.00,
            net_pay=1000.00 - (9.42 * 5),
            deductions=9.42 * 5
        )

    def test_hourly_union_member_service_charge(self):
        emp_id = 33
        add_salaried_emp_t = t.AddHourlyEmployeeTransaction(emp_id, 'Bill', 'Home', self.__db, 15.24)
        add_salaried_emp_t.execute()
        member_id = 7735
        change_member_t = t.ChangeMemberTransaction(self.__db, emp_id, member_id, 9.42)
        change_member_t.execute()
        pay_date = date(2001, 11, 30)
        add_service_charge_t = t.AddServiceChargeTransaction(self.__db, pay_date, 19.42, member_id)
        add_service_charge_t.execute()
        add_time_card_t = t.AddTimeCardTransaction(pay_date, 8.0, emp_id, self.__db)
        add_time_card_t.execute()
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        self.__validate_pay_check(
            payday_t=payday_t,
            emp_id=emp_id,
            pay_date=pay_date,
            start_date=date(2001, 11, 24),
            gross_pay=(8 * 15.24),
            net_pay=(8 * 15.24) - (9.42 + 19.42),
            deductions=(9.42 + 19.42)
        )

    def test_service_charges_spanning_multiple_pay_periods(self):
        emp_id = 34
        add_salaried_emp_t = t.AddHourlyEmployeeTransaction(emp_id, 'Bill', 'Home', self.__db, 15.24)
        add_salaried_emp_t.execute()
        member_id = 7735
        change_member_t = t.ChangeMemberTransaction(self.__db, emp_id, member_id, 9.42)
        change_member_t.execute()
        pay_date = date(2001, 11, 30)
        add_service_charge_ts = [
            t.AddServiceChargeTransaction(self.__db, date(2001, 11, 23), 19.42, member_id),
            t.AddServiceChargeTransaction(self.__db, pay_date, 19.42, member_id),
            t.AddServiceChargeTransaction(self.__db, date(2001, 12, 1), 19.42, member_id),
        ]
        for add_service_charge_t in add_service_charge_ts:
            add_service_charge_t.execute()
        add_time_card_t = t.AddTimeCardTransaction(pay_date, 8.0, emp_id, self.__db)
        add_time_card_t.execute()
        payday_t = t.PaydayTransaction(self.__db, pay_date)
        payday_t.execute()
        self.__validate_pay_check(
            payday_t=payday_t,
            emp_id=emp_id,
            pay_date=pay_date,
            start_date=date(2001, 11, 24),
            gross_pay=(8 * 15.24),
            net_pay=(8 * 15.24) - (9.42 + 19.42),
            deductions=(9.42 + 19.42)
        )

    def __validate_pay_check(self, payday_t : t.PaydayTransaction, emp_id: int, pay_date: date, start_date: date, gross_pay: float, net_pay: float, deductions: float):
        paycheck = payday_t.get_paycheck(emp_id)
        self.assertIsNotNone(paycheck)
        self.assertEqual(pay_date, paycheck.date)
        self.assertEqual(start_date, paycheck.pay_period.start_date)
        self.assertEqual(pay_date, paycheck.pay_period.end_date)
        self.assertEqual(gross_pay, paycheck.gross_pay)
        self.assertEqual('Hold', paycheck.disposition)
        self.assertEqual(deductions, paycheck.deductions)
        self.assertEqual(net_pay, paycheck.net_pay)

if __name__ == '__main__':
    unittest.main()