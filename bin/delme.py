import sys
#sys.path.append("~/Documents/parsons")
sys.path.append('/Users/charleskramer/Documents/parsons')
import parsons
from google.auth import default
app_creds,_ = default()

# app_creds = {
#   "type": "service_account",
#   "project_id": "sql-practice-425619",
#   "private_key_id": "31d4ba8aa75b0fa6a892072e4cb73d907940f24e",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDMbfuUhBQX92vv\nYdXaw6gNNLQSY+Mu+Dg2fGN0tqZrJn3HaHeBS1GWoF3rJE9M9/vmivuNSuaPgBts\nqY9x/yQ/6zYtQ62vPO0LMtLWB+NdP2Ha87eFbPEMJA2RuTubeEwfEfnv82ZBVXrI\n9+1DwbPqEqg8CrVEIBC9JJq4qyYEXj6c3ol8DcgB9Vwz8d/XrIQ7Xam2wBF/6Eba\nB8qiyzF0N40YlkjQLZ3MlQvZFBxgXAGz9qjFjTNvhrvBqz+l2+IXPzLAecvWgEck\nekbp/QsfPrCkCd614pXFdklPUzoFaznlu2EpjeQMPH3Jc9vFIzI6EjppP1wKThNk\nQPsVaedDAgMBAAECggEALd++VVkAM1Kb33d6aGGAjBoYEIpmuCsOXjeyj8XO+XuF\nPSK1sodm0yDAgpw+yVxapCTrBw1YSLpsLQmtvVyOU2OiYCzwREMtRFaO1mWlwU6Q\nVHRdae0E+H78podFF4G6vzwm9JAPkbivWXq9PPeyOmQeaX7Tp2p0pyUYLTmGyfK/\nbXT7GiIT74U6mK2mhjUws36gp/bZj2ciwOPLdKZz6qFT7c2ncp3xHZGtZOGQi0WZ\neYu0dxu8MUSNWA6yf0tdhGLGY6s5D9lgUd6S7fREd5146gc95fRmWwNXkl1ywLTp\nLHx6IvSe0Xuo6gg0kKCJmeRY26gTWl0QtsdWkqjdWQKBgQDrtOu6vBgvhm27b4VA\nFkVxHPlNNFgnegt2EhCmK2WCqCk7GbQrkQRlHr+UT5SL+gDbcTXuc34ui+/xm0XG\nUqjs2+1ntX2nkM1h7hdhPwSiiizlX2ggx7Mvz2gWBkOaXX3sBYy3ixfkzIY78Y8Q\nwIfnG+3oBsOKwP/2ET+K5UAmewKBgQDeB7NveBuTvMK7evhUzWAGvSquBHAn9BzI\n18vlkywODFhuQ0QqPses/ErB/KpercaMSnqBtyFnlpMzqYiH/aLSAPTghkLhfO7i\n9m8RfXtSPftj7glgm0uVfkOPkzupeJFRTEvTiW/qyyUBCGEszCujpMVGFh5/OsNF\n16Xp1IYL2QKBgC1YYQFLrlt2QSYODlSF9FYOfOedalgt4oaUcx+EucKpF0WHbGH1\nRCMwBytBJBLJxeBxpy54iY3q3f5dIM9Gl7j5lnKdN89EzD5Kz7Slqv6aFokKEb48\nrPxFqoCSM+8+jTsa1jd5St95eVmO3zcZ0wtjFCHPK09GUffE2bSe5fiBAoGBAIXg\nxNx44sABeLYNXwHbWISXuc12FZ6xvk2IeYSzakQKQ6Qw4UBL3KC8++LelGhEhkz/\nd8ERiI3qqFXlatL9KBlSxFVB/7/xUiX+jFhSfnLHtva5iGP9H+VDXj+LetUkQxNv\nWuVxoM9FsMlfoSCe981TxDQPkFINP8O0VXGaWT15AoGAfGtNOQ25T41F2DLo6JSe\noayqyJe2b99jL92+BHD987U9w//j/FzwnYBUcXMKuYma75LYkpampAxtuMuamlNn\nq6FLJsfTJ7a9pP3ifN4tcdrK2v2FT4yK1d03kTG6HNNaqZBat5oe4y+8DeupWovW\nU17W2i4QavuYn0FNFMXOusc=\n-----END PRIVATE KEY-----\n",
#   "client_email": "parsons-bq@sql-practice-425619.iam.gserviceaccount.com",
#   "client_id": "104516682065371288685",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/parsons-bq%40sql-practice-425619.iam.gserviceaccount.com",
#   "universe_domain": "googleapis.com"
# }
#


gbq = parsons.GoogleBigQuery(app_creds=app_creds)



# input parameters
source_project = 'sql-practice-425619'
source_dataset = 'bqtest'
source_table = 'va_2022_general'
# source_table_id = "sql-practice-425619.bqtest.va_2022_general"
# destination_table_id = "bq-for.bq2test.va_2022_general"
destination_project = 'bq-for'
destination_dataset = 'bqnew'
destination_table = 'va_2022_general_copy'
if_dataset_not_exists = 'create'  # create
if_table_exists = 'overwrite'  # overwrite

#Access Denied: Dataset bq-for:bqnew: Permission bigquery.datasets.get denied on dataset bq-for:bqnew (or it may not exist).

destination_project = 'sql-practice-425619'
destination_dataset = 'bqtest'
destination_table = 'va_2022_general'
# source_table_id = "sql-practice-425619.bqtest.va_2022_general"
# destination_table_id = "bq-for.bq2test.va_2022_general"
source_project = 'bq-for'
source_dataset = 'bqnew'
source_table = 'va_2022_general_copy'
if_dataset_not_exists = 'create'  # create
if_table_exists = 'overwrite'  # overwrite

#Access Denied: Dataset sql-practice-425619:bqtest: Permission bigquery.datasets.get denied on dataset sql-practice-425619:bqtest (or it may not exist).

# removed the client call in the method
source_project = 'sql-practice-425619'
source_dataset = 'bqtest'
source_table = 'va_2022_general'
# source_table_id = "sql-practice-425619.bqtest.va_2022_general"
# destination_table_id = "bq-for.bq2test.va_2022_general"
destination_project = 'bq-for'
destination_dataset = 'bqnew'
destination_table = 'va_2022_general_copy'

if_dataset_not_exists = 'create'  # create
if_table_exists = 'overwrite'  # overwrite


gbq.copy_between_projects(source_project,source_dataset,source_table,
                          destination_project,destination_dataset,destination_table,
                          if_dataset_not_exists,if_table_exists)
