from parsons.pdi.flag_ids import FlagIDs
from parsons.pdi.flags import Flags
from parsons.pdi.universes import Universes
from parsons.pdi.questions import Questions
from parsons.pdi.acquisition_types import AcquisitionTypes
from parsons.pdi.events import Events
from parsons.pdi.locations import Locations
from parsons.pdi.contacts import Contacts
from parsons.pdi.activities import Activities

from parsons import Table
from parsons.utilities import check_env

from datetime import datetime, timezone
from dateutil.parser import parse
from json.decoder import JSONDecodeError
import logging
import requests


logger = logging.getLogger(__name__)


class PDI(
    FlagIDs,
    Universes,
    Questions,
    AcquisitionTypes,
    Flags,
    Events,
    Locations,
    Contacts,
    Activities,
):
    def __init__(self, username=None, password=None, api_token=None, qa_url=False):
        """
        Instantiate the PDI class

        `Args:`
            username: str
                The username for a PDI account. Can be passed as arguement or
                can be set as `PDI_USERNAME` environment variable.
            password: str
                The password for a PDI account. Can be passed as arguement or
                can be set as `PDI_PASSWORD` environment variable.
            api_token: str
                The api_token for a PDI account. Can be passed as arguement or
                can be set as `PDI_API_TOKEN` environment variable.
            qa_url: bool
                Defaults to False. If True, requests will be made to a sandbox
                account. This requires separate qa credentials and api
                token.
        """
        if qa_url:
            self.base_url = "https://apiqa.bluevote.com"
        else:
            self.base_url = "https://api.bluevote.com"

        self.username = check_env.check("PDI_USERNAME", username)
        self.password = check_env.check("PDI_PASSWORD", password)
        self.api_token = check_env.check("PDI_API_TOKEN", api_token)

        super().__init__()

        self._get_session_token()

    def _get_session_token(self):
        headers = {
            "Content-Type": "application/json",
        }
        login = {
            "Username": self.username,
            "Password": self.password,
            "ApiToken": self.api_token,
        }
        res = requests.post(f"{self.base_url}/sessions", json=login, headers=headers)
        logger.debug(f"{res.status_code} - {res.url}")
        res.raise_for_status()
        # status_code == 200
        data = res.json()
        self.session_token = data["AccessToken"]
        self.session_exp = parse(data["ExpirationDate"])

    def _clean_dict(self, dct):
        if isinstance(dct, list):
            return [self._clean_dict(obj) for obj in dct]

        if isinstance(dct, dict):
            return {k: v for k, v in dct.items() if v is not None}

        return dct

    def _request(self, url, req_type="GET", post_data=None, args=None, limit=None):
        # Make sure to have a current token before we make another request
        now = datetime.now(timezone.utc)
        if now > self.session_exp:
            self._get_session_token()

        # Based on PDI docs
        # https://api.bluevote.com/docs/index
        LIMIT_MAX = 2000

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.session_token}",
        }

        request_fn = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "DELETE": requests.delete,
        }

        if limit and limit <= LIMIT_MAX:
            args = args or {}
            args["limit"] = limit

        args = self._clean_dict(args) if args else args
        post_data = self._clean_dict(post_data) if post_data else post_data
        res = request_fn[req_type](url, headers=headers, json=post_data, params=args)
        logger.debug(f"{res.url} - {res.status_code}")
        logger.debug(res.request.body)

        res.raise_for_status()

        if not res.text:
            return None

        logger.debug(res.text)

        try:
            res_json = res.json()
        except JSONDecodeError:
            res_json = None

        if "data" not in res_json:
            return res_json

        total_count = 0 if "totalCount" not in res_json else res_json["totalCount"]
        data = res_json["data"]

        if not limit:
            # We don't have a limit, so let's get everything
            # Start a page 2 since we already go page 1
            cursor = 2
            while len(data) < total_count:
                args = args or {}
                args["cursor"] = cursor
                args["limit"] = LIMIT_MAX
                res = request_fn[req_type](url, headers=headers, json=post_data, params=args)

                data.extend(res.json()["data"])

                cursor += 1

            return Table(data)

        else:
            total_need = min(limit, total_count)

            cursor = 2
            while len(data) < total_need:
                args = args or {}
                args["cursor"] = cursor
                args["limit"] = min(LIMIT_MAX, total_need - len(data))
                res = request_fn[req_type](url, headers=headers, json=post_data, params=args)

                data.extend(res.json()["data"])

                cursor += 1

            return Table(data)
