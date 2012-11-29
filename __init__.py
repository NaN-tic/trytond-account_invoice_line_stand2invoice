#This file is part account_invoice_line_stand2invoice module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool
from .invoice import *


def register():
    Pool.register(
        LineCreateInvoice,
        module='account_invoice_line_stand2invoice', type_='wizard')
