import os
import shutil
import stat
from pathlib import Path

from selenium import webdriver

global driver


def add_execute_permission(path: Path, target: str = "u"):
    """Add `x` (`execute`) permission to specified targets."""
    mode_map = {
        "u": stat.S_IXUSR,
        "g": stat.S_IXGRP,
        "o": stat.S_IXOTH,
        "a": stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
    }

    mode = path.stat().st_mode
    for t in target:
        mode |= mode_map[t]

    path.chmod(mode)


def settingDriver():
    print("driver setting")
    global driver

    driverPath = "/tmp" + "/chromedriver"
    headlessPath = "/tmp" + "/headless-chromium"

    # copy and change permission
    print("copy headless-chromium")
    shutil.copyfile(os.getcwd() + "/headless-chromium", headlessPath)
    add_execute_permission(Path(headlessPath), "ug")

    print("copy chromedriver")
    shutil.copyfile(os.getcwd() + "/chromedriver", driverPath)
    add_execute_permission(Path(driverPath), "ug")

    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280x1696")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    chrome_options.add_argument("--v=99")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.binary_location = headlessPath

    PORT = int(os.environ.get("PORT", 8080))
    print("get driver")
    driver = webdriver.Chrome(driverPath, chrome_options=chrome_options, port=PORT)


def seleniumSample(request):

    settingDriver()

    global driver
    try:
        print("URL get")
        driver.get("http://www.jma.go.jp/jma/index.html")
        targetPath = '//img[@src="/jma/com/images/logo.gif"]'
        ret = driver.find_element_by_xpath(targetPath)
        ret = ret.get_attribute("alt")
        print(ret)

    finally:
        print("driver quit")
        driver.quit()

    return ret
