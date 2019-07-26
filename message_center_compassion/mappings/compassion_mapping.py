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


class CompassionMapping(models.Model):

    _name = "compassion.mapping"

    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    # Models and fieldToJson link
    fields_json_ids = fields.Many2many('compassion.field.to.json')

    @api.multi
    def create_from_json(self, json):
        '''
         Function used to import JSON file to create a new mapping
        :param json: JSON loaded with json field name and odoo field name
        :return:return the mapping id
        '''
        self.ensure_one()
        fields = []
        for field in json.keys():
            if type(json[field]) is dict:
                tmp_mapping = self.create({
                    'name': json[field]['name'],
                    'model_id': json[field]['odoo']
                })
                tmp_mapping.create_from_json(json[field]['mapping'])
                fields.append(self.env['compassion.field.to.json'].create({
                    'field_id': False,
                    'json_name': field,
                    'sub_mapping_id': tmp_mapping.id
                }).id)
            else:
                if type(json[field]) is str:
                    json[field] = [json[field]]
                for multi_name in json[field]:
                    split_name = multi_name.split(".")
                    model_id = self.model_id
                    name = ""
                    for index in range(0, len(split_name)-1):
                        model_name = self.env['ir.model.fields'].search([
                           '&', ('name', '=', split_name[index]),
                                ('model_id', '=', self.model_id.id)
                        ]).relation
                        model_id = self.env['ir.model'].search([
                            ('model', '=', model_name)
                        ])
                        name = split_name[index+1]

                    split_name = name if name else split_name[0]
                    field_name = self.env['ir.model.fields'].search([
                       '&', ('name', '=', split_name),
                            ('model_id', '=', model_id.id)
                    ])
                    field_to_json = self.env['compassion.field.to.json'].search([
                        '&', ('json_name', '=', field),
                        ('field_id', '=', field_name.id)]).id
                    if not field_to_json:
                        fields.append(self.env['compassion.field.to.json'].create({
                            'field_id': field_name.id,
                            'json_name': field,
                            'sub_mapping_id': False
                        }).id)
                    else:
                        fields.append(field_to_json)

        duplicate_mapping = self.env['compassion.mapping'].search([
            ('model_id', '=', self.model_id.id)
        ])
        for mapping in duplicate_mapping:
            if mapping.fields_json_ids == fields:
                return duplicate_mapping

        self.write({
            'fields_json_ids': [(6, 0, fields)]
        })
        return self
