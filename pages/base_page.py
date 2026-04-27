from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))
    def click(self, locator):
        self.find_element(locator).click()