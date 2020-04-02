# coding=utf-8

import csv
from erppeek import Client
import logging

FILE_INPUT_PATH = 'account.invoice.csv'

ODOO_URL = '---'
ODOO_DB = '---'
ODOO_ACCOUNT = {'user': 'import_invoice', 'pwd': ''}

# setting erppeek
client = Client(ODOO_URL,
                db=ODOO_DB,
                user=ODOO_ACCOUNT['user'],
                password=ODOO_ACCOUNT['pwd'])

partner = client.ResPartner
invoice = client.AccountInvoice
invoice_line = client.AccountInvoiceLine
template = client.ProductProduct
uom = client.ProductUom
pricelist = client.ProductPricelist
payment_term = client.AccountPaymentTerm
currency = client.ResCurrency
journal = client.AccountJournal
account = client.AccountAccount
fiscal_position = client.AccountFiscalPosition
company = client.ResCompany
tax = client.AccountTax

# opening the file with DictReader
file_input = open(FILE_INPUT_PATH, 'rb')
spamReader = csv.DictReader(file_input, delimiter=',', quotechar='"')

COMPANY = company.browse([('name', '=', 'XXX')])[0]
print("Company: " + COMPANY)

""" define if it is a SALE or PURCHASE"""
SETTINGS = 'sale' # set 'sale' or 'purchase'

# settings for sales
if SETTINGS == "sale":
    INV_LINE_TAX = 'NI 41/50'
    INV_ACCOUNT = account.browse([('code', '=', '150100'), ('company_id.id', '=', COMPANY.id)])[0]
    INV_LINE_ACCOUNT = account.browse([('code', '=', '310100'), ('company_id.id', '=', COMPANY.id)])[0]

# settings fpor purchases
if SETTINGS == "purchase":
    INV_LINE_TAX = 'NI 41/50'
    INV_TYPE = 'in_invoice'
    INV_ACCOUNT = account.browse([('code', '=', '250100'), ('company_id.id', '=', COMPANY.id)])[0]
    INV_LINE_ACCOUNT = account.browse([('code', '=', '410100'), ('company_id.id', '=', COMPANY.id)])[0]

def import_invoice():
    """
    import invoice from file csv
    """
    # for each line of the contact file provided by the client
    line_num = 0
    new_invoice_id = ""
    for row in spamReader:
        # if there is a new invoice,check if exist or create
        if len(row['internal_number']) > 2:
            existing_invoice = invoice.browse([
                ('internal_number', '=', row['internal_number']),
                ('company_id.id', '=', COMPANY.id)])
            if existing_invoice:
                print("Existing invoice: " + existing_invoice.internal_number)
                new_invoice_id = ""
                continue
            new_invoice_id = create_invoice(row)
            create_invoice_line(row, new_invoice_id)
        if len(row['internal_number']) < 2 and new_invoice_id != "":
            create_invoice_line(row, new_invoice_id)

        line_num += 1
        if line_num % 1 == 0:
            print(line_num)

def create_invoice(row):
    # setting the client and its values
    inv_client = partner.browse([('name', '=', row['partner_id'])])[0]
    inv_client.customer = True
    inv_client.company_id = ""

    # settings other main fields
    inv_payment_draft = payment_term.browse([('name', '=', row['payment_term'])])
    if inv_payment_draft:
        inv_payment_term = inv_payment_draft[0]
    else:
        inv_payment_term = ""
    inv_currency = currency.browse([('name', '=', row['currency_id'])])[0]
    inv_journal = journal.browse([('name', '=', row['journal_id']),
                                  ('company_id.id', '=', COMPANY.id)])[0]
    inv_fiscal_position = fiscal_position.browse([('name', '=', row['fiscal_position']),
                                                  ('company_id.id', '=', COMPANY.id)])[0]

    # TODO: what if the client does not exists?
    invoice_data = (
        {'partner_id': inv_client,
         'company_id': COMPANY,
         'date_due': row['date_due'],
         'intrastat': True,
         'internal_number': row['internal_number'],
         'date_invoice': row['date_invoice'],
         'payment_term': inv_payment_term,
         'currency_id': inv_currency,
         'journal_id': inv_journal,
         # 'pricelist_id': inv_journal,
         'account_id': INV_ACCOUNT,
         'fiscal_position': inv_fiscal_position,
         })

    if len(row['supplier_invoice_number']) > 2:
        invoice_data['supplier_invoice_number'] = row['supplier_invoice_number']
        invoice_data['type'] = 'in_invoice'

    new_invoice = invoice.create(invoice_data)
    print("New invoice: " + new_invoice.internal_number)
    return new_invoice

def create_invoice_line(row, invoice):
    # setting the product
    if len(row['invoice_line_product_id']) > 2:
        inv_product_draft = template.browse([('name', '=', row['invoice_line_product_id']),
                                             ('default_code', '=', row['product_id_code'])])
        if inv_product_draft:
            inv_product = inv_product_draft[0]
        else:
            inv_product = template.browse([('name', '=', row['invoice_line_product_id'])])[0]
        unit_measure = inv_product.uom_id
    else:
        inv_product = ""
        unit_measure = ""

    inv_tax = tax.browse([('description', '=', INV_LINE_TAX),
                          ('company_id.id', '=', COMPANY.id)])[0]
    invoice_line_data = ({
        'invoice_id': invoice,
        'product_id': inv_product,
        'name': row['description'],
        'quantity': row['quantity'],
        'account_id': INV_LINE_ACCOUNT,
        'uos_id': unit_measure,
        'price_unit': row['price_unit'],
        'invoice_line_tax_id': [4, inv_tax.id],
        })

    invoice_line.create(invoice_line_data)

def intercompany_products():
    for row in spamReader:
        reset_product = template.browse([
            ('name', '=', row['invoice_line_product_id']),
            ('default_code', '=', row['product_id_code'])])
        if reset_product:
            reset_product.company_id[0] = ""
            print("Resettato prodotto: " + reset_product.name)

def approve_instrastat():
    inv_to_calc = invoice.browse([
        ('internal_number', '=', 'ACFR20170001'),
        ('company_id.id', '=', COMPANY.id)])[0]
    print("Invoice: " + inv_to_calc.internal_number)
    _ = inv_to_calc.compute_intrastat_lines()
    return True

if __name__ == "__main__":
    print("Beginning...")
    print()
    import_invoice()
    print()

    logging.info("Finito")
