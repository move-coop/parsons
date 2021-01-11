import petl

class Transformations:

    def __init__(self):

        pass

    def geocode(self, unique_id, street, city, state, zipcode):

        # Avoiding circular references.
        from parsons.geocode.census_geocoder import CensusGeocoder
        geo = CensusGeocoder()

        # Create a new table to pass to geocode.
        input_tbl = self.cut(unique_id, street, city, state, zipcode)

        # Prepare columns in correct order.
        for col in [unique_id, street, city, state, zipcode]:
            input_tbl.move_column(col, 4)

        # Geocode the columns
        output_tbl = geo.geocode_address_batch(input_tbl)

        # Join the coordinates back on to the orginal table
        self.table = petl.join(self.table, output_tbl.table, key=unique_id)

        return self.table
