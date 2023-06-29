import string
def open_template(template_path):
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return string.Template(f.read())
    except FileNotFoundError as e:
        print('Skip - Maybe there is no template of email/sms corresponding to the product-type of requested data.')
