import time
import hashlib

def authenticate_parameters(api_key, api_secret, parameters, expire=60):
    params = {}
    params.update(parameters)
    params["expire"] = int(time.time()) + expire
    params["api_key"] = api_key
    sig_base_string = ""
    for k in sorted(params.keys()):
        sig_base_string += "%s=%s" % (k, params[k])

    sig_base_string += api_secret
    md5 = hashlib.md5()
    md5.update(sig_base_string.encode("utf-8"))
    params["sig"] = md5.hexdigest()
    return params
