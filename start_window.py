import os.path
import sqlite3

import pygame

con = sqlite3.connect(os.path.join('data', 'UnderWater.sqlite'))
class InputLine:
    def __init__(self, x: int, y: int, width: int, height: int, text_bg: str, password=False):
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.password = password

        self.font = pygame.font.Font(None, height // 6 * 4)
        self.text = text_bg
        self.user_input = ''

        self.enter = False

    def draw(self, screen: pygame.surface.Surface):
        pygame.draw.rect(screen, '#03045e', self.rect, width=3)
        if not self.enter and self.user_input == '':
            self.inp_text = self.font.render(self.text, False, '#3c81f0')
        elif self.password and self.user_input != '':
            self.inp_text = self.font.render(len(self.user_input) * '*', False, '#03045e')
        else:
            self.inp_text = self.font.render(self.user_input, False, '#03045e')
        self.text_rect = self.inp_text.get_rect(center=self.rect.center)

        """
        Ниже стирается старый текст путем наложение такого же текста, цветом заднего фона
        """

        screen2 = pygame.surface.Surface((self.rect[2] - 6, self.rect[3] - 6))
        screen2.fill('#ade8f4')
        # text1 = self.font.render(self.text, False, '#ade8f4')
        # text2 = self.font.render(self.user_input[:-1], False, '#ade8f4')
        # text1_rect = text1.get_rect(center=self.rect.center)
        # text2_rect = text2.get_rect(center=self.rect.center)
        # screen.blit(text1, text1_rect)
        # screen.blit(text2, text2_rect)

        screen.blit(screen2, (self.rect[0] + 3, self.rect[1] + 3))
        screen.blit(self.inp_text, (self.rect[0] + 3, self.rect[1] + 3))

    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.x <= mouse[0] <= self.rect.x + self.rect.w and self.rect.y <= mouse[
            1] <= self.rect.y + self.rect.h:
            return True
        return False

    def input(self, event):
        try:
            if self.enter:
                if event.key != pygame.K_BACKSPACE:
                    if len(self.user_input) < 15:
                        self.user_input += chr(event.key)
                else:
                    self.user_input = self.user_input[:-1]
        except Exception:
            pass


class Button:
    def __init__(self, x, y, width, height, text, normal_bgcolor, hovered_bgcolor,
                 normal_textcolor, hovered_textcolor):
        self.rect = pygame.rect.Rect(x, y, width, height)

        self.font = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), width // (len(text) - 1))
        self.text = text

        self.colors = {'normal_bg': normal_bgcolor, 'hovered_bg': hovered_bgcolor, 'normal_text': normal_textcolor,
                       'hovered_text': hovered_textcolor}

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        bg_color, text_color = self.colors['normal_bg'], self.colors['normal_text']
        if self.is_clicked():
            bg_color, text_color = self.colors['hovered_bg'], self.colors['hovered_text']
        screen.fill(bg_color, self.rect)
        pygame.draw.rect(screen, self.colors['normal_text'], (self.rect.x - 1, self.rect.y - 1, self.rect.w + 1, self.rect.h + 1), 3)
        self.btn_text = self.font.render(self.text, True, text_color)
        self.text_rect = self.btn_text.get_rect(center=self.rect.center)
        screen.blit(self.btn_text, self.text_rect)

    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.x <= mouse[0] <= self.rect.x + self.rect.w and self.rect.y <= mouse[
            1] <= self.rect.y + self.rect.h:
            return True
        return False


class BaseWindow:
    def __init__(self):
        pygame.init()

        self.size = (800, 600)

        self.screen = pygame.display.set_mode(self.size)
        self.group_sprite = None

    def add_group_sprite(self, group):
        self.group_sprite = group


