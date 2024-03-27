import time
import numpy as np
from keras import Sequential
from keras.src.saving import load_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

from config import max_games, epsilon, learning_rate, discount_factor, mapping

# Опции веб-драйвера
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

# Открытие веб-страницы с игрой
driver.get("https://сапёр.com/")

win = 0

if os.path.exists("model.keras"):
    model = load_model("model.keras")
    print("Модель загружена.")
else:
    print("Модель не найдена. Создается новая модель.")
    model = Sequential([
        Dense(64, activation='relu', input_shape=(81,)),
        Dense(32, activation='relu'),
        Dense(2, activation='linear')
    ])
    model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mean_squared_error')

def right_click(element):
    action = ActionChains(driver)
    action.context_click(element).perform()


def choose_action(state, model, epsilon):
    if np.random.rand() < epsilon:
        return np.random.randint(0, 2)  # Случайное действие (0 - клик, 1 - установка флажка)
    else:
        q_values = model.predict(state)
        return np.argmax(q_values)  # Выбор действия с наибольшим Q-значением


# Игровой цикл
game_counter = 0
while game_counter < max_games:
    state = np.ones(81)  # Начальное состояние поля
    state = state.reshape(1, -1)  # Изменение формы для входа в модель

    # Игровой цикл
    while True:
        # Выбор действия
        action = choose_action(state, model, epsilon)

        if action == 0:  # Клик
            cell_index = np.random.choice(
                [i for i, val in enumerate(state.flatten()) if val == 1])  # Выбор случайной непосещенной ячейки
            cell = driver.find_element(By.XPATH, f"//div[@id='board']//img[{cell_index + 1}]")
            time.sleep(0.15)
            cell.click()
        elif action == 1:  # Установка флажка
            cell_index = np.random.choice(
                [i for i, val in enumerate(state.flatten()) if val == 1])  # Выбор случайной непосещенной ячейки
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

        # Обработка награды и обновление Q-таблицы
        # Ваш текущий код для обработки награды и обновления Q-таблицы

        if 1 not in state_after and 10 not in state_after:  # Если все ячейки открыты
            reward = 10
            print("ПОБЕДА!!!")
            f = open('ПОБЕДА.txt','w')
            win += 1

        elif 7 in state_after and 10 in state_after:
            reward = -0.5 * state_after.count(7)
            print(f"Лишний флаг {reward}")

        elif 9 in state_after:  # Если есть взорвавшаяся мина
            reward = 0.2 * state_after.count(9)
            print(f"Награда за обезвреженные мины: {reward}")

        elif 10 in state_after:
            reward = -5

        else:
            reward = 0

        # Обновление состояния для следующего шага
        state_after = np.array(state_after)
        state_after = state_after.reshape(1, -1)  # Изменение формы для входа в модель

        target = reward + discount_factor * np.max(model.predict(state_after))  # Целевое Q-значение
        target_vec = model.predict(state)
        target_vec[0][action] = target  # Обновление Q-значения для выбранного действия
        model.fit(state, target_vec, epochs=1, verbose=0)  # Обучение модели на одной эпохе

        if reward != 0 or 10 in state_after:
            break  # Выход из игрового цикла при окончании игры или взрыве мины

        state = state_after  # Обновление состояния для следующего шага

    # Перезапуск игры
    face = driver.find_element(By.XPATH, "//div[@id='playspace']//img[contains(@id, 'face')]")
    face.click()
    model.save('model.keras')
    print('Модель сохранена')
    # Обновление счетчика игр
    game_counter += 1
    print(f'Игра №{game_counter}')
print(f'Победа {win}')

