# GoogleFormにアクセス、データを追記して送信する
import os
import shutil
import stat
from pathlib import Path
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

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
    driver = webdriver.Chrome(driverPath, chrome_options=chrome_options, port=PORT)
    print("get driver")


def googleFormSend(request):
    """
    googleFormに直接データを記入＆送信
    [input] id:googleFormのID(string), data:{"項目" : 値}(dict)
    [output] 成功/失敗
    """
    ret = False

    # get InputData(json)
    request_json = request.get_json()
    if request_json and "id" in request_json:
        googleFormId = request_json["id"]

    if request_json and "data" in request_json:
        addDict = request_json["data"]

    # set Google Driver
    settingDriver()

    # set value & send to googleForm
    global driver
    url = "https://docs.google.com/forms/d/e/"
    url += googleFormId
    url += "/viewform?embedded=true"

    try:
        # open
        driver.set_window_size(1920, 1080)
        driver.get(url)
        print("driver.get")

        # waiting sendBtn clickable
        sendBtn = '//div[@role="button"]'
        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, sendBtn)))

        # set inputData
        print("set InputData")
        targetPath = '//input[@class="quantumWizTextinputPaperinputInput exportInput"]'
        inputList = driver.find_elements_by_xpath(targetPath)
        for i in inputList:
            lbl = i.get_attribute("aria-label")
            print("(%s, %s)" % (lbl, addDict[lbl]))
            i.send_keys(addDict[lbl])

        # submit
        driver.find_element_by_xpath(sendBtn).click()
        print("submit")
        ret = True

    finally:
        driver.quit()
        print("driver quit")

    return json.dumps({"result": ret})
