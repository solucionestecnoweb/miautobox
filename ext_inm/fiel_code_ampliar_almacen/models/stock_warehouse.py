# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from itertools import product
import json
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

import time

class StockWarehouse(models.Model):
	_inherit = "stock.warehouse"

	 code = fields.Char('Short Name', required=True, size=15, help="Short name used to identify your warehouse")