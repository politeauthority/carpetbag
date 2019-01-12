"""Carpet Tools
A series of tools for use in and outside of CarpetBag internally. Mostly for ease of handling urls.

"""
import re

import arrow
import tld

from . import xlate_extension_mime as xetm


def url_join(*args):
    """
    Concats all args with slashes as needed. This just a copy of url_concact.

    :param args: All the url components to join.
    :type args: list
    :returns: Ready to use url.
    :rtype: str
    """
    return url_concat(*args)


def url_concat(*args):
    """
    Concats all args with slashes as needed.

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

    url_segs = url_disect(url)
    return url_create(url_segs)


def url_add_missing_protocol(url, default="http"):
    """
    Adds a protocal to a URL if one is not present

    :param url: URL that may or may not have a protocol.
    :type url: str
    :param default: The protocal to default to if one is not present.
    :type default: str
    :returns: Adds a protocal of http if no protocal present.
    :rtype: str
    """
    if url[:6] != "https:" and url[:5] != "http:":
        url = "%s://%s" % (default, url)
    return url


def url_disect(url):
    """
    Disects a url into all the different pieces which it contains.

    :param url: The url to disect.
    :type url: str
    :returns: The disected elements of the url.
    :rtype: dict
    """
    url_pieces = {
        "original": url,
        "protocol": "",
        "domain": "",
        "subdomains": [],
        "tld": "",
        "port": "",
        "uri": "",
        "last": "",
        "params": {},
    }
    url = url_add_missing_protocol(url)

    url_pieces["protocol"] = url[:url.find("://")]

    url_pieces["uri"] = url.replace(url_pieces["protocol"] + "://", "")
    url_pieces["subdomains"] = url_subdomain(url)
    url_pieces["domain"] = url_domain(url)
    url_pieces["tld"] = url_tld(url)
    url_pieces["port"] = url_port(url)
    url_pieces["last"] = url_last(url, True)

    for subdomain in url_pieces["subdomains"]:
        url_pieces["uri"] = url_pieces["uri"].replace(subdomain + ".", "")

    url_pieces["uri"] = url_pieces["uri"].replace(url_pieces["domain"], "")

    for subdomain in url_pieces["subdomains"]:
        url_pieces["uri"] = url_pieces["uri"].replace(subdomain + ".", "")

    url_pieces["uri"] = url_pieces["uri"].replace(url_pieces["domain"], "")

    # Disect the query paramaters if they exist.
    url_pieces["params"] = url_params(url)
    if "?" in url_pieces["uri"]:
        url_pieces["uri"] = url_pieces["uri"][:url_pieces["uri"].find("?")]

    if ":%s" % url_pieces["port"] in url_pieces["uri"]:
        url_pieces["uri"] = url_pieces["uri"].replace(":%s" % url_pieces["port"], "")

    url_pieces["uri"] = url_pieces["uri"].replace("//", "/")

    return url_pieces


def url_subdomain(url):
    """
    Gets the sub domains from a url.

    :param url: The url to disect.
    :type url: str
    :returns: All subdomains within a url in order.
    :rtype: list
    """
    subdomain = ""
    try:
        tld_res = tld.get_tld(url, as_object=True)
        subdomain = tld_res.subdomain
    except tld.exceptions.TldDomainNotFound:
        # If the url is an IP address there will not be subdomains to worry about.
        regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        matches = re.finditer(regex, url)
        for matchNum, match in enumerate(matches):
            try:
                return []
            except AttributeError:
                pass

    if subdomain and "." in subdomain:
        ret_subdomains = subdomain.split(".")
    else:
        ret_subdomains = [subdomain]
    return ret_subdomains


def url_domain(url):
    """
    Tries to get the domain/ip and port from the url we are requesting to.

    :param url: The url to disect.
    :type url: str
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


def url_port(url):
    """
    Gets the URL's port.

    :param url: The url to disect.
    :type url: str
    :returns: The port related to the url.
    :rtype: str
    """
    regex = r":\d{2,5}"
    matches = re.finditer(regex, url)
    for matchNum, match in enumerate(matches):
        try:
            return match.group()[1:]
        except AttributeError:
            pass

    if url[:5] == "https":
        return "443"

    return "80"


