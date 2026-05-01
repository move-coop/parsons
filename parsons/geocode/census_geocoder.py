import logging
from collections.abc import Collection
from typing import Literal, overload

import censusgeocode
import petl
from censusgeocode.censusgeocode import AddressResult, GeographyResult

from parsons import Table

logger = logging.getLogger(__name__)


# The size of batches to send to the batch geocode endpoint. Currently
# the recommendation is less than 1K records.
BATCH_SIZE = 999


class CensusGeocoder:
    """
    Instantiate the CensusGecoder Class.

    Args:
        benchmark:
            The US Census benchmark file to utilize.
            By default the current benchmark is used, but other options can found
            `here <https://geocoding.geo.census.gov/geocoder/benchmarks>`__.
        vintage:
            The US Census vintage file to utilize.
            By default the current vintage is used, but other options can be found
            `here <https://geocoding.geo.census.gov/geocoder/vintages?benchmark=4>`__.

    """

    def __init__(
        self, benchmark: str = "Public_AR_Current", vintage: str = "Current_Current"
    ) -> None:
        self.cg = censusgeocode.CensusGeocode(benchmark=benchmark, vintage=vintage)

    def geocode_onelineaddress(self, address: str, return_type: str = "geographies"):
        """
        Geocode a single line address.

        Does not require parsing of city and zipcode field.
        Returns geocode as well as other census block data.
        If the service is unable to geocode the address it will return an empty list.

        Args:
            address: A valid US address.
            return_type:
                ``geographies`` will return information about the Census geographies,
                while ``locations`` will information about the address.

        """
        geo = self.cg.onelineaddress(address, returntype=return_type)
        self._log_result(geo)
        return geo

    @overload
    def geocode_address(
        self,
        address_line: ...,
        city: ...,
        state: ...,
        zipcode: ...,
        return_type: Literal["geographies"] = "geographies",
    ) -> GeographyResult: ...

    @overload
    def geocode_address(
        self,
        address_line: ...,
        city: ...,
        state: ...,
        zipcode: ...,
        return_type: Literal["locations"],
    ) -> AddressResult: ...

    def geocode_address(
        self,
        address_line: str,
        city: str | None = None,
        state: str | None = None,
        zipcode: str | None = None,
        return_type: Literal["geographies", "locations"] = "geographies",
    ) -> AddressResult | GeographyResult:
        """
        Geocode an address by specifying address fields.

        Returns the geocode as well as other census block data.

        Args:
            address_line: A valid address line
            city: A valid city
            state: A valid two character state abbreviation (e.g. ``IL``)
            zipcode: A valid five digit zipcode (e.g. ``60622``)
            return_type:
                ``geographies`` will return information about the Census geographies,
                while ``locations`` will information about the address.

        """
        geo = self.cg.address(
            address_line, city=city, state=state, zipcode=zipcode, returntype=return_type
        )
        self._log_result(geo)
        return geo

    def geocode_address_batch(self, table: Table) -> Table:
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

        Raises:
            ValueError: If the table does not contain the required columns.

        """
        logger.info(f"Geocoding {table.num_rows} records.")
        if set(table.columns) != {"id", "street", "city", "state", "zip"}:
            msg = (
                "Table must ONLY include `['id', 'street', 'city', 'state', 'zip']` as columns. "
                "Tip: try using `table.cut()`"
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

    def _log_result(self, dict: Collection) -> None:
        """Internal method to log the result of the geocode."""
        if len(dict) == 0:
            logger.info("Unable to geocode record.")
        else:
            logger.info("Record geocoded.")

    def get_coordinates_data(self, latitude: float, longitude: float) -> GeographyResult:
        """
        Return census data on coordinates.

        Args:
            latitude: A valid latitude in the United States
            longitude: A valid longitude in the United States

        """
        geo: GeographyResult = self.cg.coordinates(x=longitude, y=latitude)
        if len(geo["States"]) == 0:
            logger.info("Coordinate not found.")
        else:
            logger.info("Coordinate processed.")
        return geo
