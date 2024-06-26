from parsons.etl import Table
import petl
import censusgeocode
import logging

logger = logging.getLogger(__name__)


# The size of batches to send to the batch geocode endpoint. Currently
# the recommendation is less than 1K records.
BATCH_SIZE = 999


class CensusGeocoder(object):
    """
    Instantiate the CensusGecoder Class

    `Args:`
        benchmark: str
            The US Census benchmark file to utilize. By default the current benchmark is used,
            but other options can found `here <https://geocoding.geo.census.gov/geocoder/benchmarks>`_.
        vintage: str
            The US Census vintage file to utilize. By default the current vintage is used, but
            other options can be found `here <https://geocoding.geo.census.gov/geocoder/vintages?form>`_.
    """  # noqa E501

    def __init__(self, benchmark="Public_AR_Current", vintage="Current_Current"):

        self.cg = censusgeocode.CensusGeocode(benchmark=benchmark, vintage=vintage)

    def geocode_onelineaddress(self, address, return_type="geographies"):
        """
        Geocode a single line address. Does not require parsing of city and zipcode field. Returns
        geocode as well as other census block data. If the service is unable to geocode the address
        it will return an empty list.

        `Args:`
            address: str
                A valid US address
            return_type: str
                ``geographies`` will return information about the Census geographies
                while ``locations`` will information about the address.
        `Returns`:
            dict
        """

        geo = self.cg.onelineaddress(address, returntype=return_type)
        self._log_result(geo)
        return geo

    def geocode_address(
        self,
        address_line,
        city=None,
        state=None,
        zipcode=None,
        return_type="geographies",
    ):
        """
        Geocode an address by specifying address fields. Returns the geocode as well as other
        census block data.

        `Args:`
            address_line: str
                A valid address line
            city: str
                A valid city
            state: str
                A valid two character state abbreviation (e.g. 'IL')
            zipcode: int
                A valid five digit zipcode (e.g. 60622)
            return_type: str
                ``geographies`` will return information about the Census geographies
                while ``locations`` will information about the address.
        `Returns:`
            dict
        """

        geo = self.cg.address(address_line, city=city, state=state, zipcode=zipcode)
        self._log_result(geo)
        return geo

    def geocode_address_batch(self, table):
        """
        Geocode multiple addresses from a parsons table.

        The table must **only** include the following columns in the following order.

        .. list-table::
            :widths: 40
            :header-rows: 1

            * - Column Names
            * - id (must be unique)
            * - street
            * - city
            * - state
            * - zip

        `Args:`
            table: Parsons Table
                A Parsons table
        `Returns:`
            A Parsons table
        """

        logger.info(f"Geocoding {table.num_rows} records.")
        if set(table.columns) != {"id", "street", "city", "state", "zip"}:
            msg = (
                "Table must ONLY include `['id', 'street', 'city', 'state', 'zip']` as"
                + "columns. Tip: try using `table.cut()`"
            )
            raise ValueError(msg)

        chunked_tables = table.chunk(BATCH_SIZE)
        batch_count = 1
        records_processed = 0

        geocoded_tbl = Table([[]])
        for tbl in chunked_tables:

            geocoded_tbl.concat(Table(petl.fromdicts(self.cg.addressbatch(tbl))))
            records_processed += tbl.num_rows
            logger.info(f"{records_processed} of {table.num_rows} records processed.")
            batch_count += 1

        return geocoded_tbl

    def _log_result(self, dict):
        # Internal method to log the result of the geocode

        if len(dict) == 0:
            logger.info("Unable to geocode record.")
        else:
            logger.info("Record geocoded.")

    def get_coordinates_data(self, latitude, longitude):
        """
        Return census data on coordinates.

        `Args`
            latitude: int
                A valid latitude in the United States
            longitude: int
                A valid longitude in the United States
        `Returns:`
           dict
        """

        geo = self.cg.coordinates(x=longitude, y=latitude)
        if len(geo["States"]) == 0:
            logger.info("Coordinate not found.")
        else:
            logger.info("Coordinate processed.")
        return geo
