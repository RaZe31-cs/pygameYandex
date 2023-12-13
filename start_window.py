import hashlib
import math
import os.path
import sqlite3
import time

import pygame

con = sqlite3.connect(os.path.join('data', 'UnderWater.sqlite'))

cur = con.cursor()

SECRET_WORD = 'соль'


def hash_password(password):
    if hash:
        return hashlib.md5(password.encode()).hexdigest()


current_username = {'username': ''}


class BaseLevel:
    pass


class Level1(BaseLevel):
    def __init__(self):
        super().__init__()
        print('Левел в разработке')


class Level2(BaseLevel):
    def __init__(self):
        super().__init__()
        print('Левел в разработке')


class Level3(BaseLevel):
    def __init__(self):
        super().__init__()
        print('Левел в разработке')


class Level4(BaseLevel):
    def __init__(self):
        super().__init__()
        print('Левел в разработке')


class Level5(BaseLevel):
    def __init__(self):
        super().__init__()
        print('Левел в разработке')


class InputLine:
    def __init__(self, x: int, y: int, width: int, height: int, text_bg: str, password=False):
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.password = password

        self.font = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), height // 3)
        self.text = text_bg
        self.user_input = ''

        self.enter = False

    def draw(self, screen: pygame.surface.Surface):
        pygame.draw.rect(screen, '#ade8f4', self.rect)
        pygame.draw.rect(screen, '#03045e', self.rect, width=3)
        if not self.enter and self.user_input == '':
            self.inp_text = self.font.render(self.text, True, '#3c81f0')
        elif self.password and self.user_input != '':
            self.inp_text = self.font.render(len(self.user_input) * '*', True, '#03045e')
        else:
            self.inp_text = self.font.render(self.user_input, False, '#03045e')
        self.text_rect = self.inp_text.get_rect(center=self.rect.center)
        self.draw_cursor(screen)
        screen.blit(self.inp_text, self.text_rect)

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
                        self.user_input += event.unicode
                else:
                    self.user_input = self.user_input[:-1]
        except Exception:
            pass

    def draw_cursor(self, screen):
        if self.enter and time.time() % 1 > 0.5:
            self.cursor = pygame.Rect(self.inp_text.get_rect(center=self.rect.center).topright,
                                      (3, self.inp_text.get_rect(center=self.rect.center).h + 2))
            self.cursor.midleft = self.inp_text.get_rect(center=self.rect.center).midright
            pygame.draw.rect(screen, 'white', self.cursor)


