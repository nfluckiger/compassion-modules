﻿# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp import api, fields, models


class CollectGiftWizard(models.TransientModel):
    """ This wizard generates a Gift Invoice for a given contract. """
    _name = 'gift.collect.wizard'

    invoice_line_ids = fields.Many2many(
        'account.invoice.line', string='Invoice lines',
    )
    domain = fields.Char(
        default="[('product_id.name', '=', 'Child gift'),"
                " ('state', '=', 'paid'),"
                " ('gift_id', '=', False)]"
    )

    @api.onchange('domain')
    def apply_domain(self):
        return {
            'domain': {'invoice_line_ids': eval(self.domain)}
        }

    @api.multi
    def collect_invoices(self):
        # Read data in english
        self.ensure_one()
        gift = self.env['sponsorship.gift'].browse(
            self.env.context['active_id'])
        self.invoice_line_ids.write({'gift_id': gift.id})
        return gift.write({
            'invoice_line_ids': [(4, id) for id in self.invoice_line_ids.ids]
        })
