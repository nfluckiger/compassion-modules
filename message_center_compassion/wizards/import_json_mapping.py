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
import os


class ImportJsonMapping(models.TransientModel):

    _name = "import.json.mapping"

    mapping_name = fields.Char()
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    file = fields.Binary()

    @api.multi
    def import_json_mapping(self):
        self.ensure_one()
        dec = str(base64.decodebytes(self.file), 'utf-8').replace("\\", "")\
            .replace("\n\t", "").replace("\n", "")
        data = json.loads(dec)

        mapping = self.env['compassion_mapping'].create({
            'name': self.mapping_name,
            'model_id': self.model_id.id
        })
        mapping.create_from_json(data)

    @api.model
    def python_install_mapping(self, file_name):
        file = open(file_name)

        json_file = file.read()

        data = json.loads(json_file)

        for mapping_keys, mapping_data in data.items():
            odoo_model = self.env['ir.model'].search(
                [('model', '=', mapping_data['odoo'])]
            )
            mapping = self.env['compassion.mapping'].create({
                'name': mapping_data['name'],
                'model_id': odoo_model.id
            })
            mapping.create_from_json(mapping_data['mapping'])
