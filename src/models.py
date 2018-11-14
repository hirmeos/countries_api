import psycopg2
from aux import logger_instance
from api import db
from errors import Error, FATAL

logger = logger_instance(__name__)


class Country(object):
    """API authentication accounts"""
    def __init__(self, country_id, country_code, continent={}, names=[]):
        self.country_id     = country_id
        self.country_code   = country_code
        self.country_name   = names if names else self.get_names()
        self.continent      = continent if continent else self.get_continent()

    def save(self):
        try:
            with db.transaction():
                options = dict(country_id=self.country_id,
                               country_code=self.country_code,
                               continent_code=self.continent['continent_code'])
                q = '''INSERT INTO country (country_id, country_code,
                                            continent_code)
                       VALUES ($country_id, $country_code, $continent_code)
                       ON CONFLICT DO NOTHING'''
                db.query(q, options)
                assert self.exists()

                for name in self.country_name:
                    q = '''INSERT INTO country_name (country_name, country_id)
                           VALUES ($name, $cid) ON CONFLICT DO NOTHING'''
                    db.query(q, dict(name=name, cid=self.country_id))
        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(error)
            raise Error(FATAL)

    def exists(self):
        try:
            options = dict(cid=self.country_id)
            result = db.select('country', options, where="country_id = $cid")
            return result.first()["country_id"] == self.country_id
        except BaseException:
            return False

    def get_continent(self):
        q = '''SELECT continent_code, continent_name
               FROM continent INNER JOIN country USING(continent_code)
               WHERE country_id = $cid'''
        result = db.query(q, dict(cid=self.country_id)).first()
        return dict(continent_code=result['continent_code'],
                    continent_name=result['continent_name'])

    def get_names(self):
        options = dict(cid=self.country_id)
        names = db.select('country_name', options,
                          what="country_name", where="country_id = $cid")
        return [(x["country_name"]) for x in names]

    @staticmethod
    def get_from_country_id(country_id):
        params = dict(country_id=country_id)
        clause = "AND country_id = $country_id"
        return Country.get_all(clause, params)

    @staticmethod
    def get_from_name(country_name):
        # we first get the country_id from the name and then query all using
        # the id - otherwise we miss other names of the same country
        country_id = db.select('country_name', dict(name=country_name),
                               what="country_id", where="country_name = $name")
        params = dict(country_id=country_id.first()["country_id"])
        clause = "AND country_id = $country_id"
        return Country.get_all(clause, params)

    @staticmethod
    def get_all(clause, params):
        try:
            q = '''SELECT *
                   FROM country INNER JOIN country_name USING(country_id)
                      INNER JOIN continent USING(continent_code)
                   WHERE 1=1 ''' + clause + '''
                   ORDER BY country_id;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)


def result_to_country(r):
    continent = dict(continent_code=r["continent_code"],
                     continent_name=r["continent_name"])
    return Country(r["country_id"], r["country_code"],
                   continent, r["country_name"])


def results_to_countries(results):
    data  = []  # output
    names = []  # temporary array of country names
    last  = len(results) - 1  # last index

    i = 0
    for e in results:
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = e
        if e["country_id"] != cur["country_id"]:
            cur["country_name"] = names
            country = result_to_country(cur)
            data.append(country.__dict__)
            names = []
            cur = e

        if e["country_name"] not in names:
            names.append(e["country_name"])

        if i == last:
            cur["country_name"] = names
            country = result_to_country(cur)
            data.append(country.__dict__)
        i += 1
    return data
