# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Cyril Sester <csester@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################

from . import models
from . import controllers
from . import wizards
from odoo import api, SUPERUSER_ID
import os


def post_init_function(cr, registery):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        file_name = os.path.join(os.path.dirname(__file__)) + \
                        '/static/src/json/mappings.json'
        env['import.json.mapping'].python_install_mapping(file_name)
