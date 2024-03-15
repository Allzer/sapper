import numpy as np
import cv2
import mss

# Установите новые размеры окна браузера
new_width = 170  # Новая ширина окна
new_height = 700  # Новая высота окна

# Загрузите шаблоны изображений
place = cv2.imread("img/place.png", cv2.IMREAD_GRAYSCALE)
one = cv2.imread("img/one.png", cv2.IMREAD_GRAYSCALE)
two = cv2.imread("img/wo.png", cv2.IMREAD_GRAYSCALE)
pustaia = cv2.imread("img/pustaia.png", cv2.IMREAD_GRAYSCALE)
mina = cv2.imread("img/mina.png", cv2.IMREAD_GRAYSCALE)

# Создайте список шаблонов и их имена
templates = [place, one, two, pustaia, mina]
template_names = ['place', 'one', 'two', 'pustaia', 'mina']

# Определите область экрана, содержащую только игровое поле
game_region = {"top": 100, "left": 0, "width": 500, "height": 500}

# Создайте экземпляр объекта mss для захвата скриншотов с экрана монитора
with mss.mss() as sct:
    while True:
        # Захватите изображение с игровым полем
        screenshot = sct.grab(game_region)
        frame_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

        for template, name in zip(templates, template_names):
            # Выполните сопоставление шаблона
            result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)

            # Найдите локацию с наибольшим совпадением
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Отобразите результат сопоставления (для отладки)
            if max_val > 0.:  # Пороговое значение для совпадения
                print(f"Found {name} at location {max_loc}")

        # Покажите изображение
        cv2.imshow("Game Field", frame_gray)

        # Нажмите 'q' для выхода из цикла
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()