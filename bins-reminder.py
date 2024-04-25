import os
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage

import requests

POSTCODE = os.environ["POSTCODE"]
ADDRESS_LINE = os.environ["ADDRESS_LINE"]
TARGET_EMAIL = os.environ["TARGET_EMAIL"]
SMTP_EMAIL = os.environ["SMTP_EMAIL"]
SMTP_TOKEN = os.environ["SMTP_TOKEN"]

API_URL = "https://api.reading.gov.uk"


def get_site_uprn_from_address():
    resp = requests.get(f"{API_URL}/rbc/getaddresses/{POSTCODE}", timeout=10)
    resp.raise_for_status()

    for address in resp.json()["Addresses"]:
        sanitised_address = address["SiteShortAddress"].split(POSTCODE)[0].replace(",", "")
        if ADDRESS_LINE in sanitised_address:
            return address["AccountSiteUprn"]


def get_next_collections(uprn):
    resp = requests.get(f"{API_URL}/rbc/mycollections/{uprn}", timeout=10)
    resp.raise_for_status()

    return resp.json()["Collections"]


def do_email_collections(collections):
    content = """\
According to RBC, the following bin collections are tomorrow:

{}
    
Make sure you put your bins out tonight.
    """.format(
        "\n".join([collection["Service"] for collection in collections])
    )

    message = EmailMessage()
    message["Subject"] = "Your bin collection is tomorrow"
    message["From"] = SMTP_EMAIL
    message["To"] = TARGET_EMAIL
    message.set_content(content)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as mail_server:
        mail_server.login(SMTP_EMAIL, SMTP_TOKEN)
        mail_server.send_message(message, SMTP_EMAIL, TARGET_EMAIL)


def _get_date_from_str(in_date):
    return datetime.strptime(in_date, "%d/%m/%Y %H:%M:%S")


def get_tomorrow_collections(collections):
    eligible_collections = []

    for collection in collections:
        collection_date = collection["Date"]
        parsed_date = _get_date_from_str(collection_date)

        if parsed_date > (datetime.today() - timedelta(days=1)):
            eligible_collections.append(collection)

    return eligible_collections


def main():
    uprn = get_site_uprn_from_address()
    collections = get_next_collections(uprn)
    eligible_collections = get_tomorrow_collections(collections)

    if len(eligible_collections) > 0:
        do_email_collections(collections)


if __name__ == "__main__":
    main()
