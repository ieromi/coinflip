import time
import requests
import random
import json
from python3_capsolver.hcaptcha import HCaptcha


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json",
    "Origin": "https://coinflip.campnetwork.xyz",
    "Referer": "https://coinflip.campnetwork.xyz/dashboard",
    "Sec-Ch-Ua": '"Opera GX";v="109", "Not:A-Brand";v="8", "Chromium";v="123"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
}


def get_rucaptchav2():
    """
    This function handles the HCaptcha task using the python3_capsolver library.
    It returns the solution to the HCaptcha task and a success status.
    """
    try:
        success = 1
        task = HCaptcha(
            api_key="",
            captcha_type='HCaptchaTaskProxyless',
            websiteURL="https://coinflip.campnetwork.xyz",
            websiteKey="5b86452e-488a-4f62-bd32-a332445e2f51",
        ).captcha_handler()

        solution = task.solution['gRecaptchaResponse']

        return solution, success

    except Exception as e:
        success = 0
        return e, success


def get_faucet(address, proxy):
    """
    This function attempts to claim a faucet for the given address using the provided proxy.
    It uses a loop to handle the HCaptcha task and make the POST request to the API endpoint.
    The function returns the status code and response message of the API request.
    """
    try:
        proxies = {
            'http': proxy,
            'https': proxy
        }

        res = status_code = captcha_success = 0

        max_captcha_tries = random.randint(3, 6)
        captcha_try_count = 0

        while (captcha_success == 0 or status_code == 401) and (captcha_try_count != max_captcha_tries):
            time.sleep(random.randint(5, 10))
            captcha_try_count += 1
            hcaptcha, captcha_success = get_rucaptchav2()
            pload = {
                "address": address,
                "hcaptchaToken": hcaptcha
            }
            uri = f"https://coinflip.campnetwork.xyz/api/claim"

            res = requests.post(uri, data=json.dumps(pload), headers=headers, proxies=proxies)
            status_code = res.status_code

        return (f'Response status code: {status_code},'
                f'message: {res.text} '
                f'captcha try #{captcha_try_count}, '
                f'captcha success(0/1) {captcha_success}')

    except Exception as e:
        return e
