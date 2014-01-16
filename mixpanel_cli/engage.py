import logging
import requests
from . import auth
from . import config

logger = logging.getLogger(__name__)

PATH = "https://mixpanel.com/api/2.0/engage/"

def list(where=None, session_id=None, page=None):
    logger.debug("Getting list of users")

    if (page == None) ^ (session_id == None):
        logger.error("Must include both page and session_id if one is included")
        return None

    params = {}
    if where is not None:
        params["where"] = where
    if session_id is not None:
        params["session_id"] = session_id
    if page is not None:
        params["page"] = page

    params = auth.authenticate_parameters(config.API_KEY, config.API_SECRET, {})
    r = requests.get(PATH, params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.json()
