# This file is part of the account_invoice_line_stand2invoice module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountInvoiceLineStand2invoiceTestCase(ModuleTestCase):
    'Test Account Invoice Line Stand2invoice module'
    module = 'account_invoice_line_stand2invoice'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountInvoiceLineStand2invoiceTestCase))
    return suite