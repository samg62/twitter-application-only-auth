import sys
import base64
import json


try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError


API_ENDPOINT = 'https://api.twitter.com'
API_VERSION = '1.1'
REQUEST_TOKEN_URL =  '%s/oauth2/token' % API_ENDPOINT
REQUEST_RATE_LIMIT = '%s/%s/application/rate_limit_status.json' % (API_ENDPOINT, API_VERSION)


class ClientException(Exception):
    pass


class Client(object):
    """This class implements the Twitter's Application-only authentication."""

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = ''

    def request(self, url):
        """Send an authenticated request to the Twitter API."""
        if not self.access_token:
            self.access_token = self._get_access_token()

        request = Request(url)
        request.add_header('Authorization', 'Bearer %s' % self.access_token)
        try:
            response = urlopen(request)
        except HTTPError:
            raise ClientException

        return response.read()

    def rate_limit_status(self):
        """Returns a dict of rate limits by resource."""
        json_response = self.request(REQUEST_RATE_LIMIT)
        return json.loads(json_response.decode('utf-8'))

    def _get_access_token(self):
        """Obtain a bearer token."""
        bearer_token = '%s:%s' % (self.consumer_key, self.consumer_secret)
        encoded_bearer_token = base64.b64encode(bearer_token.encode('ascii'))
        request = Request(REQUEST_TOKEN_URL)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
        request.add_header('Authorization', 'Basic %s' % encoded_bearer_token.decode('utf-8'))
        request.add_data('grant_type=client_credentials'.encode('ascii'))

        response = urlopen(request)
        raw_data = response.read().decode('utf-8')
        data = json.loads(raw_data)
        return data['access_token']
