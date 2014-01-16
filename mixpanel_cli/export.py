import json
import logging
import requests

from . import auth
from . import config

logger = logging.getLogger(__name__)

BASE_PATH = "https://data.mixpanel.com/api/2.0/export/"

def export(from_date, to_date, event=None, where=None, bucket=None):
    logger.debug("Exporting data from %s to %s" % (from_date, to_date))
    params = {"from_date": from_date, "to_date": to_date}
    if event is not None:
        params["event"] = json.dumps(event)
    if where is not None:
        params["where"] = where
    if bucket is not None:
        params["bucket"] = bucket

    params = auth.authenticate_parameters(config.API_KEY,
                                          config.API_SECRET, params)
    print(params)

    r = requests.get(BASE_PATH, params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.text