def url_tld(url):
    """
    Just a wrapper for the TLD module's get_tld method.

    :param url: The url to disect.
    :type url: str
    :returns: The url's top level domain.
    :rtype: str
    """
    try:
        return tld.get_tld(url)
    except tld.exceptions.TldDomainNotFound:
        return ""


def url_last(url, exclude_params=False):
    """
    Gets the last segment of a url.
    Example: url = "https://www.bad-actor.services/some/thing" == "thing"

    :param url: Url to parse.
    :type url: str
    :param exclude_params: Exludes paramters from the last segment of the url.
    :type exclude_params: Bool
    :returns: The last segment of a url.
    :rtype: str
    """
    url = url[url.rfind("/") + 1:]
    if exclude_params and "?" in url:
        url = url[:url.find("?")]
    return url


def url_params(url):
    """
    Gets the URL query paramters.

    :param url:
    :type url: str
    :returns: The url paramters.
    :rtype: str
    """
    query_params = {}

    if "?" in url:
        params_str = url[url.find("?") + 1:]
        if "&" in params_str:
            params = params_str.split("&")
        else:
            params = [params_str]

        for param in params:
            param_pieces = param.split("=")
            query_params[param_pieces[0]] = param_pieces[1]

    return query_params


def url_create(url_segs, omit_standard_ports=True):
    """
    Puts a URL back together after it's been disected by url_disect.

    :param url_segs: The URL segments from the url_disect method.
    :type url_segs: dict
    :param omit_standard_ports: Skips adding standard ports to a URL.
    :type omit_standard_ports: Bool
    :returns: A full, usable url
    :rtype: str
    """
    param_seg = ""
    if url_segs["params"]:
        param_seg = "?%s" % url_segs["params"]

    subdomain_seg = ""
    for sub in url_segs["subdomains"]:
        subdomain_seg += "%s." % sub

    domain_seg = ""
    if url_segs["domain"]:
        domain_seg = "%s" % url_segs["domain"]

    port_seg = ""
    if url_segs["port"] not in ["443", "80"]:
        port_seg = ":%s" % url_segs["port"]
    elif not omit_standard_ports:
        port_seg = ":%s" % url_segs["port"]

    # For non-standard urls like homenames that might not get a domain.
    if not url_segs["domain"]:
        return url_add_missing_protocol(url_segs["original"])

    full_url = "%(protocol)s://%(subdomains)s%(domain)s%(port)s%(uri)s%(params)s" % {
        "protocol": url_segs["protocol"],
        "subdomains": subdomain_seg,
        "domain": domain_seg,
        "port": port_seg,
        "uri": url_segs["uri"],
        "params": param_seg
    }

    return full_url


def date_to_json(the_date=None):
    """
    Gets a date string capable of being sent over JSON.

    :param the_date: Datetime to convert, or if None, will use now.
    :type the_date: <DateTime> or None
    :returns: JSONable date time string
    :rtype: str
    """
    if not the_date:
        the_date = arrow.utcnow().datetime
    ret = the_date.strftime("%Y-%m-%d %H:%M:%S")

    return ret


def json_to_date(the_json_date):
    """
    Attempts to create a python dastetime object from a JSON type data string.

    :param the_json_date: A string from a JSON response to attempt to create a datetime object out of.
    :type the_json_date: str
    :returns: A datetime representation of the string argument supplied.
    :rtype: <datetime> obj
    """
    ret = arrow.get(the_json_date)
    return ret.datetime


def content_type_to_extension(content_type):
    """
    Takes a content type and tries to map it to an extension.
    @note: This is not a very complete list of content types, just what I could find easily, this could be expanded!

    :param content_type: Content type from a request
    :type content_type: str
    :returns: The extension translation from the content-type.
    :rtype: str
    """
    for extension, i_content_type in xetm.xlate_extension_to_mime.items():
        if content_type in i_content_type:
            return extension

    return ""


def extension_to_content_type(user_extension):
    """
    Takes an extension and attempts to pair ir with a content type.
    @note: This is not a very complete list of content types, just what I could find easily, this could be expanded!

    :param user_extension: Content type from a request
    :type user_extension: str
    :returns: The matching HTTP Content-Type for a particular extension.
    :rtype: str
    """
    for extension, i_content_type in xetm.xlate_extension_to_mime.items():
        if user_extension in extension:
            return i_content_type[0]

    return ""

# EndFile: carpetbag/carpetbag/carpet_tools.py
