# Parsons


A Python package that provides a simple interface to a variety of utilities and tools frequently used by progressive organizations, political and issue campaigns, activists, and other allied actors.

Parsons offers simplified interactions with these services and tools, including a growing number of CRMs, organizing tools, cloud compute service providers, as well as tools to easily trasform data in transit.

This project maintained by [The Movement Cooperative](https://movementcooperative.org/) and is named after [Lucy Parsons](https://en.wikipedia.org/wiki/Lucy_Parsons). The Movement Cooperative is a member led organization focused on providing data, tools, and strategic support for the progressive community.

### License and Usage
Usage of Parsons is governed by the [TMC Parsons License](https://github.com/move-coop/parsons_public/blob/documentation/LICENSE.md), which allows for unlimited non-commercial usage, provided that individuals and organizations adhere to our broad values statement. 

### Documentation
The gain a full understanding of all of the features of Parsons, please review the Parson's [documentation](https://move-coop.github.io/parsons/html/index.html).


### Installation


#### PYPI
You can install the most recent release by running: `pip install parsons`


#### Install from Github

To access the most recent code base that may contain features not yet included in the latest release, download this repository and then run `python setup.py develop`.

### Quickstart

```
# VAN - Download activist codes to a CSV

van = VAN(db='MyVoters')
ac = van.get_activist_codes()
ac.to_csv('my_activist_codes.csv')

# Redshift - Create a table from a CSV

tbl = Table.from_csv('my_table.csv')
tbl.to_redshift('my_schema.my_table')

# Redshift - Export from a query to CSV

sql = 'select * from my_schema.my_table'
rs = Redshift()
tbl = rs.query(sql)
tbl.to_csv('my_table.csv')

# Upload a file to S3

s3 = S3()
s3.put_file('my_bucket','my_table.csv')

# TargetSmart - Append data to a record

ts = TargetSmart(api_key='MY_KEY')
record = ts.data_enhance(231231231, state='DC')
```


### Community
We hope to foster a strong and robust community of individuals who use and contribute to further development. Individuals are encouraged to submit issues with bugs, suggestions and feature requests. [Here](https://github.com/move-coop/parsons_public/blob/documentation/docs/contributing.md) are the guidelines and best practices for contributing to Parsons.

You can also stay up to date by joining the parsons google group.
