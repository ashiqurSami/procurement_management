from odoo import api,fields,models

class RejectBlacklistWizard(models.TransientModel):
    _name="reject.blacklist.wizard"
    _description = "Reject Blacklist Wizard"

    comments = fields.Text(string="Reason", required=True)

    def action_confirm(self):
        supplier_id=self.env.context.get('active_id')
        supplier=self.env['procurement_management.supplier.registration'].browse(supplier_id)

        if self.env.context.get('blacklisted'):
            #blacklisting the supplier mail
            self.env['mail.blacklist'].create({
                'email': supplier.email,
            })

            #update the supplier state to blacklisted and store the reason
            supplier.write({
                'state' : 'blacklisted',
                'comments' : self.comments
            })

        elif self.env.context.get('rejected'):
            supplier.write({
                'state' : 'rejected',
                'comments' : self.comments
            })