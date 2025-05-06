from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import pyautogui as pt

def requestClima(driver, listInfo):
    tagTemp=driver.find_element(By.CLASS_NAME, 'summaryTemperatureCompact-DS-EntryPoint1-1.summaryTemperatureHover-DS-EntryPoint1-1')
    tagSens=driver.find_elements(By.TAG_NAME, 'div')
    for a in tagSens:
        if a.text:
            print(a.text)
        if len(a.text)==3:
            print(a.text)
    listInfo.append(tagTemp.text[0:2])
    return listInfo

def requestNav(url, cidade):
    driver = webdriver.Edge()
    listInfo=list()
    try:
        driver.get(f'{url}')
        sleep(1)
        inputDriver=driver.find_element(By.CLASS_NAME, 'textField-DS-EntryPoint1-1.textField-DS-EntryPoint1-2')
        sleep(1)
        driver.execute_script("document.querySelector('button#onetrust-reject-all-handler').click()")
        sleep(1)
        try:
            inputDriver.send_keys(f'{cidade}')
            sleep(1)
            pt.press('enter')
            sleep(1)
            requestClima(driver,listInfo)
            print(listInfo)
        except:
            print('Cidade invalida')
        sleep(20)
        driver.quit()
    except:
        print('Error url invalida')
    return

requestNav('https://www.msn.com/pt-br/clima/forecast/in-Cuiab%C3%A1?loc=eyJsIjoiQ3VpYWLDoSIsImkiOiJCUiIsImciOiJwdC1iciIsIngiOiItNTYuMDk3NzI4NzI5MjQ4MDUiLCJ5IjoiLTE1LjU4ODg1NzY1MDc1NjgzNiJ9&weadegreetype=C&ocid=msedgntp&cvid=4c2f76b3eba647a6a590d2cb98c6707e', 'piaui')
