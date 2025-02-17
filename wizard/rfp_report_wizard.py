from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import base64
import xlsxwriter
from datetime import datetime, time  # Corrected import

class RFPReportWizard(models.TransientModel):
    _name = 'report.rfp.wizard'
    _description = 'RFP Report Wizard'

    supplier_id = fields.Many2one('res.partner', string="Supplier", required=True, domain=[('supplier_rank', '>', 0)])
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    logo = fields.Binary(string="Company Logo")
    excel_report = fields.Binary(string="Excel Report")  # Added field to store the report
    html_preview = fields.Html(string="HTML Preview", readonly=True)

    def _validate_inputs(self):
        """ Validates form inputs before generating the report """
        if self.start_date > self.end_date:
            raise UserError(_("Start date must be earlier than or equal to the end date."))

        approved_rfps = self.env['procurement_management.rfp'].search([
            ('approved_supplier', '=', self.supplier_id.id),
            ('required_date', '>=', self.start_date),
            ('required_date', '<=', self.end_date),
            ('status', '=', 'accepted')
        ])

        if not approved_rfps:
            raise UserError(_("No accepted RFPs found for this supplier within the given date range."))

        if not self.env.company.logo:
            raise UserError(_("The current company does not have a logo. Please upload a logo."))

        return approved_rfps

    def action_generate_excel_report(self):
        # Validation: date range
        if self.start_date > self.end_date:
            raise UserError(_('Start date must be earlier than or equal to End date.'))

        # Search for accepted RFPs in "procurement.management.rfp"
        RFP = self.env['procurement_management.rfp']
        accepted_rfps = RFP.search([
            ('approved_supplier', '=', self.supplier_id.id),
            ('status', '=', 'accepted'),
            ('required_date', '>=', self.start_date),
            ('required_date', '<=', self.end_date)
        ])
        print("accepted rfps",accepted_rfps)
        if not accepted_rfps:
            raise UserError(_('The selected supplier has no accepted RFPs.'))

        # Get current company and check logo availability
        company = self.env.user.company_id
        if not company.logo:
            raise UserError(_('Current company does not have a logo.'))

        # Create the Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('RFP Report')

        # Set column widths for better display
        worksheet.set_column('A:A', 20)  # For RFP Number or Product
        worksheet.set_column('B:B', 20)  # For dates or quantities
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)

        # Define common formats
        title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'left', 'font_color': '#4F81BD'})
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': '#FFFFFF',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        text_format = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
        total_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        self.logo = company.logo

        # --- Section 1: Company Logo and Supplier Information ---
        # Save the company logo to a temporary file and insert with resizing options
        logo_path = '/tmp/company_logo.png'
        with open(logo_path, 'wb') as f:
            f.write(base64.b64decode(self.logo))
        worksheet.insert_image('A1', logo_path, {'x_scale': 0.2, 'y_scale': 0.1})

        # Display supplier name in title style (starting at cell C1)
        worksheet.merge_range('C1:E1', self.supplier_id.name, title_format)

        # Supplier details table (starting at row 2)
        supplier_info = [
            ['Email', self.supplier_id.email or ''],
            ['Phone', self.supplier_id.phone or ''],
            ['Address', self.supplier_id.contact_address or ''],
            ['TIN', self.supplier_id.vat or ''],
            # Extend with bank details if available:
            ['Bank Name', self.supplier_id.bank_ids and self.supplier_id.bank_ids[0].bank_id.name or ''],
            ['Account Name', self.supplier_id.bank_ids and self.supplier_id.bank_ids[0].acc_number or ''],
        ]
        row = 2
        for label, value in supplier_info:
            worksheet.write(row, 2, label, header_format)
            worksheet.write(row, 3, value, text_format)
            row += 1

        # --- Section 2: Table of Approved RFPs ---
        row += 2  # space between sections
        worksheet.write(row, 0, 'RFP Number', header_format)
        worksheet.write(row, 1, 'Date', header_format)
        worksheet.write(row, 2, 'Required Date', header_format)
        worksheet.write(row, 3, 'Total Amount', header_format)
        row += 1

        net_total = 0.0
        for rfp in accepted_rfps:
            # RFP Number
            worksheet.write(row, 0, rfp.rfp_id_seq, text_format)

            # Use create_date as RFP date; ensure it's a datetime object
            if rfp.create_date:
                rfp_date = fields.Datetime.from_string(rfp.create_date) if isinstance(rfp.create_date, str) else rfp.create_date
                worksheet.write_datetime(row, 1, rfp_date, date_format)
            else:
                worksheet.write(row, 1, '', text_format)

            # Convert required_date (a date) to a datetime for proper formatting
            if rfp.required_date:
                req_date = datetime.combine(rfp.required_date, time.min)  # Use `time.min`
                worksheet.write_datetime(row, 2, req_date, date_format)
            else:
                worksheet.write(row, 2, '', text_format)

            # Total Amount
            worksheet.write(row, 3, rfp.total_amount, money_format)
            net_total += rfp.total_amount
            row += 1

        # Write Net Total row
        worksheet.write(row, 2, 'Net Total', total_format)
        worksheet.write(row, 3, net_total, total_format)

        # --- Section 3: Grouped Product Lines ---
        row += 2
        worksheet.write(row, 0, 'Product', header_format)
        worksheet.write(row, 1, 'Quantity', header_format)
        worksheet.write(row, 2, 'Unit Price', header_format)
        worksheet.write(row, 3, 'Delivery Charge', header_format)
        worksheet.write(row, 4, 'Subtotal', header_format)
        row += 1

        product_groups = {}

        for rfp in accepted_rfps:
            accepted_rfq = self.env['purchase.order'].search([
                ('rfp_id', '=', rfp.id),
                ('state', '=', 'purchase')  # Assuming 'purchase' means the RFQ is accepted
            ], limit=1)  # Assuming 'purchase' means accepted
            print("accepted rfq",accepted_rfq)

            if accepted_rfq:
                for line in accepted_rfq.order_line:
                    product = line.product_id.name
                    if product not in product_groups:
                        product_groups[product] = {
                            'product_qty': 0,
                            'unit_price': 0,
                            'delivery_charge': 0,
                            'subtotal_price': 0,
                        }
                    product_groups[product]['product_qty'] += line.product_qty  # Use correct quantity field from RFQ line
                    product_groups[product]['unit_price'] += line.price_unit  # Unit price from RFQ line
                    product_groups[product]['delivery_charge'] += line.delivery_charge or 0  # Assuming this field exists
                    product_groups[product]['subtotal_price'] += line.price_total  # Subtotal price from RFQ line

        total_product_total = 0.0
        for product, values in product_groups.items():
            worksheet.write(row, 0, product, text_format)
            worksheet.write(row, 1, values['product_qty'], text_format)
            worksheet.write(row, 2, values['unit_price'], money_format)
            worksheet.write(row, 3, values['delivery_charge'], money_format)
            worksheet.write(row, 4, values['subtotal_price'], money_format)
            total_product_total += values['subtotal_price']
            row += 1

        worksheet.write(row, 3, 'Total', total_format)
        worksheet.write(row, 4, total_product_total, total_format)

        # --- Section 4: Current Company Contact Information ---
        row += 3
        worksheet.write(row, 0, 'Company Email', header_format)
        worksheet.write(row, 1, company.email or '', text_format)
        row += 2

        worksheet.write(row, 0, 'Company Phone', header_format)
        worksheet.write(row, 1, company.phone or '', text_format)
        row += 2

        worksheet.write(row, 0, 'Company Address', header_format)
        worksheet.write(row, 1, company.street or '', text_format)

        # Finalize and close the workbook
        workbook.close()
        output.seek(0)
        excel_data = base64.b64encode(output.read())

        self.excel_report = excel_data

        # Optionally, store or serve the file; here we return an action to trigger a download:
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s/%s?download=true' % (self._name, self.id, 'excel_report'),
            'target': 'self',
        }

    def action_generate_html_preview(self):
        approved_rfps = self._validate_inputs()

        company = self.env.company
        logo = company.logo and f"data:image/png;base64,{company.logo.decode()}" or ''

        # Start HTML report content with company logo
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{logo}" alt="Company Logo" style="height: 80px;"/>
                <h2 style="color: #4F81BD;">RFP Report for {self.supplier_id.name}</h2>
                <p><strong>Date Range:</strong> {self.start_date.strftime('%d-%m-%Y')} to {self.end_date.strftime('%d-%m-%Y')}</p>
                <p><strong>Company:</strong> {company.name} | <strong>Email:</strong> {company.email or 'N/A'} | <strong>Phone:</strong> {company.phone or 'N/A'}</p>
            </div>

            <h3 style="background-color: #4F81BD; color: white; padding: 5px;">Approved RFPs</h3>
            <table border="1" cellpadding="5" cellspacing="0" width="100%" style="border-collapse: collapse;">
                <tr style="background-color: #D9E1F2; text-align: center;">
                    <th>RFP Number</th>
                    <th>Date</th>
                    <th>Required Date</th>
                    <th>Total Amount</th>
                </tr>
        """

        net_total = 0.0
        for rfp in approved_rfps:
            rfp_date = rfp.create_date.strftime('%d-%m-%Y') if rfp.create_date else ''
            req_date = rfp.required_date.strftime('%d-%m-%Y') if rfp.required_date else ''
            total_amount = "{:,.2f}".format(rfp.total_amount)
            net_total += rfp.total_amount

            html_content += f"""
                <tr style="text-align: center;">
                    <td>{rfp.rfp_id_seq}</td>
                    <td>{rfp_date}</td>
                    <td>{req_date}</td>
                    <td>{total_amount}</td>
                </tr>
            """

        html_content += f"""
            <tr style="background-color: #D9E1F2; font-weight: bold; text-align: right;">
                <td colspan="3">Net Total</td>
                <td>{net_total:,.2f}</td>
            </tr>
            </table>
            <br/>
        """

        # Product Summary Section
        html_content += """
            <h3 style="background-color: #4F81BD; color: white; padding: 5px;">Grouped Product Summary</h3>
            <table border="1" cellpadding="5" cellspacing="0" width="100%" style="border-collapse: collapse;">
                <tr style="background-color: #D9E1F2; text-align: center;">
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Delivery Charge</th>
                    <th>Subtotal</th>
                </tr>
        """

        product_groups = {}
        for rfp in approved_rfps:
            accepted_rfq = self.env['purchase.order'].search([
                ('rfp_id', '=', rfp.id),
                ('state', '=', 'purchase')
            ], limit=1)

            if accepted_rfq:
                for line in accepted_rfq.order_line:
                    product = line.product_id.name
                    if product not in product_groups:
                        product_groups[product] = {
                            'product_qty': 0,
                            'unit_price': 0,
                            'delivery_charge': 0,
                            'subtotal_price': 0,
                        }
                    product_groups[product]['product_qty'] += line.product_qty
                    product_groups[product]['unit_price'] += line.price_unit
                    product_groups[product]['delivery_charge'] += line.delivery_charge or 0
                    product_groups[product]['subtotal_price'] += line.price_total

        total_product_total = 0.0
        for product, values in product_groups.items():
            total_product_total += values['subtotal_price']
            html_content += f"""
                <tr style="text-align: center;">
                    <td>{product}</td>
                    <td>{values['product_qty']}</td>
                    <td>{values['unit_price']:,.2f}</td>
                    <td>{values['delivery_charge']:,.2f}</td>
                    <td>{values['subtotal_price']:,.2f}</td>
                </tr>
            """

        html_content += f"""
            <tr style="background-color: #D9E1F2; font-weight: bold; text-align: right;">
                <td colspan="4">Total</td>
                <td>{total_product_total:,.2f}</td>
            </tr>
            </table>
        </div>
        """

        self.html_preview = html_content
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

