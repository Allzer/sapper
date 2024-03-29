import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import joblib

from config import max_games, epsilon, learning_rate, discount_factor, mapping
victory = 0

# Опции веб-драйвера
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

# Открытие веб-страницы с игрой
driver.get("https://сапёр.com/")

try:
    Q_table = joblib.load("Q_table.pkl")
    print("Q-таблица загружена.")
except FileNotFoundError:
    print("Q-таблица не найдена. Создается новая таблица.")
    Q_table = {}


def right_click(element):
    action = ActionChains(driver)
    action.context_click(element).perform()


def choose_action(state, Q_table, epsilon):
    Q_table[state] = Q_table.get(state, np.zeros(2))  # Создание записи для нового состояния
    if np.random.rand() < epsilon:
        return np.random.randint(0, 2)  # Случайное действие (0 - клик, 1 - установка флажка)
    else:
        return np.argmax(Q_table[state])  # Выбор действия с наибольшим значением в Q-таблице




# Игровой цикл
game_counter = 0
while game_counter < max_games:
    state = tuple([1] * 81)  # Начальное состояние
    # Игровой цикл
    while True:
        # Выбор действия
        action = choose_action(state, Q_table, epsilon)

        if action == 0:  # Клик
            cell_index = np.random.choice(
                [i for i, val in enumerate(state) if val == 1])  # Выбор случайной непосещенной ячейки
            cell = driver.find_element(By.XPATH, f"//div[@id='board']//img[{cell_index + 1}]")
            time.sleep(0.15)
            cell.click()
        elif action == 1:  # Установка флажка
            cell_index = np.random.choice(
                [i for i, val in enumerate(state) if val == 1])  # Выбор случайной непосещенной ячейки
            cell = driver.find_element(By.XPATH, f"//div[@id='board']//img[{cell_index + 1}]")
            time.sleep(0.15)
            right_click(cell)

        # Получение нового состояния поля
        cells = driver.find_elements(By.XPATH, "//div[@id='board']//img[contains(@style, 'left')]")
        state_after = []
        for cell in cells:
            cell_style = cell.get_attribute("src")
            for k, v in mapping.items():
                if k in cell_style:
                    state_after.append(v)

        if 1 not in state_after and 10 not in state_after:  # Если все ячейки открыты
            reward = 10
            victory = open('Победа.txt','w')
            victory.write(f'{time.time()}')
            print("ПОБЕДА!!!")

        elif 7 in state_after and 10 in state_after:
            reward = -0.5 * state_after.count(7)
            print("Лишний флаг")

        elif 9 in state_after:  # Если есть взорвавшаяся мина
            reward = 0.2 * state_after.count(9)
            print(f"Награда за обезвреженные мины: {reward}")

        elif 10 in state_after:
            reward = -5

        else:
            reward = 0
        Q_table[tuple(state_after)] = Q_table.get(tuple(state_after), np.zeros(2))
        Q_table[tuple(state_after)][action] += learning_rate * (reward + discount_factor * np.max(Q_table.get(tuple(state_after), np.zeros(2))) -
                    Q_table[tuple(state_after)][action])

        if reward != 0 or 10 in state_after:
            break  # Выход из игрового цикла при окончании игры или взрыве мины

        state = tuple(state_after)  # Выбор нового состояния из открытых ячеек

    # Перезапуск игры
    face = driver.find_element(By.XPATH, "//div[@id='playspace']//img[contains(@id, 'face')]")
    face.click()

    # Сохранение Q-таблицы после каждой игры
    joblib.dump(Q_table, "Q_table.pkl")
    # print("Q-таблица сохранена.")
    game_counter += 1  # Увеличение счетчика игр

    print(f'Игра №{game_counter}')
