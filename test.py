import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from config import mapping

def split(array, n):
    return [array[i:i + n] for i in range(0, len(array), n)]

# Опции веб-драйвера
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

# Открытие веб-страницы с игрой
driver.get("https://сапёр.com/")

cells = driver.find_elements(By.XPATH, "//div[@id='board']//img[contains(@style, 'left')]")
state_after = []
for cell in cells:
    cell_style = cell.get_attribute("src")

    for k, v in mapping.items():
        if k in cell_style:
            state_after.append(v)

state_after_split = split(state_after, 9)
state_block = []
for i in range(len(state_after_split)):
    state_block.append(state_after_split[i:i+3:1])

state_block = state_block[:-2]
for i in state_block:
    print(i)





