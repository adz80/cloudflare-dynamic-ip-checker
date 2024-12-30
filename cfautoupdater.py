import datetime
import json
import logging
import os
import smtplib
import time
import requests
import logging


# Check for required environment variables
required_env_vars = ['CF_ZONE_ID', 'CF_BEARER_TOKEN', 'CF_RECORD']
for var in required_env_vars:
    if var not in os.environ:
        print(f"Error: {var} environment variable is not set")
        exit(1)

# Load environment variables
cf_zone_id = os.environ['CF_ZONE_ID']
cf_bearer_token = os.environ['CF_BEARER_TOKEN']
cf_record = os.environ['CF_RECORD']

# Optional environment variables with default values


interval = int(os.environ.get('INTERVAL', 12))  # default to 12 hours
email = os.environ.get('EMAIL', 'nobody@nobody.com')
smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
smtp_port = int(os.environ.get('SMTP_PORT', 587))
smtp_username = os.environ.get('SMTP_USERNAME', 'default-username')
smtp_password = os.environ.get('SMTP_PASSWORD', '')
log_file = os.environ.get('LOG_FILE', 'ipchanges.log')
send_email = os.environ.get('SEND_EMAIL', 'False')
logging_level = os.environ.get('LOGGING_LEVEL', 'INFO').upper()


def main():
    # Setting up the logger (a file where it records all IP changes)
    # Colourful logging
    logging.basicConfig(
        level=logging_level, 
        format='%(asctime)s :: \033[94m%(levelname)s\033[0m :: \033[92m%(message)s\033[0m',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # The headers we want to use
    headers = {
        "Authorization": f"Bearer {cf_bearer_token}", 
        "content-type": "application/json"
        }

    while True:
        # Get the initial data of your A Record
        cf_record_id = extract_record_id(cf_record, cf_zone_id, headers)
        a_record_url = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/dns_records/{cf_record_id}", headers=headers)
        log_request_response(a_record_url)
        
        if a_record_url.status_code != 200:
            logging.error(f"Cloudflare API returned {a_record_url.status_code} at {datetime.datetime.now().isoformat()}")
            time.sleep(600)
            continue

        arecordjson = a_record_url.json()
        current_set_ip = arecordjson['result']['content']

        try:
            currentip = requests.get("https://api.ipify.org?format=json")
            currentip.raise_for_status()
            currentactualip = currentip.json()['ip']
        except requests.RequestException as e:
            logging.error(f"Failed to get current IP: {e}")
            time.sleep(600)
            continue

        if currentactualip != current_set_ip:
            payload = {"content": currentactualip}
            response = requests.patch(
                f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/dns_records/{cf_record_id}",
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logging.info(f"{now} - IP change from {current_set_ip} to {currentactualip}")
                if send_email.lower() == 'true':
                    send_email_notification(current_set_ip, currentactualip)
            else:
                logging.error(f"Failed to update IP address: {response.status_code} - {response.text}")
        
        logging.info(f"{datetime.datetime.now().isoformat()} - IP is up to date")
        logging.info(f"Sleeping for {interval} hours")
        time.sleep(interval * 3600)

            

def send_email_notification(current_set_ip, currentactualip):
    """
    Send an email notification with the IP change.

    This function sends an email notification from the EMAIL environment variable to the same address
    with the subject "DNS IP Updated" and the message body containing the IP change.

    The function relies on the following environment variables being set:

    - EMAIL: the sender's email address
    - SMTP_SERVER: the SMTP server to use
    - SMTP_PORT: the SMTP port to use
    - SMTP_USERNAME: the SMTP username to use
    - SMTP_PASSWORD: the SMTP password to use

    If any of these variables are not set, the function does nothing.

    :param current_set_ip: the IP address currently set in the DNS record
    :param currentactualip: the current actual IP address
    """
    if all(key in os.environ for key in ['EMAIL', 'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']):
        sender = os.environ['EMAIL']
        receivers = [os.environ['EMAIL']]

        message = f"""From: Server <{sender}>
        To: Your email <{receivers[0]}>
        Subject: DNS IP Updated

        The server's IP has changed from {current_set_ip} to {currentactualip}.

        The DNS records have been updated.
        """

        with smtplib.SMTP(os.environ['SMTP_SERVER'], port=int(os.environ['SMTP_PORT'])) as smtpObj:
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(os.environ['SMTP_USERNAME'], os.environ['SMTP_PASSWORD'])
            smtpObj.sendmail(sender, receivers, message)

def log_request_response(response):
    logging.debug('Request Headers:')
    try:
        logging.debug(json.dumps(dict(response.request.headers), indent=2))
    except Exception as e:
        logging.debug(f"Failed to log request headers: {e}")

    logging.debug('Response Headers:')
    try:
        logging.debug(json.dumps(dict(response.headers), indent=2))
    except Exception as e:
        logging.debug(f"Failed to log response headers: {e}")

    logging.debug('Response Payload:')
    try:
        logging.debug(json.dumps(response.json(), indent=2))
    except ValueError:
        logging.debug(response.text)

def extract_record_id(domain, cf_zone_id, headers):
    """
    Extracts the ID of a DNS record for a given domain and Cloudflare zone.

    Parameters
    ----------
    domain : str
        The domain name of the DNS record to extract.
    cf_zone_id : str
        The ID of the Cloudflare zone containing the DNS record.
    headers : dict
        The headers to use for the request, including the API token.

    Returns
    -------
    str or None
        The ID of the DNS record if found, otherwise None.
    """
    response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/dns_records", headers=headers)
    log_request_response(response)
    records = response.json()['result']
    for record in records:
        if record['name'] == domain:
            return record['id']
    return None



if __name__ == "__main__":
    main()
