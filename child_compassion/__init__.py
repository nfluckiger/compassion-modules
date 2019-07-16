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
from . import mappings
from . import controllers
from . import wizards
from odoo import api, SUPERUSER_ID


def post_init_function(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['import.json.mapping'].python_install_mapping()