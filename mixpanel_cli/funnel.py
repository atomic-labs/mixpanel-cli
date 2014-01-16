import datetime
import logging
import requests
from . import auth
from . import config

logger = logging.getLogger(__name__)

BASE_PATH = "https://mixpanel.com/api/2.0/"

def list():
    logger.debug("Getting list of funnels")
    params = auth.authenticate_parameters(config.API_KEY, config.API_SECRET, {})
    r = requests.get(BASE_PATH + "/funnels/list/", params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.json()

def funnel(funnel_id):
    logger.debug("Showing funnel with id %s" % funnel_id)
    to_date = datetime.date.today()
    from_date = to_date - datetime.timedelta(days=60)
    params = auth.authenticate_parameters(config.API_KEY, config.API_SECRET,
                                          {"funnel_id": funnel_id,
                                           "interval": 14,
                                           "from_date": from_date,
                                           "to_date": to_date})
    r = requests.get(BASE_PATH + "/funnels/", params=params)
    if r.status_code != 200:
        logger.warning("Received code: %s. Body: %s" % (r.status_code, r.text))
        return None

    return r.json()
