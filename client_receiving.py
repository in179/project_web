import requests
import json
import pyautogui
from sys import platform
import pygame
from PIL import Image
import time


pygame.init()
infoObject = pygame.display.Info()
w, h = infoObject.current_w, infoObject.current_h


def move(coords, is_clicked, data, display):
    coords[0] = h * coords[0] / display[1]
    coords[1] = w * coords[0] / display[0]
    for button in data:
        pyautogui.write(button)


def draw_cursor(coords):
    # открываем изображения
    with Image.open('image.png').convert("RGBA") as img, Image.open('cursor.png').convert("RGBA") as cursor:
        # создаем новое изображение, которое будет результатом
        result = Image.new('RGBA', img.size, (0, 0, 0, 0)).convert("RGBA")
        # наложение курсора на изображение
        result.paste(img, (0, 0), img)
        result.paste(cursor, coords, cursor)
        # сохраняем результат
        result.save('image.png')


url = "https://dsfsdfdsf.pythonanywhere.com/"  # "http://127.0.0.1:5000"

# Отправляем запрос на получение ID
print("Starting receiving")


def main():
    response = requests.get(f"{url + '/api'}?id=0&os={platform}")
    print(f"{url + '/api'}?id=0&os={platform}")
    my_id = response.json()['id']
    name = f"image.png"
    # Бесконечный цикл
    while True:
        # Создаем скриншот экрана и сохраняем в файл data.png
        pyautogui.screenshot(name)
        coords = pygame.mouse.get_pos()
        draw_cursor(coords)
        files = {'file': open(name, 'rb')}
        requests.post(url + f"/upload?id={my_id}", files=files)
        # Получаем координаты и флаг клика с сервера
        response = requests.get(f"{url + '/api'}?get_for_id={my_id}")
        print(f"{url + '/api'}?get_for_id={my_id}")
        print(response)
        print(response.json())
        coords = json.loads(response.content)['coords']
        is_clicked = json.loads(response.content)['is_clicked']
        data = json.loads(response.content)['data']
        display = json.loads(response.content)['display']
        # Вызываем функцию для перемещения курсора
        move(coords, is_clicked, data, display)


if __name__ == "__main__":
    while True:
        #try:
        main()
        #except Exception as ex:
        #    print(f"No connection to server! Error {ex.__class__.__name__}")