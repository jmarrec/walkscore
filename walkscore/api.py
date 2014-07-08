import urllib2
import urllib
try:
    import simplejson as json
except ImportError:
    import json

"""
Error handler
"""
class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(
            req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result

class InvalidApiKeyException(Exception):
    pass

class InvalidLatLongException(Exception):
    pass

class ExceedQuotaException(Exception):
    pass

class ScoreUnavailableException(Exception):
    pass

class InternalServerException(Exception):
    pass

"""
Your IP is blocked
"""
class IpBlockedException(Exception):
    pass

class WalkScore:
    apiUrl = 'http://api.walkscore.com/score?format'

    def __init__(self, apiKey, format = 'json'):
        self.apiKey = apiKey
        self.format = format

    def makeRequest(self, address, lat = '', long = ''):
        url = '%s=%s&%s&lat=%s&lon=%s&wsapikey=%s' % (self.apiUrl, self.format, urllib.urlencode({'address': address}), lat, long, self.apiKey)
        request = urllib2.Request(url)
        opener = urllib2.build_opener(DefaultErrorHandler())
        first = opener.open(request)

        first_datastream = first.read()

        # Append caching headers
        request.add_header('If-None-Match', first.headers.get('ETag'))
        request.add_header('If-Modified-Since', first.headers.get('Date'))

        response = opener.open(request)

        # some error handling
        responseStatusCode = response.getcode()

        # jsonify response
        jsonResp = json.load(response)
        jsonRespStatusCode = jsonResp['status']

        # Error handling
        # @see http://www.walkscore.com/professional/api.php
        if responseStatusCode == 200 and jsonRespStatusCode == 40:
            raise InvalidApiKeyException

        if responseStatusCode == 200 and jsonRespStatusCode == 2:
            raise ScoreUnavailableException

        if responseStatusCode == 200 and jsonRespStatusCode == 41:
            raise ExceedQuotaException

        if responseStatusCode == 403 and jsonRespStatusCode == 42:
            raise IpBlockedException

        if responseStatusCode == 404 and jsonRespStatusCode == 30:
            raise InvalidLatLongException

        if responseStatusCode == 500 and jsonRespStatusCode == 31:
            raise InternalServerException

        return jsonResp