class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.screen.fill('#ade8f4')
        pygame.display.set_caption('Главный экран')

        btn_width, btn_height = 210, 70
        btn_login_x, btn_login_y = self.size[0] // 2 - btn_width * 1.2, self.size[1] / 2 + btn_height / 4
        btn_reg_x, btn_reg_y = self.size[0] // 2 + btn_width * 0.2, self.size[1] / 2 + btn_height / 4
        btn_records_x, btn_records_y = self.size[0] // 2 - btn_width // 2, self.size[1] / 2 + btn_height * 1.7

        normal_bg, hovered_bg = '#48cae4', '#00b4d8'
        normal_text, hovered_text = '#03045e', '#ffffff'

        self.btn_login = Button(btn_login_x, btn_login_y, btn_width, btn_height, 'Войти в аккаунт', normal_bg,
                                hovered_bg, normal_text, hovered_text)
        self.btn_reg = Button(btn_reg_x, btn_reg_y, btn_width, btn_height, 'Создать аккаунт', normal_bg,
                              hovered_bg, normal_text, hovered_text)
        self.btn_records = Button(btn_records_x, btn_records_y, btn_width, btn_height, 'Таблица рекордов', normal_bg,
                                  hovered_bg, normal_text, hovered_text)

        self.btn_group = [self.btn_login, self.btn_reg, self.btn_records]

    def display_text(self):
        f = pygame.font.Font(os.path.join('data', 'Aguante-Regular.otf'), 90)
        text = f.render('UNDERWATER', True, '#0077b6')
        x, y = self.size[0] // 2 - text.get_width() // 2, self.size[1] // 2 - text.get_width() / 3.5
        self.screen.blit(text, (x, y))

    def draw(self):
        self.display_text()
        for btn in self.btn_group:
            btn.draw(self.screen)


class LoginWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        pygame.display.set_caption('Логин')

    def draw(self):
        pass


class RegistrationWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        pygame.display.set_caption('Регистрация')

        self.screen.fill('#ade8f4')

        inp_width, inp_height = 210, 40

        inp_user_name_x, inp_user_name_y = self.size[0] / 6, self.size[1] / 10 * 2
        inp_password_x, inp_password_y = self.size[0] / 6, self.size[1] / 10 * 4
        inp_proof_password_x, inp_proof_password_y = self.size[0] / 6, self.size[1] / 10 * 6

        self.user_name = InputLine(inp_user_name_x, inp_user_name_y, inp_width, inp_height, 'Имя пользователя')
        self.password = InputLine(inp_password_x, inp_password_y, inp_width, inp_height, 'Пароль', password=True)
        self.proof_password = InputLine(inp_proof_password_x, inp_proof_password_y, inp_width, inp_height,
                                        'Подтверждение пароля', password=True)

        btn_width, btn_height = 300, 100
        btn_x, btn_y = self.size[0] / 6 * 3.5, self.size[1] / 6 * 2.3
        normal_bg, hovered_bg = '#48cae4', '#00b4d8'
        normal_text, hovered_text = '#03045e', '#ffffff'

        self.btn_reg = Button(btn_x, btn_y, btn_width, btn_height, 'Регистрация', normal_bg, hovered_bg,
                              normal_text, hovered_text)

        self.inp_group = (self.user_name, self.password, self.proof_password)

    def draw(self):
        for i in self.inp_group:
            i.draw(self.screen)
        self.btn_reg.draw(self.screen)

    def reg(self):
        username = self.user_name.user_input
        password = self.password.user_input
        proof_password = self.proof_password.user_input
        if username == '' or password == '' or proof_password == '':
            """
            Вывод текста "Поля заполнены не корректно"
            """
        elif password != proof_password:
            """
            Вывод текста "Не совпадают пароли"  
            """
        elif len(username) < 4:
            """
            Вывод текста "Имя слишком короткое, минимум 4 символа"
            """
        elif len(password) < 8:
            """
            Вывод текста "Пароль слишком короткий, минимум 8 символов"
            """
        else:
            self.add_bd(username, password, proof_password)

    def add_bd(self, username, password, proof_password):
        print(username, password, proof_password)


class RecordsWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        pygame.display.set_caption('Рекорды')

    def draw(self):
        pass


if __name__ == '__main__':
    current_window = MainWindow()
    running = True
    clock = pygame.time.Clock()
    FPS = 60
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if isinstance(current_window, MainWindow):
                    if current_window.btn_login.is_clicked():
                        current_window = LoginWindow()
                    elif current_window.btn_reg.is_clicked():
                        current_window = RegistrationWindow()
                    elif current_window.btn_records.is_clicked():
                        current_window = RecordsWindow()
                elif isinstance(current_window, RegistrationWindow):
                    if current_window.btn_reg.is_clicked():
                        current_window.reg()
                    for input_line in current_window.inp_group:
                        if input_line.is_clicked():
                            input_line.enter = True
                            for i in current_window.inp_group:
                                if i != input_line:
                                    i.enter = False
                            break
                    else:
                        for input_line in current_window.inp_group:
                            input_line.enter = False
            elif event.type == pygame.KEYDOWN:
                if isinstance(current_window, RegistrationWindow):
                    for input_line in current_window.inp_group:
                        if input_line.enter is True:
                            input_line.input(event)

        current_window.draw()
        pygame.display.flip()
    pygame.quit()
