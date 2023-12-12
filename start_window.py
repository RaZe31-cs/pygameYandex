import os.path
import pygame


class InputLine:
    def __init__(self, x: int, y: int, width: int, height: int, text_bg: str):
        self.rect = pygame.rect.Rect(x, y, width, height)

        self.font = pygame.font.Font(None, height // 6 * 3)
        self.text = text_bg
        self.user_input = ''

        self.enter = False

    def draw(self, screen: pygame.surface.Surface):
        pygame.draw.rect(screen, '#03045e', self.rect, width=3)
        if not self.enter:
            self.inp_text = self.font.render(self.text, False, '#3c81f0')
        else:
            self.inp_text = self.font.render(self.user_input, False, '#03045e')
        self.text_rect = self.inp_text.get_rect(center=self.rect.center)

        """
        Ниже стирается старый текст путем наложение такого же текста, цветом заднего фона
        ДОДЕЛАТЬ
        !
        !
        !
        !
        !
        """
        text1 = self.font.render(self.text, False, '#ade8f4')
        text2 = self.font.render(self.user_input, False, '#ade8f4')
        text1_rect = text1.get_rect(center=self.rect.center)
        text2_rect = text2.get_rect(center=self.rect.center)
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
        """
        !
        !
        !
        !
        ДОДЕЛАТЬ
        """

        screen.blit(self.inp_text, self.text_rect)

    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.x <= mouse[0] <= self.rect.x + self.rect.w and self.rect.y <= mouse[
            1] <= self.rect.y + self.rect.h:
            return True
        return False

    def input(self, event):
        if self.enter:
            self.user_input += chr(event.key)


class Button:
    def __init__(self, x, y, width, height, text, normal_bgcolor, hovered_bgcolor,
                 normal_textcolor, hovered_textcolor):
        self.rect = pygame.rect.Rect(x, y, width, height)

        self.font = pygame.font.Font(None, height // 6 * 4)
        self.text = text

        self.colors = {'normal_bg': normal_bgcolor, 'hovered_bg': hovered_bgcolor, 'normal_text': normal_textcolor,
                       'hovered_text': hovered_textcolor}

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        bg_color, text_color = self.colors['normal_bg'], self.colors['normal_text']
        if self.is_clicked():
            bg_color, text_color = self.colors['hovered_bg'], self.colors['hovered_text']
        screen.fill(bg_color, self.rect)

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

        btn_width, btn_height = 210, 50
        btn_login_x, btn_login_y = self.size[0] / 3 - btn_width / 2, self.size[1] / 3 + btn_height
        btn_reg_x, btn_reg_y = self.size[0] - self.size[0] / 3 - btn_width / 2, self.size[1] / 3 + btn_height
        btn_records_x, btn_records_y = self.size[0] / 2 - btn_width / 2, self.size[1] / 2 + btn_height / 2

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
        f1 = pygame.font.Font(os.path.join('data', 'Aguante-Regular.otf'), 60)
        text = f1.render('UNDERWATER', True, '#0077b6')
        x, y = self.size[0] / 2 - text.get_width() / 2, self.size[1] / 2 - text.get_width() / 2
        text_w, text_h = text.get_width(), text.get_height()
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
        self.password = InputLine(inp_password_x, inp_password_y, inp_width, inp_height, 'Пароль')
        self.proof_password = InputLine(inp_proof_password_x, inp_proof_password_y, inp_width, inp_height,
                                        'Подтверждение пароля')

        self.inp_group = (self.user_name, self.password, self.proof_password)

    def draw(self):
        for i in self.inp_group:
            i.draw(self.screen)


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
                    for input_line in current_window.inp_group:
                        if input_line.is_clicked():
                            input_line.enter = True
                            print('нажата')
                            break
                    else:
                        for input_line in current_window.inp_group:
                            input_line.enter = False
                            print('все сброшены')
            elif event.type == pygame.KEYDOWN:
                if isinstance(current_window, RegistrationWindow):
                    for input_line in current_window.inp_group:
                        if input_line.enter == True:
                            input_line.input(event)

        current_window.draw()
        pygame.display.flip()
    pygame.quit()
