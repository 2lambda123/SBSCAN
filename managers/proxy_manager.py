#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
   File Name：     proxy_manager.py
   Description :
   Author :       sule01u
   date：          2023/10/8
"""
import requests
from utils.custom_headers import DEFAULT_HEADER, TIMEOUT
from utils.logging_config import configure_logger

# Constants
TEST_URL = "https://www.baidu.com/"

logger = configure_logger(__name__)
requests.packages.urllib3.disable_warnings()


class ProxyManager:
    def __init__(self, proxies=None):
        """Initializes the function with a proxy, if provided, and checks if the proxy is functional. If the proxy is not functional, an error is raised and the function proceeds without the proxy.
        Parameters:
            - proxies (dict): A dictionary containing the proxy information.
        Returns:
            - None: This function does not return any value.
        Processing Logic:
            - Initialize function with proxy if provided.
            - Check if proxy is functional.
            - If proxy is not functional, raise error.
            - If proxy is functional, proceed with function."""
        
        self.proxy = proxies
        if self.proxy and not self._is_proxy_working():
            msg = "Proxy seems to be non-functional. Proceeding without it."
            logger.warning(msg)
            raise ConnectionError("Error: Proxy unavailable")

    def _is_proxy_working(self):
        """
        检测代理有效性
        """
        try:
            response = requests.get(TEST_URL, headers=DEFAULT_HEADER, verify=True, timeout=TIMEOUT)
            if response.status_code == 200:
                logger.info("Proxy detection available", extra={"target": self.proxy})
                return True
        except requests.Timeout:
            logger.warning("Proxy connection timed out", extra={"target": self.proxy})
        except requests.ConnectionError:
            logger.warning("Error connecting through proxy", extra={"target": self.proxy})
        except requests.RequestException:
            logger.warning("Proxy connection error", extra={"target": self.proxy})
        except Exception as e:
            logger.warning(f"Proxy detect UnknownError: {e}", extra={"target": self.proxy})
        return False

    def get_proxy(self):
        """"Returns the proxy value of the object."
        Parameters:
            - self (object): The object to retrieve the proxy value from.
        Returns:
            - proxy (object): The proxy value of the object.
        Processing Logic:
            - Retrieve the proxy value.
            - No additional processing is done.
            - Proxy value is returned.
            - No error handling is included."""
        
        return self.proxy

