import pygame
import requests
import pyautogui
from PIL import Image


class Button:
    def __init__(self, x, y, width, height, text, id):
        self.rect = pygame.Rect(x, y, width, height)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.color = self.black
        self.border_color = black
        self.button_color = white
        self.hover_color = (0, 0, 255)
        self.text = text
        self.id = id

    def draw(self, surface):
        pygame.draw.rect(surface, self.button_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, width=5)
        font = pygame.font.Font(None, 24)
        text = font.render(self.text, True, self.color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def check_on(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color = self.hover_color
        else:
            self.color = self.black

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            return self.id
        return -1


# Инициализация Pygame
pygame.init()

# Установка размеров окна
win_size = (1920, 1000)
screen = pygame.display.set_mode(win_size)

# Установка заголовка окна
pygame.display.set_caption("Авторизация")

# Установка цветов
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

infoObject = pygame.display.Info()
w, h = infoObject.current_w, infoObject.current_h

# Установка шрифтов
font = pygame.font.SysFont(None, 30)

# Установка URL-адреса для запросов
url = 'https://dsfsdfdsf.pythonanywhere.com'  # "http://127.0.0.1:5000"

# Подключение к базе данных
print("Starting client")


# Функция для отображения текста на экране
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()


# Функция для отображения сообщения об ошибке
def message_display(text):
    TextSurf, TextRect = text_objects(text, font)
    TextRect.center = ((win_size[0] / 2), 25)
    screen.blit(TextSurf, TextRect)
    pygame.display.update()


# Функция для проверки логина и пароля в базе данных
def check_login(username, password):
    r = requests.get(url + f'/check_login?username={username}&password={password}')
    return r.json()["res"]


# Функция для получения списка данных
def get_data():
    r = requests.get(url + '/get_data')
    res = r.json()
    return res


# Функция для получения изображения
def get_image(id, name):
   # try:
    response = requests.get(url + f'/download?id={id}')
    with open(name, 'wb') as f:
        f.write(response.content)
    f.close()
    img = Image.open(name)
    # изменяем размер
    new_image = img.resize((1920, 980))
    new_image.save(name)
    return True
    #except Exception as ex:
    #    print(ex.__class__.__name__)
    #    return False


# Функция для отправки координат и состояния мыши
def send_mouse(coords, is_clicked, data, img_id, display):
    params = {'coords': str(coords), 'is_clicked': is_clicked, "data": data, "display":display}
    r = requests.post(url + f"/api?moving={img_id}", data=params)


def check_connection():
    r = requests.get(url + "/check_connection")
    return r.json()


# Функция для отображения списка данных на экране
def show_data(data, buttons):
    x = 50
    y = 100
    for d in sorted(list(data.keys())):
        button_text = f"{d}. {data[d]}"
        buttons.append(Button(x, y, 150, 50, button_text, d))
        y += 75


# Функция для запуска проекта
def main():
    print(pygame.key.get_pressed())
    # Отображение окна авторизации
    check_connection()
    login = ""
    password = ""
    login_input_rect = pygame.Rect(250, 200, 300, 50)
    password_input_rect = pygame.Rect(250, 300, 300, 50)
    login_active = True
    password_active = False
    time_to_check = False
    was_checked = False
    while True:
        check_connection()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_input_rect.collidepoint(event.pos):
                    login_active = True
                    password_active = False
                    time_to_check = False
                    was_checked = False
                elif password_input_rect.collidepoint(event.pos):
                    login_active = False
                    password_active = True
                    time_to_check = False
                    was_checked = False
                else:
                    login_active = False
                    password_active = False
                    time_to_check = True
                    was_checked = False
            if event.type == pygame.KEYDOWN:
                if login_active:
                    if event.key == pygame.K_RETURN:
                        password_active = True
                        login_active = False
                        time_to_check = False
                        was_checked = False
                    elif event.key == pygame.K_BACKSPACE:
                        login = login[:-1]
                    else:
                        login += event.unicode
                elif password_active:
                    if event.key == pygame.K_RETURN:
                        time_to_check = True
                        check_login(login, password)
                    elif event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        password += event.unicode
        screen.fill(white)
        login_input_text = font.render("Login: " + login, True, black)
        password_input_text = font.render("Password: " + "*" * len(password), True, black)
        pygame.draw.rect(screen, black, login_input_rect, 2)
        pygame.draw.rect(screen, black, password_input_rect, 2)
        screen.blit(login_input_text, (login_input_rect.x + 5, login_input_rect.y + 5))
        screen.blit(password_input_text, (password_input_rect.x + 5, password_input_rect.y + 5))
        print(time_to_check)
        if time_to_check and check_login(login, password):
            pygame.display.set_caption("Online OS")
            data = {0: "Close"}
            k = get_data()
            for e in k.keys():
                data[int(e)] = k[e]
            print(data)
            buttons = []
            show_data(data, buttons)
            image_id = 0
            flag = True
            while flag:
                check_connection()
                screen.fill(white)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                for b in buttons:
                    b.draw(screen)
                    b.check_on(pygame.mouse.get_pos())
                    idd = b.check_click(pygame.mouse.get_pos())
                    if idd != -1:
                        flag = False
                        image_id = idd
                        break
                pygame.display.flip()
            if image_id == 0:
                quit(0)
            while True:
                check_connection()
                data = []
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit(0)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        coords = pygame.mouse.get_pos()
                        is_clicked = event.button == 1
                        send_mouse(coords, is_clicked, data, image_id, (w, h))
                name = "response.png"
                while not get_image(image_id, name):
                    pass
                while True:
                    check_connection()
                    data = []
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit(0)
                        if event.type == pygame.KEYDOWN:
                            data.append(event.unicode)
                            print(event.unicode)
                    while not get_image(image_id, name):
                        pass
                    screen.blit(pygame.image.load(name), (0, 0))
                    pygame.display.flip()
                    coords = pygame.mouse.get_pos()
                    is_clicked = pygame.mouse.get_pressed()[0]
                    size_display = w, h
                    send_mouse(coords, is_clicked, data, image_id, size_display)
                    print("here!", data, coords, is_clicked, size_display)
                pygame.display.flip()
        elif time_to_check and not check_login(login, password):
            message_display("Login failed. Please try again.")
            time_to_check = False
            was_checked = True
        elif was_checked:
            message_display("Login failed. Please try again.")
        pygame.display.flip()


if __name__ == "__main__":
    while True:
        main()
        '''
        try:
            main()
        except Exception as ex:
            screen.fill(white)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            name = ex.__class__.__name__
            print(f"No connection to server! Error {name}")
            message_display(name)
            pygame.display.flip()
        '''