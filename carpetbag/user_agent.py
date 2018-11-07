"""User Agent
Module for storing and retreiving user agent strings.

"""
import random

user_agents = {
    "Firefox 40.1": [
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"
    ],
    "Firefox 36.0": [
        "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"
    ],
    "Firefox 33.0": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"
    ],
    "Firefox 31.0": [
        "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
        "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
    ],


    "Chrome 41.0.2228.0": [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"],
    "Chrome 41.0.2227.1": [
        """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) """ +
        """Chrome/41.0.2227.1 Safari/537.36"""],
    "Chrome 41.0.2227.0": [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    ],
    "Chrome 41.0.2226.0": [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    ],
    "Chrome 41.0.2225.0": [
        "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36"
    ],
    "Chrome 41.0.2224.3": [
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36"
    ],
    "Chrome 40.0.2214.93": [
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36"
    ]
}


def get_random_ua(except_user_agent=""):
    """
    Gets a random user aget string. @todo add optional restrictions for browser brand/operating system.

    :param except_user_agent: User agent string to be removed from consideration.
    :type except_user_agent: str
    :returns: A user agent string.
    :rtype: str
    """
    possible_strings = get_flattened_uas()
    if except_user_agent and except_user_agent in possible_strings:
        possible_strings.remove(except_user_agent)

    return possible_strings[random.randint(0, len(possible_strings) - 1)]


def get_flattened_uas():
    """
    Gets a flattened list of user agent strings, sometimes a little easier to work with than the dictionary.

    :returns: All User Agent Strings in a single flat list.
    :rtype: list
    """
    flattend_user_agents = []
    for browser, uas in user_agents.items():
        flattend_user_agents = flattend_user_agents + uas

    return flattend_user_agents


# EndFile: CarpetBag/carpetbag/user_agent.py
