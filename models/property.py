from odoo import fields, models, api

class Property(models.Model):
  _name = 'estate.property'
  _description = 'Estate Properties'

  name                = fields.Char('Name', required=True)
  state               = fields.Selection([
                          ('new', 'New'),
                          ('received', 'Offer Received'),
                          ('accepted', 'Offer Accepted'),
                          ('sold', 'Sold'),
                          ('cancelled', 'Canceled'),
                        ], string='Status', default='new')
  tag_ids             = fields.Many2many('estate.property.tag', string="Property Tag")
  type_id             = fields.Many2one('estate.property.type', string="Property Type")
  description         = fields.Text('Description')
  postcode            = fields.Char('Postcode')
  date_availability   = fields.Date('Available From')
  expected_price      = fields.Float('Expected Price')
  best_offer          = fields.Float('Best Offer', compute='_compute_best_price')
  selling_price       = fields.Float('Selling Price', readonly=True)
  bedrooms            = fields.Integer('Bedrooms')
  living_area         = fields.Integer('Living Area(sqm)')
  facades             = fields.Integer('Facades')
  garage              = fields.Boolean('Gerage', default=False)
  garden              = fields.Boolean('Garden', default=False)
  garden_area         = fields.Integer('Garden Area')
  garden_orientation  = fields.Selection([
                        ('north', 'North'),
                        ('south', 'South'),
                        ('west', 'West'),
                        ('east', 'East'),
                      ], default='north', string='Garden Orientation')
  
  offer_ids           = fields.One2many('estate.property.offer', 'property_id', string="Offers")
  sales_id            = fields.Many2one('res.users', string='Salesman')
  buyer_id            = fields.Many2one('res.partner', string='Buyer', domain=[('is_company', '=', True)])
  # total_area = fields.Integer('Total Area')
  total_area          = fields.Integer('Total Area')
  phone               = fields.Char('Phone', related='buyer_id.phone')


  @api.onchange('living_area', 'garden_area')
  def _onchange_total_area(self):
    self.total_area = self.living_area + self.garden_area

  def action_sold(self):
    self.state = 'sold'
  
  def action_cancel(self):
    self.state = 'cancelled'
  
  @api.depends('offer_ids')
  def _compute_offer_count(self):
    for rec in self:
      rec.offer_count = len(rec.offer_ids)

  offer_count = fields.Integer('Offer Count', compute=_compute_offer_count)

  def action_property_view_offers(self):
    return {
      'type': 'ir.actions.act_window',
      'name': f"{self.name} - Offers",
      'domain': [('property_id', '=', self.id)],
      'view_mode': 'tree',
      'res_model': 'estate.property.offer',
    }

  @api.depends('offer_ids')
  def _compute_best_price(self):
    for rec in self:
      if rec.offer_ids:
        rec.best_offer = max(rec.offer_ids.mapped('price'))
      else:
        rec.best_offer = 0

class PropertyType(models.Model):
  _name = 'estate.property.type'
  _description = "Property Type"

  name = fields.Char('Name')

class PropertyTag(models.Model):
  _name = 'estate.property.tag'
  _description = 'Property Tag'

  name = fields.Char('Name')
  color = fields.Integer('Color')