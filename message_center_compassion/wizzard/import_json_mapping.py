# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Flückiger Nathan <nathan.fluckiger@hotmail.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import models, fields, api
import base64
import json


class ImportJsonMapping(models.TransientModel):

    _name = "import_json_mapping"

    mapping_name = fields.Char()
    file = fields.Binary()

    @api.multi
    def import_json_mapping(self):
        self.ensure_one()
        dec = str(base64.decodebytes(self.file), 'utf-8').replace("\\", "")\
            .replace("\n\t", "").replace("\n", "")
        data = json.loads(dec)

        mapping = self.env['compassion_mapping'].create({
            'name': self.mapping_name
        })
        mapping.create_from_json(data)
