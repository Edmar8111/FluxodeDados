from selenium import webdriver
import pyautogui as pt
import threading
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

#configuração referente a anulação de verificação de conta no navegador
options = Options()
#options.add_argument("--proxy-server=http://192.168.0.24:8080") #define um proxy para o acesso

options.add_argument("--ignore-certificate-errors")
options.add_argument("--start-maximized")

#options.add_argument("--disable-sync") #Desativa a sincronização com a conta do google
#options.add_argument("--disable-background-networking") #Desativa conexoes feitas em segundo plano
#options.add_argument("--no-first-run") #Impede a execução do assistente de "primeira vez"
#options.add_argument("--no-default-browser-check") #Impede que o navegador questione para ser navegador padrão
#options.add_argument("--disable-default-apps") #Desativa os aplicativos padrão do chrome
#options.add_argument("--disable-popup-blocking") #Desativa o bloqueador de popups
#options.add_argument("--disable-translate") #Desativa o tradutor automatico do chrome
#options.add_argument("--headless") #Executa o navegador sem a interface grafica ativa
#options.add_argument("--disable-gpu") #desativa o uso da gpu
#options.add_argument("--remote-debugging-port=9222") #ativa o chromeDevtools na porta 9222

driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
def clicar_certificado():
	sleep(2.5)
	pt.press('enter')
	sleep(10)
thread=threading.Thread(target=clicar_certificado)


driver.set_page_load_timeout(10)

#driver.get('https://google.com')
sleep(1)
#bt=driver.find_element(By.CLASS_NAME, 'ui-link.ui-widget')
#print(driver.find_element(By.CLASS_NAME, 'ui-outputlabel.ui-widget').text)

try:
	thread.start()	#efetua a execução da função em simultaneo com as linhas seguintes
	driver.get('https://www.sefaz.mt.gov.br/acesso/pages/login/login.xhtml')
	driver.execute_script("document.querySelectorAll('div.form-group')[7].children[1].click()")
	thread.join() #aguarda a finalização do thread para continuar a execução	
	sleep(1)
	driver.execute_script("document.querySelectorAll('div.ui-helper-hidden-accessible')[1].children[0].value='CONTABILISTA'")
	driver.find_element(By.CLASS_NAME, 'btnPadrao').click()
	sleep(5)
	driver.execute_script("document.querySelector('iframe#iframeMenu').contentDocument.querySelectorAll('a')[103].click()")
except TimeoutException as e:
	print(driver.execute_script("return document.readyState"))
	print(f'Requisitou erro {e}')
	

sleep(5)
driver.quit()