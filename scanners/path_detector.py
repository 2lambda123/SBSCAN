#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
   File Name：     path_detector.py
   Description :
   Author :       sule01u
   date：          2023/10/8
"""
import requests
from urllib.parse import urljoin
from utils.custom_headers import TIMEOUT, DEFAULT_HEADER
from colorama import Fore
from utils.logging_config import configure_logger
logger = configure_logger(__name__)


class PathDetector:
    MAX_FAILED_COUNT = 80
    MAX_SUCCESS_COUNT = 50
    CHUNK_SIZE = 1024
    SSE_MAX_SIZE = 5120  # 5KB
    MAX_RESPONSE_LENGTH = 102400  # 100KB

    def __init__(self, paths, proxy_manager):
        """Initializes the class with the given paths and proxy manager.
        Parameters:
            - paths (list): List of paths to be used.
            - proxy_manager (ProxyManager): Object that manages the proxy.
        Returns:
            - None: This function does not return anything.
        Processing Logic:
            - Initializes the class with given paths.
            - Gets a proxy from the proxy manager.
            - Assigns the proxy to the class variable."""
        
        self.paths = paths
        self.proxy = proxy_manager.get_proxy()

    def detect(self, url):
        """
        敏感路径检测
        """
        path_failed_count = 0
        path_success_count = 0
        detected_paths = []
        for path, signature in self.paths.items():
            if path_failed_count > self.MAX_FAILED_COUNT:
                logger.info(f"failed_count: {path_failed_count} - stop detecting paths! Exceeds the maximum number of failed request", extra={"target": url})
                break
            elif path_success_count > self.MAX_SUCCESS_COUNT:
                logger.info(f"success_count: {path_success_count} - stop detecting paths! Exceeds the maximum number of successful request", extra={"target": url})
                detected_paths = []
                break
            full_url = urljoin(url, path)
            response = self._make_request(full_url)
            if not response:
                path_failed_count += 1
                continue
            if signature.lower() in response.lower():
                path_success_count += 1
                detected_paths.append(full_url)
                logger.info(Fore.CYAN + f"<-- " + Fore.RED + f"[success detected path!]", extra={"target": full_url})
        return detected_paths

    def _make_request(self, url):
        """Makes a request to the provided URL and returns the response content or None if an error occurs.
        Parameters:
            - url (str): The URL to make the request to.
        Returns:
            - str: The response content if the request is successful, or None if an error occurs.
        Processing Logic:
            - Sends a GET request with specified headers, timeout, and proxies.
            - Checks if the response content type is "text/event-stream".
            - If so, reads the response content in chunks and decodes it.
            - If not, checks if the response status code is 200.
            - If so, returns the first MAX_RESPONSE_LENGTH characters of the response text.
            - If an error occurs, logs the error and returns None."""
        
        try:
            with requests.get(url, headers=DEFAULT_HEADER, verify=True, proxies=self.proxy, timeout=TIMEOUT, stream=True, allow_redirects=False) as res:
                logger.debug(Fore.CYAN + f"[{res.status_code}]" + Fore.BLUE + f"  [Content-Length: {res.headers.get('Content-Length', 0)}]", extra={"target": url})
                if "text/event-stream" in res.headers.get("Content-Type", ""):
                    content = b""
                    for chunk in res.iter_content(self.CHUNK_SIZE):
                        content += chunk
                        if len(content) > self.SSE_MAX_SIZE:
                            break
                    return content.decode("utf-8")
                elif res.status_code == 200:
                    return res.text[:self.MAX_RESPONSE_LENGTH]
        except requests.RequestException as e:
            logger.debug(f"Request error: {e}", extra={"target": url})
        except Exception as e:
            logger.error(f"An unexpected error occurred during path detection: {e}", extra={"target": url})
        return None


if __name__ == '__main__':
    from managers.proxy_manager import ProxyManager
    proxy_manager = ProxyManager()
    paths = {"actuator": "_links", "actuator/beans": "beans"}
    path_d = PathDetector(paths, proxy_manager)
    print(path_d.detect("http://192.168.1.13:8080/"))
    print(path_d.detect("http://192.168.1.13:8083/"))
