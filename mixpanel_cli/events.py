import json
import logging
import requests

from . import auth
from . import config

logger = logging.getLogger(__name__)

BASE_PATH = "https://mixpanel.com/api/2.0/events/"

def events(event, event_type, unit, interval, fmt="json"):
    logger.debug("Fetching event: %s" % event)
    params = {"event": json.dumps(event),
              "type": event_type,
              "unit": unit,
              "interval": interval,
              "format": fmt}

    params = auth.authenticate_parameters(config.API_KEY,
                                          config.API_SECRET, params)

    r = requests.get(BASE_PATH, params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.text

def top(event_type, limit=None):
    logger.debug("Fetching top events")
    params = {"type": event_type}
    if limit is not None:
        params["limit"] = limit

    params = auth.authenticate_parameters(config.API_KEY,
                                          config.API_SECRET, params)

    r = requests.get("%stop/" % BASE_PATH, params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.text

def names(event_type, limit=None):
    logger.debug("Fetching event names")
    params = {"type": event_type}
    if limit is not None:
        params["limit"] = limit

    params = auth.authenticate_parameters(config.API_KEY,
                                          config.API_SECRET, params)

    r = requests.get("%snames/" % BASE_PATH, params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.text
