#This file is part account_invoice_line_stand2invoice module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder

__all__ = ['LineCreateInvoice']


class LineCreateInvoice(Wizard):
    'Account Invoice Lines to Invoice'
    __name__ = 'account.invoice.line.stand2invoice.create_invoice'
    start_state = 'open_'
    open_ = StateAction('account_invoice.act_invoice_out_invoice_form')

    @classmethod
    def __setup__(cls):
        super(LineCreateInvoice, cls).__setup__()
        cls._error_messages.update({
            'line_invoiced': 'Invoice line "%s" (%s) was invoiced (%s)!',
            'line_party_required': 'Invoice line "%s" (%s) must be a party!',
            'line_type_out_invoice': 'Invoice line "%s" (%s) not Out Invoice!',
            'line_same_party': 'Select Invoice Lines same party to invoice!',
            'invoice_window_name': 'Invoice - %s',
            })

    def do_open_(self, action):
        party = None

        pool = Pool()
        Invoice = pool.get('account.invoice')
        InvoiceLine = pool.get('account.invoice.line')

        lines = []
        ids = Transaction().context['active_ids']
        for line in Pool().get('account.invoice.line').browse(ids):
            if line.invoice:
                self.raise_user_error('line_invoiced',
                    error_args=(line.description, line, line.invoice))
            if not line.party:
                self.raise_user_error('line_party_required',
                    error_args=(line.description, line))
            if not line.invoice_type == 'out_invoice':
                self.raise_user_error('line_type_out_invoice',
                    error_args=(line.description, line))
            if not party:
                party = line.party
            if party != line.party:
                self.raise_user_error("line_same_party")

            lines.append(line)

        # Create invoice
        description = None
        vals = Invoice.get_invoice_data(party, description)
        with Transaction().set_user(0, set_context=True):
            invoice = Invoice.create([vals])[0]

        # Write Invoice Lines
        InvoiceLine.write(lines, {'invoice': invoice})

        # Update Taxes
        with Transaction().set_user(0, set_context=True):
            Invoice.update_taxes([invoice])

        action['pyson_domain'] = PYSONEncoder().encode(
            [('id', '=', invoice.id)])
        action['name'] = self.raise_user_error('invoice_window_name',
            error_args=(party.name), raise_exception=False)
        return action, {}

    def transition_open_(self):
        return 'end'
