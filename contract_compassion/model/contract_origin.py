# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp import models, fields, api, _
from psycopg2 import IntegrityError


class contract_origin(models.Model):
    """ Origin of a contract """
    _name = 'recurring.contract.origin'

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################
    name = fields.Char(compute='_set_name', store=True)
    type = fields.Selection('_get_origin_types', help=_(
        "Origin of contract : "
        " * Contact with sponsor/ambassador : an other sponsor told the "
        "person about Compassion."
        " * Event : sponsorship was made during an event"
        " * Marketing campaign : sponsorship was made after specific "
        "campaign (magazine, ad, etc..)"
        " * Transfer : sponsorship transferred from another country."
        " * Other : select only if none other type matches."
    ), required=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    analytic_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account')
    contract_ids = fields.One2many(
        'recurring.contract', 'origin_id', 'Sponsorships originated',
        readonly=True)
    country_id = fields.Many2one('res.country', 'Country')
    other_name = fields.Char('Give details', size=128)
    won_sponsorships = fields.Integer(
        compute='get_won_sponsorships', store=True)
    conversion_rate = fields.Float(
        compute='get_won_sponsorships', store=True)

    _sql_constraints = [(
        'name_uniq', 'UNIQUE(name)',
        _("You cannot have two origins with same name."
          "The origin does probably already exist.")
    )]

    ##########################################################################
    #                             FIELDS METHODS                             #
    ##########################################################################
    @api.one
    @api.depends('type')
    def _set_name(self):
        name = ""
        if self.type == 'partner':
            if self.partner_id.parent_id:
                name = self.partner_id.parent_id.name + ", "
            name += self.partner_id.name or _(
                'Contact with Sponsor/Ambassador')
        elif self.type in ('event', 'marketing'):
            name = self.analytic_id.name
        elif self.type == 'transfer':
            if self.country_id:
                name = _('Transfer from ') + self.country_id.name
            else:
                name = _('Transfer from partner country')
        elif self.type == 'other':
            name = self.other_name or 'Other'
        elif self.type == 'sub':
            name = _('SUB Sponsorship')

        self.name = name

    def _get_origin_types(self):
        return [
            ('partner', _("Contact with sponsor/ambassador")),
            ('event', _("Event")),
            ('marketing', _("Marketing campaign")),
            ('sub', _("SUB Sponsorship")),
            ('transfer', _("Transfer")),
            ('other', _("Other")),
        ]

    @api.depends('contract_ids.origin_id', 'contract_ids.activation_date')
    @api.multi
    def get_won_sponsorships(self):
        for origin in self.filtered('contract_ids'):
            contract_ids = origin.contract_ids
            origin.won_sponsorships = len(contract_ids)
            origin.conversion_rate = len(
                contract_ids.filtered('activation_date')) / float(len(
                    contract_ids)) * 100

    ##########################################################################
    #                              ORM METHODS                               #
    ##########################################################################
    @api.model
    def create(self, vals):
        """Try to find existing origin instead of raising an error."""
        try:
            res = super(contract_origin, self).create(vals)
        except IntegrityError:
            # Find the origin
            self.env.cr.commit()     # Release the lock
            origins = self.search([
                ('type', '=', vals.get('type')),
                ('partner_id', '=', vals.get('partner_id')),
                ('analytic_id', '=', vals.get('analytic_id')),
                ('country_id', '=', vals.get('country_id')),
                ('other_name', '=', vals.get('other_name')),
            ])
            if origins:
                res = origins[0]
            else:
                raise

        # Put analytic account of the user if it exists
        partner = res.partner_id
        if res.type == 'partner' and partner and not res.analytic_id:
            partner_name = partner.name
            if partner.parent_id:
                partner_name = partner.parent_id.name + ', ' + partner_name
            analytic_account = self.env[
                'account.analytic.account'].with_context(lang='en_US').search(
                    [('name', '=', partner_name)], limit=1)
            res.analytic_id = analytic_account

        return res
