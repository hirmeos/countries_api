import web
from aux import logger_instance, debug_mode
from api import json_response, api_response, check_token, build_params
from errors import Error, NOTALLOWED, NORESULT
from models import Country, results_to_countries

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class CountryController(object):
    """Handle country queries"""

    @json_response
    @api_response
    @check_token
    def GET(self, name):
        """List a country if country_id provided otherwise list all"""
        logger.debug("Query: %s" % (web.input()))

        country_id = web.input().get('country_id')
        country_name = web.input().get('country_name')

        if country_id:
            results = Country.get_from_country_id(country_id)
        elif country_name:
            results = Country.get_from_name(country_name)
        else:
            filters = web.input().get('filter')
            clause, params = build_params(filters)
            results = Country.get_all(clause, params)

        if not results:
            raise Error(NORESULT)

        return results_to_countries(results)

    def POST(self, name):
        raise Error(NOTALLOWED)

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)

    @json_response
    def OPTIONS(self, name):
        return
