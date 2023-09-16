import platform,time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as OptionsChrome
from selenium.webdriver.ie.options import Options as OptionsIE
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service

TIME_OUT_WEB=30

class SeleniumLayer:    
    def __init__(self, log, dir_in, dir_path, dir_out):
        self.log = log
        self.dir_path = dir_path
        self.dir_in = dir_in
        self.dir_out = dir_out
        log = log

    def iniciar_driver_chrome(self):        
        ###################### CHROME - DRIVER ######################
        # Path Chromedriver
        if (platform.system().lower()=="linux"): chrome_path='/usr/bin/chromedriver'
        elif (platform.system().lower()=="windows"): chrome_path=os.path.join(self.dir_path,"chromedriver.exe")

        # Capabillities - Options
        caps_chrome = DesiredCapabilities().CHROME
        caps_chrome["pageLoadStrategy"] = "normal"
        opts_chrome = OptionsChrome()
        opts_chrome.add_argument("disable-infobars")
        opts_chrome.add_argument("--disable-extensions")
        opts_chrome.add_argument("no-sandbox")
        opts_chrome.add_argument("disable-gpu")
        opts_chrome.add_argument("lang=es")
        opts_chrome.add_argument("test-type")
        opts_chrome.add_argument("force-renderer-accessibility")
        opts_chrome.add_argument("disable-web-security")
        opts_chrome.add_argument("disable-extensions")
        opts_chrome.add_argument("allow-insecure-localhost")
        opts_chrome.add_argument("ignore-ssl-errors=yes")
        opts_chrome.add_argument("ignore-certificate-errors")
        opts_chrome.add_argument("--log-level=3")
        opts_chrome.add_argument("safebrowsing-disable-download-protection")
        prefs = {"download.default_directory" : self.dir_in}
        opts_chrome.add_experimental_option("prefs",prefs)
        #####################################################

        self.log.debug("############### Inicio Cargar Chrome ###############")
        inicio=time.time()
        self.log.debug ("Chrome Caps: ")
        self.log.debug (caps_chrome)
        self.log.debug ("Chrome Path: "+ chrome_path)
        self.log.debug ("Chrome Opts: ")
        self.log.debug (opts_chrome)
        try:
            self.log.debug ("Iniciando WebDriver")
            service = Service(executable_path= chrome_path)
            self.driver = webdriver.Chrome(service= service)
            self.driver.set_page_load_timeout(TIME_OUT_WEB*2)
            
            
            
        except Exception as e:
            self.log.error("Ocurrio un error con el ChromeDriver")
            raise Exception(e)
        
        self.log.debug("## Tiempo transcurrido: " + str(time.time()-inicio))
        self.log.debug("############### Fin Cargar Chrome ###############")
        

    def quit_driver_chrome(self):
        self.driver.quit()

    def navegar_url_chrome(self, url):
        self.log.debug("############### Navegar URL ###############")
        inicio=time.time()    
        try:
            self.log.debug ("Cargando url: " + url)
            self.driver.get(url)
        except Exception as e:
            self.log.error("Ocurrio un error con el ChromeDriver")
            raise Exception(e)
    

    def clear_visible_element_by_id(self, id):
        WebDriverWait( self.driver, TIME_OUT_WEB).until(
            EC.visibility_of_element_located((By.ID, id))
        ).clear()

    def click_visible_element_by_xpath(self, xpath):
         WebDriverWait( self.driver, TIME_OUT_WEB).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        ).click()

    def send_key_visible_element_by_id(self, id, data):
        WebDriverWait( self.driver, TIME_OUT_WEB).until(
            EC.visibility_of_element_located((By.ID, id))
        ).send_keys(data)
    
    def send_key_visible_element_by_name(self, name, data):
        WebDriverWait( self.driver, TIME_OUT_WEB).until(
            EC.visibility_of_element_located((By.NAME, name))
        ).send_keys(data)    
    

    def click_visible_element_by_id(self, id):
        WebDriverWait(self.driver, TIME_OUT_WEB).until(
            EC.visibility_of_element_located((By.ID, id))
        ).click()

    def click_located_element_id(self, id):
        WebDriverWait( self.driver, TIME_OUT_WEB).until(
            EC.presence_of_element_located((By.ID, id))
        ).click()
    
    def send_key_located_element_by_id(self, id, data):
        WebDriverWait( self.driver, TIME_OUT_WEB).until(
            EC.presence_of_element_located((By.ID, id))
        ).send_keys(data)

    def select_by_value_located_by_id(self, id, value):
        Select(WebDriverWait( self.driver, TIME_OUT_WEB).until(
             EC.presence_of_element_located((By.ID, id))
        )).select_by_value(value)

    def select_by_value_located_by_xpath(self, xpath, value):
        Select(WebDriverWait( self.driver, TIME_OUT_WEB).until(
             EC.presence_of_element_located((By.XPATH, xpath))
        )).select_by_value(value)

    def check_exists_visible_element_by_id(self, id):
        try:
            elements=WebDriverWait(self.driver, 5).until(EC.visibility_of_all_elements_located((By.ID, id)))
            return len(elements)>0
        except:
            return False
        
    def check_exists_visible_element_by_xpath(self, xpath):
        try:
            elements=WebDriverWait(self.driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))
            return len(elements)>0
        except:
            return False
        
    def check_exists_visible_element_by_name(self, name):
        try:
            elements=WebDriverWait(self.driver, 5).until(EC.visibility_of_all_elements_located((By.NAME, name)))
            return len(elements)>0
        except:
            return False
    
    def check_checkbox_is_selected_by_xpath(self, xpath):
        elements=WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return elements.is_selected()

    def get_exists_visible_element_by_xpath(self, xpath):        
        elements=WebDriverWait(self.driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))
        return elements

    def get_text_element(self, element):                
        return element.text
    
    def download_imagen_by_xpath(self, xpath, path, element=None):
        
        if element == None:
            with open(path, 'wb') as file:
                file.write(WebDriverWait( self.driver, TIME_OUT_WEB).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                ).screenshot_as_png)
        else:
            element.find_element(By.XPATH,xpath).screenshot(path)
        
        time.sleep(0.3)


        
        
    
      
    
        