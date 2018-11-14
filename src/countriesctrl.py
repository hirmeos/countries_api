import web
from aux import logger_instance, debug_mode
from api import json, json_response, api_response, build_params
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

        try:
            assert results
            countries = results_to_countries(results)
            assert countries
        except AssertionError:
            raise Error(NORESULT)

        return countries

    def POST(self, name):
        """Create a country"""
        logger.debug("Data: %s" % (web.data()))

        data           = json.loads(web.data())
        country_id     = data.get('country_id')
        country_code   = data.get('country_code')
        country_name   = data.get('country_name')
        continent_code = data.get('continent_code')

        try:
            country_name = strtolist(country_name)
            assert country_id and country_name and country_code \
            and continent_code
        except AssertionError as error:
            logger.debug(error)
            m = "You must provide a (country_id, country_code"
                ", a continent_code, and at least one country_name"
            raise Error(BADPARAMS, msg=m)

        continent = {continent_code=continent_code}
        country = Country(country_id, country_code, continent, country_name)
        country.save()
        # now we get the record from db to make sure it's been inserted
        # and reload continent information
        record = Country.get_from_country_id(country_id)
        assert record
        return results_to_countries(record)

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)

    @json_response
    def OPTIONS(self, name):
        return
