"""Import required libraries."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


options = Options()
options.headless = False
# options.add_argument("window-size=1920x1080")

website = "https://www.audible.com/search"
driver = webdriver.Chrome(options=options)
driver.get(website)
driver.maximize_window()

pagination = driver.find_element(By.XPATH, '//ul[contains(@class, "pagingElements")]')
pages = pagination.find_elements(By.TAG_NAME, "li")
last_page = int(pages[-2].text)

current_page = 1

book_title = []
book_author = []
book_length = []

while current_page <= last_page:
    container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'adbl-impression-container')))
    # container = driver.find_element(By.CLASS_NAME, "adbl-impression-container"
    products = WebDriverWait(container, 10).until(EC.presence_of_all_elements_located((By.XPATH, './/li')))
    # products = container.find_elements(By.XPATH, "./li")

    for product in products:
        title = product.find_element(By.XPATH, './/h3[contains(@class, "bc-heading")]').text
        book_title.append(title)
        print(title)
        book_author.append(product.find_element(By.XPATH, './/li[contains(@class, "authorLabel")]').text)
        book_length.append(product.find_element(By.XPATH, './/li[contains(@class, "runtimeLabel")]').text)

    current_page += 1

    try:
        next_page = driver.find_element(By.XPATH, '//span[contains(@class, "nextButton")]')
        next_page.click()
    except:
        pass

driver.quit()

df = pd.DataFrame({'book_title': book_title, 'book_author': book_author, 'book_length': book_length})
df.to_csv('books.csv', index=False)
