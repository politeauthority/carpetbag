"""Utils

"""
from datetime import datetime
import tld
import re


def url_join(*args):
    """
    Concats all args with slashes as needed.
    @note this will probably move to a utility class sometime in the near future.

    :param args: All the url components to join.
    :type args: list
    :returns: Ready to use url.
    :rtype: str
    """
    return url_concat(*args)


def url_concat(*args):
    """
    Concats all args with slashes as needed.
    @note this will probably move to a utility class sometime in the near future.

    :param args: All the url components to join.
    :type args: list
    :returns: Ready to use url.
    :rtype: str
    """
    url = ""
    for url_segment in args:
        if url and url[len(url) - 1] != "/" and url_segment[0] != "/":
            url_segment = "/" + url_segment
        url += url_segment

    if "://" not in url:
        url = "https://" + url

    protocol = url[:url.find("://") + 3]
    protocolless_url = url[url.find("://") + 3:]
    query_params = ""
    if "?" in protocolless_url:
        query_params = url[url.find("?"):]
        protocolless_url = url[:url.find("?")]
    if "//" in protocolless_url:
        protocolless_url = protocolless_url.replace("//", "/")

    return "%(protocol)s%(url)s%(params)s" % {
        "protocol": protocol,
        "url": protocolless_url,
        "params": query_params
    }


def url_disect(url):
    """
    Disects a url into all the different pieces which it contains.

    :param url: The url to disect.
    :type url: str
    :returns: The disected elements of the url.
    :rtype: dict
    """
    url_pieces = {
        "protocol": "",
        "domain": "",
        "sub_domains": [],
        "tld": "",
        "url": "",
        "last": "",
        "params": {},
    }
    if "://" in url:
        url_pieces["protocol"] = url[:url.find("://")]
        url_pieces["url"] = url[url.find("://") + 3:]
    else:
        url_pieces["protocol"] = ""
        url_pieces["url"] = url

    url_pieces["domain"] = get_domain(url)

    tld_res = tld.get_tld(url, as_object=True)
    sub_domains = tld_res.subdomain
    if "." in sub_domains:
        url_pieces["sub_domains"].split(".")
    else:
        url_pieces["sub_domains"] = [sub_domains]

    url_pieces["tld"] = tld.get_tld(url)

    url_pieces["url"] = url_pieces["url"].replace(url_pieces["protocol"] + "://", "")
    url_pieces["last"] = url_last(url, True)

    # Disect the query paramaters if they exist.
    if "?" in url:
        url_pieces["url"] = url_pieces["url"][:url_pieces["url"].find("?")]
        query_params = {}
        params_str = url[url.find("?") + 1:]
        if "&" in params_str:
            params = params_str.split("&")
        else:
            params = [params_str]

        for param in params:
            param_pieces = param.split("=")
            query_params[param_pieces[0]] = param_pieces[1]
        url_pieces["params"] = query_params

    return url_pieces


def get_domain(url):
    """
    Tries to get the domain/ip and port from the url we are requesting to.
    @todo: There looks to be an issue with getting an ip address from the url.

    :param url:
    :type urls: str
    :returns: The domain/ip of the server being requested to.
    :rtype: str
    """
    regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    matches = re.finditer(regex, url)
    for matchNum, match in enumerate(matches):
        try:
            return match.group()
        except AttributeError:
            pass

    if "//localhost" in url:
        return "localhost"

    try:
        return tld.get_fld(url)
    except tld.exceptions.TldDomainNotFound:
        return ""


def url_last(url, exclude_params=False):
    """
    Gets the last segment of a url.
    Example: url = "https://www.bad-actor.services/some/thing" == "thing"

    :param url: Url to parse.
    :type url: str
    :returns: The last segment of a url.
    :rtype: str
    """
    url = url[url.rfind("/") + 1:]
    if exclude_params and "?" in url:
        url = url[:url.find("?")]
    return url


def json_date(the_date=None):
    """
    Concats all args with slashes as needed.
    @note this will probably move to a utility class sometime in the near future.

    :param the_date: Datetime to convert, or if None, will use now.
    :type the_date: <DateTime> or None
    :returns: Jsonable date time string
    :rtype: str
    """
    if not the_date:
        the_date = datetime.now()
    ret = the_date.strftime("%Y-%m-%d %H:%M:%S")

    return ret


def add_missing_protocol(url):
    """
    Adds the protocol "http://" if a protocal is not present.

    :param url: The url that may or may not be missing a protocol.
    :type url: str
    :returns: Safe url with protocal.
    :rtype: str
    """
    if url[:8] == "https://" or url[:7] == "http://":
        return url
    else:
        return "%s%s" % ("http://", url)


def remove_protocol(url):
    """
    Adds a url's protocol "http://" if a protocal is not present.
    @note: This doesnt appear to even be used. Could probably be removed.

    :param url: The url that may or may not be missing a protocol.
    :type url: str
    :returns: Safe url with protocal.
    :rtype: str
    """
    url = url.replace("https", "")
    url = url.replace("http", "")
    url = url.replace("://", "")
    if "/" in url:
        url = url[: url.find("/")]
    return url


def content_type_to_extension(content_type):
    """
    Takes a content type and tries to map it to an extension.
    @todo: Needs more content types!

    :param content_type: Content type from a request
    :type content_type: str
    :returns: The extension translation from the content-type.
    :rtype: str
    """
    if content_type == "image/jpg" or content_type == "image/jpeg":
        return "jpg"
    elif content_type == "text/html":
        return "html"
    elif content_type == "text/css":
        return "css"
    return ""

# EndFile: carpetbag/carpetbag/carpet_tools.py
