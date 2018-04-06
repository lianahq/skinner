from selenium import webdriver
# from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import helpers

def setSeleniumProxy(burpUrl, burpProxyPort, seleniumUrl, seleniumPort, target):
    PROXY = "{}:{}".format(
            burpUrl,
            burpProxyPort
            )
    desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
    desired_capabilities['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "noProxy": None,
            "proxyType": "MANUAL",
            "class": "org.openqa.selenium.Proxy",
            "autodetect": False
            }
    driver = webdriver.Remote(
            "http://{}:{}/wd/hub".format(
                seleniumUrl,
                seleniumPort
            ), desired_capabilities)
    print("Connecting to Selenium server and sending target traffic to burp from Selenium for {}, Please wait...".format(target))

    # driver.get(target)
    # driver.quit()

    return driver

#TODO authentication
#TODO driver.get pages
#TODO taking and saving screenshot of pages in scan and adding to report

def appLogin(burpUrl, burpProxyPort, seleniumUrl, seleniumPort, target):
    targetUsername = helpers.configs("selenium")['targetusername']
    targetPassword = helpers.configs("selenium")['targetpassword']

    driver = setSeleniumProxy(burpUrl, burpProxyPort, seleniumUrl, seleniumPort, target)
    driver.get(target)
    time.sleep(5)

    element = driver.find_element_by_name('login')
    element.send_keys(targetUsername)
    element.send_keys(Keys.RETURN)
    time.sleep(5)

    element = driver.find_element_by_name('password')
    element.send_keys(targetPassword)
    element.send_keys(Keys.RETURN)
    time.sleep(5)

def seleniumRq(burpUrl, burpProxyPort, seleniumUrl, seleniumPort, target, targetList):
    driver = setSeleniumProxy(burpUrl, burpProxyPort, seleniumUrl, seleniumPort, target)

    for url in targetList:
        driver.get(url)
