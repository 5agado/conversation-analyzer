import requests
import logging
import sys

class BluemixClient:
    def __init__(self, username, password, serviceUrl, useToken=False):
        self._username = username
        self._password = password
        self._useToken = useToken
        if useToken:
            self._token = getAuthToken(username, password, serviceUrl)

    def request(self, url, data):
        headers={"accept": "application/json",
                 "content-type": "text/html; charset=UTF-8",
                 "X-Watson-Learning-Opt-Out": "true"} #If not specified in all payload data,
                                                    # data is collected and used to improve Bluemix.

        if self._useToken:
            auth = {}
            headers["X-Watson-Authorization-Token"] = self._token
        else:
            auth=(self._username, self._password)

        resp = requests.post(url, auth=auth, headers=headers, data=data)

        if resp.status_code != 200:
            logging.error('Request error. Response code: {}'.format(resp.status_code))

        logging.info('Output from server: {}'.format(resp.text))
        return resp.text

def getAuthToken(username, password, urlParam):
    AUTH_URL = "https://gateway.watsonplatform.net/authorization/api/v2/token"
    resp = requests.get(AUTH_URL, auth=(username, password), params={"url": urlParam},
                        headers={"accept": "application/json"})

    if resp.status_code != 200:
        logging.error('Bluemix authentication error. Response code: {}'.format(resp.status_code))
        raise Exception("Authentication Error")

    token = resp.json()["token"]
    logging.info('Bluemix authentication success. Auth token: {}'.format(token))
    return token
