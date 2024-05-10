from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError

class PropertyOffer(models.Model):
  _name = 'estate.property.offer'
  _description = 'Estate Property Offers'

  @api.depends('property_id', 'partner_id')
  def _compute_name(self):
    for rec in self:
      if rec.property_id and rec.partner_id:
        rec.name = f"{rec.property_id.name} - {rec.partner_id.name}"
      else:
        rec.name = False

  name      = fields.Char('Description', compute="_compute_name")
  price     = fields.Float('Price')
  status    = fields.Selection([
              ('accepted', 'Accepted'),
              ('refused', 'Refused'),
            ], string='status')

  partner_id  = fields.Many2one('res.partner', string="Customer")
  property_id = fields.Many2one('estate.property', string="Property")
  validity    = fields.Integer('Validity', default=7)
  daedline    = fields.Date('Deadline', compute="_compute_deadline", inverse="_inverse_deadline")
  
  # _sql_constraints = [
  #   ('check_validity', 'check(validity > 0)', 'Deadline cannot be before creation date')
  # ]

  @api.model
  def _set_creation_date(self):
    return fields.Date.today()
  
  creation_date = fields.Date('Creation Date', default=_set_creation_date)

  @api.depends('validity', 'creation_date')
  def _compute_deadline(self):
    for record in self:
      if record.creation_date and record.validity:
        record.daedline = record.creation_date + timedelta(record.validity)
      else:
        record.daedline = False

  def _inverse_deadline(self):
    for rec in self:
      if rec.daedline and rec.creation_date:
        rec.validity = (rec.daedline - rec.creation_date).days
      else:
        rec.validity = False

  @api.constrains('validity')
  def _check_validity(self):
    for rec in self:
      if rec.daedline <= rec.creation_date:
        raise ValidationError(f"Deadline cannot be before creation date")

  def action_accept_offer(self):
    if self.property_id:
      self._validation_accepted_offer()
      self.property_id.write({
        'selling_price': self.price,
        'state': 'accepted'
      })
    self.status = 'accepted'

  def _validation_accepted_offer(self):
    offer_ids = self.env['estate.property.offer'].search([
      ('property_id', '=', self.property_id.id),
      ('status', '=', 'accepted'),
    ])
    if offer_ids:
      raise ValidationError(f"You have an accepted already")

  def action_decline_offer(self):
    self.status = 'refused'
    if all(self.property_id.offer_ids.mapped('status')):
      self.property_id.write({
        'selling_price': 0,
        'state': 'received'
      })



  # def write(self, vals):
  #   print(vals)
  #   # ORM SEARCH
  #   # res_partner_ids = self.env['res.partner'].search([
  #   #   ('is_company', '=', True)
  #   # ])
  #   # ORM BROWSE
  #   # res_partner_ids = self.env['res.partner'].browse(2)
  #   # ORM SERACH MAPPED
  #   res_partner_ids = self.env['res.partner'].search([
  #     ('is_company', '=', True)
  #   ]).mapped() # return nya berupa list/array
  #   res_partner_ids = self.env['res.partner'].search([
  #     ('is_company', '=', True)
  #   ]).filtered(lambda x: x.phone == '') 
    
  #   print(res_partner_ids.name)
  #   return super(PropertyOffer, self).write(vals)

