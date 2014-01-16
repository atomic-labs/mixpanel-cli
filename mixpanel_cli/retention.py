import logging
import requests
from . import auth
from . import config

logger = logging.getLogger(__name__)

PATH = "https://mixpanel.com/api/2.0/retention/"

def retention(from_date, to_date, retention_type="birth", born_event=None,
              event=None, born_where=None, where=None, interval=None,
              interval_count=None, unit=None, on=None, limit=None):
    if retention_type == "birth" and born_event is None:
        logger.error("born_event must be set if retention_type is \"birth\" "
                     "(the default)")
        return None

    logger.debug("Getting retention data")
    params = {"from_date": from_date, "to_date": to_date,
              "retention_type": retention_type}

    if born_event is not None:
        params["born_event"] = born_event

    if event is not None:
        params["event"] = event

    if born_where is not None:
        params["born_where"] = born_where

    if where is not None:
        params["where"] = where

    if interval is not None:
        params["interval"] = interval

    if interval_count is not None:
        params["interval_count"] = interval_count

    if unit is not None:
        params["unit"] = unit

    if on is not None:
        params["on"] = on

    if limit is not None:
        params["limit"] = limit

    params = auth.authenticate_parameters(config.API_KEY, config.API_SECRET,
                                          params)
    r = requests.get(PATH, params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.json()