class Button:
    def __init__(self, x, y, width, height, text, normal_bgcolor, hovered_bgcolor,
                 normal_textcolor, hovered_textcolor):
        self.rect = pygame.rect.Rect(x, y, width, height)

        size = width // (len(text) - 1)
        self.font = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), size if size < 20 else 20)
        self.text = text

        self.colors = {'normal_bg': normal_bgcolor, 'hovered_bg': hovered_bgcolor, 'normal_text': normal_textcolor,
                       'hovered_text': hovered_textcolor}

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        bg_color, text_color = self.colors['normal_bg'], self.colors['normal_text']
        if self.is_clicked():
            bg_color, text_color = self.colors['hovered_bg'], self.colors['hovered_text']
        screen.fill(bg_color, self.rect)
        pygame.draw.rect(screen, self.colors['normal_text'],
                         (self.rect.x - 1, self.rect.y - 1, self.rect.w + 1, self.rect.h + 1), 3)
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
        pygame.display.set_caption('Вход')

        self.screen.fill('#ade8f4')

        inp_width, inp_height = 320, 50

        inp_user_name_x, inp_user_name_y = self.size[0] // 2 - inp_width // 2, self.size[1] / 10 * 3.5
        inp_password_x, inp_password_y = self.size[0] // 2 - inp_width // 2, self.size[1] / 10 * 5

        self.user_name = InputLine(inp_user_name_x, inp_user_name_y, inp_width, inp_height, 'Имя пользователя')
        self.password = InputLine(inp_password_x, inp_password_y, inp_width, inp_height, 'Пароль', password=True)

        self.inp_group = (self.user_name, self.password)

        btn_width, btn_height = 220, 50
        self.enter_btn = Button(self.size[0] // 2 - btn_width // 2, self.size[1] // 4 * 2.9, btn_width, btn_height,
                                'Войти', '#48cae4', '#00b4d8', '#03045e', '#ffffff')
        self.exit_btn = Button(20, 20, 50, 50, '', '#48cae4', '#00b4d8', '#03045e', '#ffffff')
        self.error = False
        self.error_text = ''

    def display_text(self):
        f = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), 50)
        text = f.render('Вход', True, '#0077b6')
        x, y = self.size[0] / 2 - text.get_width() / 2, text.get_height() * 2
        self.screen.blit(text, (x, y))

    def exit_btn_draw(self):
        fullname = os.path.join('data', 'exit.png')
        self.image = pygame.image.load(fullname)
        self.exit_btn.draw(self.screen)
        self.rect = self.image.get_rect()
        self.rect.x = self.exit_btn.rect.x + (self.exit_btn.rect.w // 2 - self.rect.w // 2)
        self.rect.y = self.exit_btn.rect.y + (self.exit_btn.rect.h // 2 - self.rect.h // 2)
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

    def draw(self):
        self.screen.fill('#ade8f4')
        self.display_text()
        for i in self.inp_group:
            i.draw(self.screen)
        self.enter_btn.draw(self.screen)
        self.exit_btn_draw()
        if self.error:
            f = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), 15)
            text = f.render(self.error_text, True, '#0077b6')
            x, y = self.size[0] // 2 - text.get_width() // 2, self.size[1] // 2 + text.get_height() * 6.8
            self.screen.blit(text, (x, y))

    def check_input(self):
        self.error, self.error_text = False, ''
        for i in self.inp_group:
            if i.user_input == '':
                self.error = True
                self.error_text = 'Заполните все поля'
                break
        username = self.user_name.user_input
        password = hash_password(self.password.user_input + SECRET_WORD)
        try:
            data = cur.execute(f"""SELECT * from Players
                                    where username = '{username}'""").fetchone()
            if password != data[2]:
                self.error = True
                self.error_text = 'Неверный пароль'
            else:
                current_username['username'] = username
        except Exception as e:
            self.error = True
            self.error_text = 'Такого пользователя не существует'
        return self.error

    def next_input(self):
        for i in range(len(self.inp_group)):
            if self.inp_group[i].enter:
                self.inp_group[i].enter = False
                if i == len(self.inp_group) - 1:
                    self.inp_group[0].enter = True
                else:
                    self.inp_group[i + 1].enter = True
                break


class RegistrationWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        pygame.display.set_caption('Регистрация')

        self.screen.fill('#ade8f4')

        inp_width, inp_height = 320, 50

        inp_user_name_x, inp_user_name_y = self.size[0] // 2 - inp_width // 2, self.size[1] / 10 * 2.5
        inp_password_x, inp_password_y = self.size[0] // 2 - inp_width // 2, self.size[1] / 10 * 4
        inp_proof_password_x, inp_proof_password_y = self.size[0] // 2 - inp_width // 2, self.size[1] / 10 * 5.5

        self.user_name = InputLine(inp_user_name_x, inp_user_name_y, inp_width, inp_height, 'Имя пользователя')
        self.password = InputLine(inp_password_x, inp_password_y, inp_width, inp_height, 'Пароль', password=True)
        self.proof_password = InputLine(inp_proof_password_x, inp_proof_password_y, inp_width, inp_height,
                                        'Подтверждение пароля', password=True)

        self.error_text = ''

        btn_width, btn_height = 220, 50
        btn_x, btn_y = self.size[0] / 6 * 2, self.size[1] / 6 * 4
        normal_bg, hovered_bg = '#48cae4', '#00b4d8'
        normal_text, hovered_text = '#03045e', '#ffffff'

        self.btn_reg = Button(self.size[0] // 2 - btn_width // 2, self.size[1] // 4 * 3.2, btn_width, btn_height,
                              'Регистрация', normal_bg, hovered_bg,
                              normal_text, hovered_text)
        self.exit_btn = Button(20, 20, 50, 50, '', normal_bg, hovered_bg, normal_text, hovered_text)

        self.inp_group = (self.user_name, self.password, self.proof_password)

        self.font = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), 15)

    def display_text(self):
        f = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), 45)
        text = f.render('Регистрация', True, '#0077b6')
        x, y = self.size[0] / 2 - text.get_width() / 2, self.size[1] / 2 - text.get_width() / 1.5
        self.screen.blit(text, (x, y))

    def exit_btn_draw(self):
        fullname = os.path.join('data', 'exit.png')
        self.image = pygame.image.load(fullname)
        self.exit_btn.draw(self.screen)
        self.rect = self.image.get_rect()
        self.rect.x = self.exit_btn.rect.x + (self.exit_btn.rect.w // 2 - self.rect.w // 2)
        self.rect.y = self.exit_btn.rect.y + (self.exit_btn.rect.h // 2 - self.rect.h // 2)
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

    def error_message(self):
        if self.error_text:
            text = self.font.render(self.error_text, True, '#3c81f0')
            x, y = self.size[0] // 2 - text.get_width() // 2, self.size[1] // 4 * 3
            self.screen.blit(text, (x, y))

    def draw(self):
        self.screen.fill('#ade8f4')
        self.display_text()
        for i in self.inp_group:
            i.draw(self.screen)
        self.btn_reg.draw(self.screen)
        self.exit_btn_draw()
        self.error_message()

    def reg(self):
        self.error_text = ''
        username = self.user_name.user_input
        password = self.password.user_input
        proof_password = self.proof_password.user_input
        if username == '' or password == '' or proof_password == '':
            self.error_text = 'Поля заполнены некорректно'
        elif password != proof_password:
            self.error_text = "Пароли не совпадают"
        elif len(username) < 4:
            self.error_text = "Имя слишком короткое, минимум 4 символа"
        elif len(password) < 8:
            self.error_text = "Пароль слишком короткий, минимум 8 символов"
        else:
            if self.add_bd(username, password):
                current_username['username'] = username
                return True
            return False

    def add_bd(self, username, password):
        password = hash_password(password + SECRET_WORD)
        try:
            cur.execute("""
            INSERT INTO Players(username, password, progress) VALUES(?, ?, ?)
            """, (username, password, 1))
            id = cur.execute("""SELECT id FROM Players WHERE username = ?""", (username,)).fetchone()
            cur.execute("""
            INSERT INTO Levels_Progress(player_id, level1_star, level2_star, level3_star, level4_star, level5_star) 
            VALUES(?, 0, 0, 0, 0, 0)
            """, (*id,))
            con.commit()
            return True
        except Exception as e:
            self.error_text = "Такое имя пользователя существует"
            self.error_message()
            return False

    def next_input(self):
        for i in range(len(self.inp_group)):
            if self.inp_group[i].enter:
                self.inp_group[i].enter = False
                if i == len(self.inp_group) - 1:
                    self.inp_group[0].enter = True
                else:
                    self.inp_group[i + 1].enter = True
                break


class RecordsWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        pygame.display.set_caption('Рекорды')

    def draw(self):
        pass


class LevelMenu(BaseWindow):
    def __init__(self):
        super().__init__()
        pygame.display.set_caption('Выбор уровня')
        self.screen.fill('#ade8f4')

        btn_width = btn_height = 70

        btn_level1_x, btn_level1_y = self.size[0] / 10 * 2, self.size[1] / 4
        btn_level2_x, btn_level2_y = self.size[0] / 10 * 4.5, self.size[1] / 4
        btn_level3_x, btn_level3_y = self.size[0] / 10 * 7, self.size[1] / 4
        btn_level4_x, btn_level4_y = self.size[0] / 10 * 3.23, self.size[1] / 6 * 3
        btn_level5_x, btn_level5_y = self.size[0] / 10 * 5.7, self.size[1] / 6 * 3

        normal_bg, hovered_bg = '#48cae4', '#00b4d8'
        normal_text, hovered_text = '#03045e', '#ffffff'

        self.btn_level1 = Button(btn_level1_x, btn_level1_y, btn_width, btn_height, ' 1 ', normal_bg, hovered_bg,
                                 normal_text, hovered_text)
        self.btn_level2 = Button(btn_level2_x, btn_level2_y, btn_width, btn_height, ' 2 ', normal_bg, hovered_bg,
                                 normal_text, hovered_text)
        self.btn_level3 = Button(btn_level3_x, btn_level3_y, btn_width, btn_height, ' 3 ', normal_bg, hovered_bg,
                                 normal_text, hovered_text)
        self.btn_level4 = Button(btn_level4_x, btn_level4_y, btn_width, btn_height, ' 4 ', normal_bg, hovered_bg,
                                 normal_text, hovered_text)
        self.btn_level5 = Button(btn_level5_x, btn_level5_y, btn_width, btn_height, ' 5 ', normal_bg, hovered_bg,
                                 normal_text, hovered_text)

        self.exit_btn = Button(20, 20, 50, 50, '', '#48cae4',
                               '#00b4d8', '#03045e', '#ffffff')

        self.group_btn = (
            self.btn_level1, self.btn_level2, self.btn_level3, self.btn_level4, self.btn_level5)

    def draw(self):
        self.exit_btn_draw()
        for i in self.group_btn:
            i.draw(self.screen)
        self.draw_stars()

    def exit_btn_draw(self):
        fullname = os.path.join('data', 'exit.png')
        self.image = pygame.image.load(fullname)
        self.exit_btn.draw(self.screen)
        self.rect = self.image.get_rect()
        self.rect.x = self.exit_btn.rect.x + (self.exit_btn.rect.w // 2 - self.rect.w // 2)
        self.rect.y = self.exit_btn.rect.y + (self.exit_btn.rect.h // 2 - self.rect.h // 2)
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

    def draw_stars(self):
        for number, i in enumerate(self.group_btn):
            self.draw_star(number, i.rect)

    def draw_star(self, number, rect):
        count_star = self.count_star(number)
        if count_star != 0:
            images_star = {1: pygame.image.load(os.path.join('data', 'star1.png')),
                           2: pygame.image.load(os.path.join('data', 'star2.png')),
                           3: pygame.image.load(os.path.join('data', 'star3.png'))}
            image = images_star[count_star]
            image = pygame.transform.scale(image,
                                           (image.get_width() * 0.5 * 0.3 * 2, image.get_height() * 0.5 * 0.3 * 2))
            if count_star == 1:
                x = rect.x + image.get_width() / 1.5
            else:
                x = rect.x
            y = rect.y + image.get_height() * 70 / image.get_height()
            width = image.get_width()
            height = image.get_height()
            self.screen.blit(image, pygame.rect.Rect(x, y, width, height))

    def count_star(self, number) -> int:
        res = cur.execute(f'SELECT level{number + 1}_star FROM Levels_Progress WHERE player_id = ('
                          'SELECT id FROM Players where username = ?)', (current_username['username'],)).fetchone()
        return sum(res)


if __name__ == '__main__':
    current_window = MainWindow()
    # current_window = LevelMenu()
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
                        if current_window.reg():
                            current_window = LevelMenu()
                    elif current_window.exit_btn.is_clicked():
                        current_window = MainWindow()
                    else:
                        for input_line in current_window.inp_group:
                            if input_line.is_clicked():
                                input_line.enter = True
                            else:
                                input_line.enter = False
                elif isinstance(current_window, LoginWindow):
                    if current_window.enter_btn.is_clicked():
                        if not current_window.check_input():
                            current_window = LevelMenu()
                    elif current_window.exit_btn.is_clicked():
                        current_window = MainWindow()
                    else:
                        for input_line in current_window.inp_group:
                            if input_line.is_clicked():
                                input_line.enter = True
                            else:
                                input_line.enter = False
                elif isinstance(current_window, LevelMenu):
                    if current_window.exit_btn.is_clicked():
                        current_window = LoginWindow()
                    elif current_window.btn_level1.is_clicked():
                        current_window = Level1()
                    elif current_window.btn_level2.is_clicked():
                        current_window = Level2()
                    elif current_window.btn_level3.is_clicked():
                        current_window = Level3()
                    elif current_window.btn_level4.is_clicked():
                        current_window = Level4()
                    elif current_window.btn_level5.is_clicked():
                        current_window = Level5()
            elif event.type == pygame.KEYDOWN:
                if isinstance(current_window, RegistrationWindow):
                    if event.key == pygame.K_RETURN:
                        if current_window.reg():
                            current_window = LevelMenu()
                    elif event.key == pygame.K_TAB:
                        current_window.next_input()
                    else:
                        for input_line in current_window.inp_group:
                            if input_line.enter:
                                input_line.input(event)
                if isinstance(current_window, LoginWindow):
                    if event.key == pygame.K_RETURN:
                        if not current_window.check_input():
                            current_window = LevelMenu()
                    elif event.key == pygame.K_TAB:
                        current_window.next_input()
                    else:
                        for input_line in current_window.inp_group:
                            if input_line.enter:
                                input_line.input(event)

        current_window.draw()
        pygame.display.flip()
    pygame.quit()
