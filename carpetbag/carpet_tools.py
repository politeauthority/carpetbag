"""Utils

"""
from datetime import datetime
import re

import tld


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
    regex = r":\d{2,4}"
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


def url_create(url_segments, omit_standard_ports=True):
    """
    Puts a URL back together after it's been disected by url_disect.

    :param url_segments: The URL segments from the url_disect method.
    :type url_segments: dict
    :param omit_standard_ports: Skips adding standard ports to a URL.
    :type omit_standard_ports: Bool
    :returns: A full, usable url
    :rtype: str
    """
    param_seg = ""
    if url_segments["params"]:
        param_seg = "?%s" % url_segments["params"]

    subdomain_seg = ""
    for sub in url_segments["subdomains"]:
        subdomain_seg += "%s." % sub
    domain_seg = ""
    if url_segments["domain"]:
        domain_seg = "%s" % url_segments["domain"]

    port_seg = ""
    if url_segments["port"] not in ["443", "80"]:
        port_seg = ":%s" % url_segments["port"]
    elif not omit_standard_ports:
        port_seg = ":%s" % url_segments["port"]

    full_url = "%(protocol)s://%(subdomains)s%(domain)s%(port)s%(uri)s%(params)s" % {
        "protocol": url_segments["protocol"],
        "subdomains": subdomain_seg,
        "domain": domain_seg,
        "port": port_seg,
        "uri": url_segments["uri"],
        "params": param_seg
    }
    # import pdb; pdb.set_trace()

    return full_url


def json_date(the_date=None):
    """
    Concats all args with slashes as needed.

    :param the_date: Datetime to convert, or if None, will use now.
    :type the_date: <DateTime> or None
    :returns: Jsonable date time string
    :rtype: str
    """
    if not the_date:
        the_date = datetime.now()
    ret = the_date.strftime("%Y-%m-%d %H:%M:%S")

    return ret


def content_type_to_extension(content_type):
    """
    Takes a content type and tries to map it to an extension.
    @note: This is not a very complete list of content types, just what I could find easily, this could be expanded!

    :param content_type: Content type from a request
    :type content_type: str
    :returns: The extension translation from the content-type.
    :rtype: str
    """
    xlate_extension_to_mime = {
        "aac": "audio/aac",
        "abw": "application/x-abiword",
        "arc": "application/octet-stream",
        "avi": "video/x-msvideo",
        "azw": "application/vnd.amazon.ebook",
        "bin": "application/octet-stream",
        "bmp": "image/bmp",
        "bz": "pplication/x-bzip",
        "bz2": "application/x-bzip2",
        "csh": "application/x-csh",
        "css": "text/css",
        "csv": "text/csv",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "eot": "application/vnd.ms-fontobject",
        "epub": "application/epub+zip",
        "es": "application/ecmascript",
        "gif": "image/gif",
        "html": "text/html",
        "ico": "image/x-icon",
        "ics": "text/calendar",
        "jar": "application/java-archive",
        "jpg": "image/jpeg",
        "js": "application/javascript",
        "json": "application/json",
        "midi": "audio/midi audio/x-midi",
        "mpeg": "video/mpeg",
        "mpkg": "application/vnd.apple.installer+xml",
        "odp": "application/vnd.oasis.opendocument.presentation",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "odt": "application/vnd.oasis.opendocument.text",
        "oga": "audio/ogg",
        "ogv": "video/ogg",
        "ogx": "application/ogg",
        "otf": "font/otf",
        "png": "image/png",
        "pdf": "application/pdf",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "rar": "application/x-rar-compressed",
        "rtf": "application/rtf",
        "sh": "application/x-sh",
        "svg": "image/svg+xml",
        "swf": "application/x-shockwave-flash",
        "tar": "application/x-tar",
        "tiff": "image/tiff",
        "ts": "application/typescript",
        "ttf": "font/ttf",
        "txt": "text/plain",
        "vsd": "application/vnd.visio",
        "wav": "audio/wav",
        "weba": "audio/webm",
        "webm": "video/webm",
        "webp": "image/webp",
        "woff": "font/woff",
        "woff2": "font/woff2",
        "xhtml": "application/xhtml+xml",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xml": "application/xml",
        "xul": "application/vnd.mozilla.xul+xml",
        "zip": "application/zip",
        "7z": "application/x-7z-compressed",
    }
    for extension, i_content_type in xlate_extension_to_mime.items():
        if i_content_type == content_type:
            return extension
    return ""

# EndFile: carpetbag/carpetbag/carpet_tools.py
