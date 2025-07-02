"""
Download utilities for FDMA 2530 shelf system.

Handles HTTP requests to GitHub and other sources with proper
error handling, timeouts, and cross-platform compatibility.

Functions
---------
download_raw(url, timeout=15) -> str or None
    Download raw text content from a URL.

download_json(url, timeout=15) -> dict or None  
    Download and parse JSON content from a URL.
"""

from __future__ import absolute_import, print_function

try:
    # Python 3
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    # Python 2
    from urllib2 import urlopen, URLError, HTTPError

import sys


def download_raw(url, timeout=15):
    """
    Download raw text content from a URL.
    
    Parameters
    ----------
    url : str
        URL to download from.
    timeout : int, optional
        Timeout in seconds for the request.
        
    Returns
    -------
    str or None
        Downloaded text content, None if failed.
    """
    try:
        response = urlopen(url, timeout=timeout)
        content = response.read()
        
        # Handle Python 3 bytes to string conversion
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode("utf-8")
            
        return content
        
    except (URLError, HTTPError) as e:
        print("Download failed for {0}: {1}".format(url, e))
        return None
    except Exception as e:
        print("Unexpected download error for {0}: {1}".format(url, e))
        return None


def download_json(url, timeout=15):
    """
    Download and parse JSON content from a URL.
    
    Parameters
    ----------
    url : str
        URL to download JSON from.
    timeout : int, optional
        Timeout in seconds for the request.
        
    Returns
    -------
    dict or None
        Parsed JSON data, None if failed.
    """
    import json
    
    raw_content = download_raw(url, timeout)
    if not raw_content:
        return None
        
    try:
        return json.loads(raw_content)
    except (ValueError, TypeError) as e:
        print("Failed to parse JSON from {0}: {1}".format(url, e))
        return None


def get_github_raw_url(user, repo, branch, file_path):
    """
    Build a GitHub raw content URL.
    
    Parameters
    ----------
    user : str
        GitHub username.
    repo : str
        Repository name.
    branch : str
        Branch name (e.g. 'master', 'main').
    file_path : str
        Path to file within repository.
        
    Returns
    -------
    str
        Complete GitHub raw URL.
    """
    return "https://raw.githubusercontent.com/{0}/{1}/{2}/{3}".format(
        user, repo, branch, file_path
    )
