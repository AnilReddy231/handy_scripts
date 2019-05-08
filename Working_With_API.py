import requests
import json
import argparse
import sys
import logging, csv
from time import time, sleep


class APIWrapper:
    def __init__(self, target, bearer):
        self.target = target
        self.headers = {
            'Authorization': f'Bearer {bearer}',
            'Content-Type': 'application/json'
        }

    def post(self, path, data, flush_auth=False):
        """
        POST method for requesting information from an OpsMan endpoint.
        :param target: The Marketo API endpoint.
        :param data: Dictionary of data to be passed as the body of the request.
        :param flush_auth: If set to True will flush the Authorization header.
        :return: Returns the response in text or json as well as a status message if successful. False, False if not.
        """
        if flush_auth is True:
            del self.headers['Authorization']

        try:
            response = requests.post(f'{self.target}{path}', headers=self.headers, data=json.dumps(data), verify=False)
            status = response.status_code

            try:
                return response.json(), status
            except json.decoder.JSONDecodeError:
                return response.text, status

        except requests.exceptions.ConnectionError:
            return False, False

    def get(self, path, flush_auth=False):
        """
        GET method for requesting information from an OpsMan endpoint.
        :param: target: The Marketo API endpoint.
        :return: Returns the response in text or json as well as a status message if successful. False, False if not.
        """
        if flush_auth is True:
            del self.headers['Authorization']

        try:
            response = requests.get(f'{self.target}{path}', headers=self.headers, verify=False)
            status = response.status_code

            try:
                return response.json(), status
            except json.decoder.JSONDecodeError:
                return response.text, status

        except requests.exceptions.ConnectionError:
            return False, False

    def get_access_token(self, c_id, secret, path=None, flush_auth=False):
        access_data = {"client_id": c_id, "client_secret": secret, "grant_type": "client_credentials"}
        if flush_auth is True:
            del self.headers['Authorization']

        try:
            response = requests.get(f'{self.target}{path}', params=access_data, headers=self.headers, verify=False)
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError:
            return False, False

    def create_job(self):
        logging.info("Creating Job")
        path = "bulk/v1/leads/export/create.json"
        data = {
               "fields": [
                  "firstName",
                  "lastName"
               ],
               "format": "CSV",
               "columnHeaderNames": {
                  "firstName": "First Name",
                  "lastName": "Last Name"
               },
               "filter": {
                  "createdAt": {
                     "startAt": "2019-03-15T00:00:00Z",
                     "endAt": "2019-4-15T00:00:00Z"
                  }
               }
            }
        response, status= self.post(path, data)

        if status == 200:
            return response["result"][0]["exportId"]
        else:
            return None

    def start_job(self, export_id):
        logging.info(f"Starting Job : {export_id}")
        path = f"bulk/v1/leads/export/{export_id}/enqueue.json"
        response, status = self.post(path, None)

        if status == 200:
            return response["result"][0]["status"]
        else:
            return None

    def check_status(self, export_id):
        logging.info (f"Checking status of Job Id: {export_id}")
        path = f"bulk/v1/leads/export/{export_id}/status.json"
        state = "Created"
        n = 600  # seconds

        start = time()
        while time() - start < n:
            response, status = self.get(path)
            state = response["result"][0]["status"]
            logging.info(f"Status of Job Id:{export_id} is: {state}")
            if state == "Completed":
                break
            sleep(15)

        if status == 200:
            return state
        else:
            return None

    def retrieve_data(self,export_id):
        logging.info (f"Retrieving results of Job Id: {export_id}")
        path = f"bulk/v1/leads/export/{export_id}/file.json"
        response = requests.get(f'{self.target}{path}', headers=self.headers, verify=False)
        status = response.status_code
        if status == 200:
            data = response.text
            with open ('output.csv', "w") as csvFile:
                csvFile.write(data)

            logging.info("Please find the results at outputs.csv")
        else:
            logging.error("Probably Job: {export_id} hadn't been completed or not Found, please check its status")


def main(parsed):
    base_url = "https://071-JJS-314.mktorest.com/"
    ref = APIWrapper(base_url, None)
    response, status = ref.get_access_token(parsed.c_id, parsed.c_secret, 'identity/oauth/token', flush_auth=True)

    if status == 200:
        logging.info("Got the Authentication token from Marketo ")
        ref.headers["Authorization"] = f"Bearer {response['access_token']}"
    else:
        logging.error('Could not authenticate with Marketo!')
        exit(1)

    export_id = ref.create_job()
    logging.info(f"Job created with export_id: {export_id}")

    status = ref.start_job(export_id)

    if status is not None:
        logging.info(f"Job Id: {export_id} is currently {status}")
    else:
        logging.error(f"Failed to start Export_Id: {export_id}")

    job_status = ref.check_status(export_id)

    if job_status == "Completed":
        logging.info(f"{export_id} had been {job_status}")
        ref.retrieve_data(export_id)
    else:
        logging.error(f"{export_id} had failed to complete in 5 minutes")


def arg_parse(*args, **kwargs):
    parser = argparse.ArgumentParser(
        description="Program to work with Marketo Bulk Extract API",
        prog=sys.argv[0],
    )

    parser.add_argument (
        "-cid", "--client-id",
        action='store',
        help="Client Id",
        dest='c_id'
    )

    parser.add_argument (
        "-secret", "--client-secret",
        action='store',
        help="Client Secret",
        dest='c_secret'
    )

    parsed = parser.parse_args()
    main(parsed)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    sys.exit(arg_parse(*sys.argv))
