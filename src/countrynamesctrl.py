import web
from aux import logger_instance, debug_mode
from api import json, json_response, api_response, build_params
from errors import Error, NOTALLOWED, NORESULT
from models import Country, results_to_countries

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class CountrynameController(object):
    """Handle country names queries"""

    @json_response
    @api_response
    @check_token
    def GET(self, name):
        raise Error(NOTALLOWED)

    def POST(self, name):
        """Add a name to an existing country"""
        logger.debug("Data: %s" % (web.data()))

        data           = json.loads(web.data())
        country_id     = data.get('country_id')
        country_name   = data.get('country_name')

        try:
            assert country_id and country_name
        except AssertionError as error:
            logger.debug(error)
            m = "You must provide a country_id and a country_name"
            raise Error(BADPARAMS, msg=m)

        try:
            record = Country.get_from_country_id(country_id)
            assert record
            country = result_to_country(record)
        except AssertionError:
            raise Error(BADPARAMS, msg="Unknown country '%s'" % (country_id))
        country.country_name.append(country_name)
        country.save()

        return [country.__dict__]

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        """Delete a country name"""
        logger.debug("Data: %s" % (web.data()))

        data           = json.loads(web.data())
        country_id     = data.get('country_id')
        country_name   = data.get('country_name')

        try:
            assert country_id and country_name
        except AssertionError as error:
            logger.debug(error)
            m = "You must provide a country_id and a country_name"
            raise Error(BADPARAMS, msg=m)

        try:
            record = Country.get_from_country_id(country_id)
            assert record
            country = result_to_country(record)
        except AssertionError:
            raise Error(BADPARAMS, msg="Unknown country '%s'" % (country_id))

        Country.delete_name(country_name)
        country['country_name'].remove(country_name)

        return [country.__dict__]

    @json_response
    def OPTIONS(self, name):
        return
