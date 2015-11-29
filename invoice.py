#This file is part account_invoice_line_stand2invoice module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder

__all__ = ['LineCreateInvoiceStart', 'LineCreateInvoice']


class LineCreateInvoiceStart(ModelView):
    'Account Invoice Lines to Invoices Start'
    __name__ = 'account.invoice.line.stand2invoice.create_invoice.start'
    invoice_date = fields.Date('Invoice Date', required=True)
    description = fields.Char('Description')

    @staticmethod
    def default_invoice_date():
        Date = Pool().get('ir.date')
        return Date.today()


class LineCreateInvoice(Wizard):
    'Account Invoice Lines to Invoices'
    __name__ = 'account.invoice.line.stand2invoice.create_invoice'
    start = StateView('account.invoice.line.stand2invoice.create_invoice.start',
        'account_invoice_line_stand2invoice.create_invoice_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create', 'create_', 'tryton-ok', default=True),
            ])
    create_ = StateAction('account_invoice.act_invoice_form')

    @classmethod
    def __setup__(cls):
        super(LineCreateInvoice, cls).__setup__()
        cls._error_messages.update({
                'line_invoiced': 'Invoice line "%s" (ID %s) was invoiced (ID %s).',
                'line_party_required': ('Invoice line "%s" (ID %s) must have a '
                    'party.'),
                'line_same_invoice_type': ('The invoice lines do not have the '
                    'same invoice type.'),
                'invoice_window_name': 'Invoices - %s',
                })

    def do_create_(self, action):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Lang = pool.get('ir.lang')

        invoice_date = self.start.invoice_date
        description = self.start.description
        invoice_type = None
        parties = {}
        ids = Transaction().context['active_ids']
        for line in Pool().get('account.invoice.line').browse(ids):
            if line.invoice:
                self.raise_user_error('line_invoiced',
                    error_args=(line.description, line.id, line.invoice.id))
            if not line.party:
                self.raise_user_error('line_party_required',
                    error_args=(line.description, line.id))
            if not invoice_type:
                invoice_type = line.invoice_type
            if invoice_type != line.invoice_type:
                self.raise_user_error('line_same_invoice_type')
            if line.party not in parties:
                parties[line.party] = []
            parties[line.party].append(line)

        invoices = []
        for party in parties:
            # Create invoice
            invoice = Invoice.get_invoice_data(party, description, invoice_type)
            invoice.invoice_date = invoice_date
            with Transaction().set_user(0, set_context=True):
                invoice.save()
                invoices.append(invoice.id)

            # Relate lines to invoice
            for line in parties[party]:
                line.invoice = invoice.id
                line.save()

            # Update Taxes
            with Transaction().set_user(0, set_context=True):
                Invoice.update_taxes([invoice])

        language = Transaction().language
        languages = Lang.search([('code', '=', language)])
        if not languages:
            languages = Lang.search([('code', '=', 'en_US')])
        language = languages[0]
        formatted = Lang.strftime(invoice_date, language.code, language.date)

        action['name'] = self.raise_user_error('invoice_window_name',
            error_args=(formatted,), raise_exception=False)
        action['pyson_domain'] = PYSONEncoder().encode(
            [('id', 'in', invoices)])
        return action, {}

    def transition_open_(self):
        return 'end'
