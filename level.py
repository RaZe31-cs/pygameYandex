import pygame
import os
import sys
import csv
import random
import sqlite3
import datetime
from functions import *
from start_window import *

con = sqlite3.connect(os.path.join('data', 'UnderWater.sqlite'))
cur = con.cursor()


def load_level(filename):
    filename = "data/" + filename
    if not os.path.isfile(filename):
        print(f"Файл '{filename}' не найден")
        sys.exit()
    level_map = []
    with open(filename) as map:
        level = csv.reader(map, delimiter=',')
        for row in level:
            level_map.append(list(row))
    return level_map


class Sounds:
    def __init__(self, path_running=None, path_jump=None, path_drop=None, path_star=None, path_take_a_life=None,
                 path_loading_start_screen=None):
        self.set_sound_running(path_running)
        self.set_sound_star(path_star)
        self.set_sound_jump(path_jump)
        self.set_sound_drop(path_drop)
        self.set_sound_take_a_life(path_take_a_life)
        self.set_sound_loading_start_screen(path_loading_start_screen)

    def set_sound_running(self, path):
        self.music_running = pygame.mixer.music
        self.music_running.load(os.path.join('data', 'sound', path))
        self.music_running.set_volume(0.05)

    def set_sound_star(self, path):
        self.sound_star = pygame.mixer.Sound(os.path.join('data', 'sound', path))
        self.sound_star.set_volume(0.054)

    def set_sound_jump(self, path):
        self.sound_jump = pygame.mixer.Sound(os.path.join('data', 'sound', path))
        self.sound_jump.set_volume(0.1)

    def set_sound_drop(self, path):
        self.sound_drop = pygame.mixer.Sound(os.path.join('data', 'sound', path))
        self.sound_drop.set_volume(0.045)

    def set_sound_take_a_life(self, path):
        self.sound_take_a_life = pygame.mixer.Sound(os.path.join('data', 'sound', path))

    def set_sound_loading_start_screen(self, path):
        self.music_loading_start_screen = pygame.mixer.Sound(os.path.join('data', 'sound', path))
        self.music_loading_start_screen.set_volume(0.05)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos, size):
        super().__init__()
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.current_x = 0
        self.animation_speed = 0.1
        self.end = False

        self.status = 'idle'
        self.facing_right = True
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 4
        self.gravity = 0.15
        self.jump_speed = -6.8
        self.hurts = 0

        self.on_ground = False

    def import_character_assets(self):
        character_path = os.path.join('data', 'character')
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'hurt': []}

        for animation in self.animations.keys():
            full_path = os.path.join(character_path, animation)
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False)

        if self.hurts:
            self.hurts -= 1

    def get_status(self):
        self.animation_speed = 0.2
        if self.hurts:
            self.status = 'hurt'
        elif self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                # sound
                if self.status == 'fall':
                    sounds.sound_drop.play()
                # sound
                self.status = 'run'
            else:
                # sound
                if self.status == 'fall':
                    sounds.sound_drop.play()
                # sound
                self.status = 'idle'
                self.animation_speed = 0.1

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
            # sound
            if not sounds.music_running.get_busy() and self.on_ground:
                sounds.music_running.play()

        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
            # sound
            if not sounds.music_running.get_busy() and self.on_ground:
                sounds.music_running.play()
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()
            # sound
            sounds.sound_jump.play()

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
        if self.rect.left >= width:
            self.end = True


class BackGround:
    def __init__(self, path):
        self.path = path
        self.x_left = level.player.sprite.rect.x
        self.x_back_ground = 0
        self.x = 0
        self.word_shift = 0

    def draw_and_update(self):
        self.word_shift += level.world_shift
        if level.world_shift:
            self.x = 0 + self.word_shift
        screen.blit(self.path, (self.x / 20, 0))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, name):
        super().__init__()
        self.name = name
        self.import_enemy_assets()
        self.frame_index = 0
        self.animation_speed = 0.1
        self.is_alive = True

        self.status = 'run'
        self.facing_right = True
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.speed = 2
        self.direction = pygame.math.Vector2(-1, 0)

    def import_enemy_assets(self):
        enemy_path = f'data/enemies/{self.name}/'
        self.animations = {'run': [], 'death': []}

        for animation in self.animations.keys():
            full_path = enemy_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0
            if self.status == 'death':
                self.is_alive = False

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False)

    def change_status(self):
        self.status = 'death'

    def change_direction(self):
        self.facing_right = False if self.facing_right else True
        self.direction.x = -self.direction.x

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift


class Decor(pygame.sprite.Sprite):
    def __init__(self, pos, size, image):
        super().__init__()
        self.image = load_image(image)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift


class LossWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.bg_image = load_image('start_background.png')

        btn_width, btn_height = 240, 80
        btn_menu_x, btn_menu_y = self.size[0] // 2 - btn_width * 1.2, self.size[1] / 2 + btn_height / 5
        btn_again_x, btn_again_y = self.size[0] // 2 + btn_width * 0.2, self.size[1] / 2 + btn_height / 5

        normal_bg, hovered_bg = '#078CB2', '#076682'
        normal_text, hovered_text = '#011D2B', '#ffffff'

        self.btn_menu = Button(btn_menu_x, btn_menu_y, btn_width, btn_height, 'Вернуться в меню', normal_bg,
                               hovered_bg, normal_text, hovered_text)
        self.btn_again = Button(btn_again_x, btn_again_y, btn_width, btn_height, 'Заново', normal_bg,
                                hovered_bg, normal_text, hovered_text)

        self.btn_group = [self.btn_menu, self.btn_again]

    def display_text(self):
        f = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), 90)
        text = f.render('Вы проиграли!', True, '#011D2B')
        x, y = self.size[0] // 2 - text.get_width() // 2, self.size[1] // 2 - text.get_width() / 3.5
        self.screen.blit(text, (x, y))

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.display_text()
        for btn in self.btn_group:
            btn.draw(self.screen)


class WinWindow:
    def __init__(self, surface):
        self.screen = surface
        self.size = (650, 350)

        btn_width, btn_height = 180, 50
        btn_menu_x, btn_menu_y = width // 2 - btn_width * 1.7, height / 2 + btn_height * 2.2
        btn_next_x, btn_next_y = width // 2 - btn_width // 2, height / 2 + btn_height * 2.2
        btn_again_x, btn_again_y = width // 2 + btn_width * 0.7, height / 2 + btn_height * 2.2

        normal_bg, hovered_bg = '#078CB2', '#076682'
        normal_text, hovered_text = '#011D2B', '#ffffff'

        self.btn_menu = Button(btn_menu_x, btn_menu_y, btn_width, btn_height, 'Вернуться в меню', normal_bg,
                               hovered_bg, normal_text, hovered_text)
        self.btn_again = Button(btn_again_x, btn_again_y, btn_width, btn_height, 'Заново', normal_bg,
                                hovered_bg, normal_text, hovered_text)
        self.btn_next = Button(btn_next_x, btn_next_y, btn_width, btn_height, 'Следующий уровень', normal_bg,
                               hovered_bg, normal_text, hovered_text)

        self.btn_group = [self.btn_menu, self.btn_again, self.btn_next]
        self.finish = False

    def display_text(self):
        f = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), 45)
        text = f.render('Победа!', True, '#011D2B')
        x = self.screen.get_width() // 2 - text.get_width() // 2
        y = self.screen.get_height() // 2 - self.size[1] // 2 + text.get_height() * 0.5
        self.screen.blit(text, (x, y))

        f2 = pygame.font.Font(os.path.join('data', 'better-vcr-5.2.ttf'), 20)

        time_delta = level.finish_time - level.start_time
        time_delta = time_delta.total_seconds()
        self.text_time = f'{str(int(time_delta // 60)).rjust(2, "0")}:{str(int(time_delta % 60)).rjust(2, "0")}'
        text_time = f2.render(self.text_time, True, '#011D2B')
        x_time = self.screen.get_width() // 2 - text_time.get_width() // 3.5
        y = self.screen.get_height() // 2 + text_time.get_height() * 2.5
        time_img = pygame.image.load(os.path.join('data', 'win_window', 'clock.png'))
        self.screen.blit(text_time, (x_time, y))
        self.screen.blit(time_img, (x_time - 1.2 * time_img.get_width(), y - time_img.get_height() // 4))

        self.text_star = f'{level.player_stars}/{level.stars_count}'
        text_star = f2.render(self.text_star, True, '#011D2B')
        x_stars = self.screen.get_width() // 2 - text_time.get_width() * 2.7
        star_img = pygame.image.load(os.path.join('data', 'win_window', 'coins.png'))
        self.screen.blit(text_star, (x_stars, y))
        self.screen.blit(star_img, (x_stars - 1.2 * star_img.get_width(), y - star_img.get_height() // 4))

        self.text_enemies = f'{level.enemies_count - len(level.enemies)}/{level.enemies_count}'
        text_enemies = f2.render(self.text_enemies, True, '#011D2B')
        x_enemies = self.screen.get_width() // 2 + text_time.get_width() * 2.3
        enemy_img = pygame.image.load(os.path.join('data', 'win_window', 'dead_fish.png'))
        self.screen.blit(text_enemies, (x_enemies, y))
        self.screen.blit(enemy_img, (x_enemies - 1.2 * enemy_img.get_width(), y - enemy_img.get_height() // 4))

    def draw_star(self):
        count_star = self.count_star()
        empty_img = pygame.image.load(os.path.join('data', 'win_window', 'empty_star.png'))
        full_img = pygame.image.load(os.path.join('data', 'win_window', 'full_star.png'))

        empty_img_big = pygame.image.load(os.path.join('data', 'win_window', 'empty_star_big.png'))
        full_img_big = pygame.image.load(os.path.join('data', 'win_window', 'full_star_big.png'))

        star_coords = [(self.screen.get_width() // 2 - 1.8 * empty_img_big.get_width(),
                        self.screen.get_height() // 2 - empty_img_big.get_height()), (
                       self.screen.get_width() // 2 - empty_img_big.get_width() // 2,
                       self.screen.get_height() // 2 - empty_img_big.get_height()),
                       (self.screen.get_width() // 2 + empty_img_big.get_width(),
                        self.screen.get_height() // 2 - empty_img_big.get_height())]
        for s in range(count_star):
            star_x, star_y = star_coords[s]
            img = full_img_big if s == 1 else full_img
            self.screen.blit(img, (star_x, star_y))
        for q in range(count_star, 3):
            star_x, star_y = star_coords[q]
            img = empty_img_big if q == 1 else empty_img
            self.screen.blit(img, (star_x, star_y))

    def db_stars(self, number, level):
        now = cur.execute(f'SELECT level{level}_star FROM Levels_Progress WHERE player_id = ('
                          'SELECT id FROM Players where username = ?)', (current_username['username'],)).fetchone()
        cur.execute(f'update Levels_Progress set level{level}_star = ?'
                    f'WHERE player_id = (SELECT id FROM Players where username = ?)',
                    (max(number, int(now[0])), current_username['username']))
        if int(now[0]) == 0 and number != 0:
            progress = int(cur.execute(f'SELECT progress FROM Players WHERE username = ?', (current_username['username'],)).fetchone()[0])
            cur.execute(f'update Players set progress = ?'
                        f'WHERE username = ?',
                        (progress + 1, current_username['username']))
        con.commit()

    def count_star(self):
        res = 0
        if self.text_star.split('/')[0] == self.text_star.split('/')[1]:
            res += 1
        if self.text_enemies.split('/')[0] == self.text_enemies.split('/')[1]:
            res += 1
        if int(self.text_time.split(':')[0]) * 60  + int(self.text_time.split(':')[-1]) < 60:
            res += 1
        if not self.finish:
            self.db_stars(res, level.lvl_num)
            self.finish = True
        return res

    def draw(self):
        w, h = self.size
        self.screen.fill('#5FB5CD',
                         pygame.rect.Rect(self.screen.get_width() / 2 - w / 2, self.screen.get_height() / 2 - h / 2, w,
                                          h))
        pygame.draw.rect(self.screen, '#011D2B', pygame.rect.Rect(self.screen.get_width() / 2 - w / 2 - 2,
                                                                  self.screen.get_height() / 2 - h / 2 - 2, w + 2,
                                                                  h + 2), 4)
        self.display_text()
        for btn in self.btn_group:
            btn.draw(self.screen)
        self.draw_star()


class Level:
    def __init__(self, level_data, surface, lvl):
        self.display_surface = surface
        self.setup_level(level_data)
        self.live_img = load_image('lives.png')
        self.lives = [(25 * (i + 1) + 5 * i, 25) for i in range(3)]
        self.win_window = None
        time = datetime.datetime.now().time()
        self.start_time = datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
        self.finish_time = self.start_time
        self.lvl_num = lvl
        self.end = False

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.stars_count, self.player_stars = 0, 0
        self.player = pygame.sprite.GroupSingle()
        self.enemies_count, self.enemies = 0, pygame.sprite.Group()
        self.obstacles = []

        self.seaweeds = pygame.sprite.Group()
        self.world_shift = 0

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if cell.isdigit():
                    tile = Tile(int(cell), (x, y), tile_size)
                    self.tiles.add(tile)

                if cell == '|':
                    seaweed = Decor((x, y), tile_size, os.path.join('seaweeds', f'seaweed{random.randint(1, 9)}.png'))
                    self.seaweeds.add(seaweed)

                if cell == '@':
                    player = Player((x, y))
                    self.player.add(player)

                if cell == '%':
                    enemy = Enemy((x, y), random.choice(os.listdir('data/enemies')[1:]))
                    self.enemies.add(enemy)
                    self.enemies_count += 1

                if cell == '*':
                    star = Decor((x, y), tile_size, 'coins.png')
                    self.stars.add(star)
                    self.stars_count += 1

                if cell == '!':
                    obstacle = pygame.rect.Rect(x, y, tile_size, tile_size)
                    self.obstacles.append(obstacle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction = player.direction.x
        tiles = self.tiles.sprites()
        if player_x < width / 4 and direction < 0 and tiles[0].rect.x + 4 < 1:
            self.world_shift = 4
            player.speed = 0

        elif player_x > width / 4 * 3 and direction > 0 and tiles[-1].rect.x - 4 >= 1280:
            self.world_shift = -4
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 4

    def live(self):
        if self.lives:
            self.lives.pop(-1)
            # sound
            sounds.sound_take_a_life.play()

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for enemy in self.enemies.sprites():
            if not enemy.is_alive:
                self.enemies.remove_internal(enemy)
            else:
                if enemy.status == 'run':
                    enemy.rect.x += enemy.direction.x * enemy.speed
                for obstacle in self.obstacles:
                    if enemy.rect.colliderect(obstacle):
                        enemy.change_direction()
                if enemy.rect.colliderect(player.rect) and enemy.status == 'run' and not player.hurts:
                    self.live()
                    player.hurts = 80

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.current_x = player.rect.right

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

        for sprite in self.stars.sprites():
            if player.rect.colliderect(pygame.rect.Rect(sprite.rect.x + 10, sprite.rect.y + 10, 20, 20)):
                self.player_stars += 1
                self.stars.remove_internal(sprite)
                # sound
                sounds.sound_star.play()

        for enemy in self.enemies.sprites():
            if (player.rect.colliderect(enemy.rect) and not player.on_ground and
                    player.rect.bottom < enemy.rect.bottom and player.direction.y > 0):
                enemy.change_status()

        if player.on_ground and (player.direction.y < 0 or player.direction.y > 1):
            player.on_ground = False

    def draw_end(self):
        if not self.end:
            self.win_window = WinWindow(self.display_surface)
            self.end = True
        self.win_window.draw()

    def draw(self):
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.stars.update(self.world_shift)
        self.stars.draw(self.display_surface)
        self.scroll_x()

        if self.player.sprite.end:
            self.seaweeds.update(self.world_shift)
            if self.start_time == self.finish_time:
                time = datetime.datetime.now().time()
                self.finish_time = datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
            self.draw_end()
        else:
            self.enemies.update(self.world_shift)
            for obstacle in self.obstacles:
                obstacle.x += self.world_shift
            self.player.update()
            self.horizontal_movement_collision()
            self.vertical_movement_collision()
            self.enemies.draw(self.display_surface)
            self.player.draw(self.display_surface)
            for l in self.lives:
                self.display_surface.blit(self.live_img, l)
            self.seaweeds.update(self.world_shift)
            self.seaweeds.draw(self.display_surface)


def game():
    global level, lvl
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if isinstance(level, LossWindow):
                    if level.btn_again.is_clicked():
                        level = Level(load_level(f'levels/level{lvl}.csv'), screen)
                    elif level.btn_menu.is_clicked():
                        lvl = start_window(current_window=LevelMenu, username=current_username['username'])
                        level = Level(load_level(f'levels/level{lvl}.csv'), screen, lvl)
                if isinstance(level, Level):
                    if level.win_window is not None:
                        if level.win_window.btn_again.is_clicked():
                            level = Level(load_level(f'levels/level{lvl}.csv'), screen, lvl)
                        elif level.win_window.btn_menu.is_clicked():
                            lvl = start_window(current_window=LevelMenu, username=current_username['username'])
                            level = Level(load_level(f'levels/level{lvl}.csv'), screen, lvl)
                        elif level.win_window.btn_next.is_clicked():
                            lvl = lvl + 1
                            level = Level(load_level(f'levels/level{lvl}.csv'), screen, lvl)
        if isinstance(level, Level):
            if not level.lives:
                level = LossWindow()
            else:
                bg.draw_and_update()
        level.draw()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


pygame.init()
sounds = Sounds(path_jump='sound_jump.mp3',
                path_drop='sound_drop.mp3',
                path_running='sound_running.mp3',
                path_star='sound_star.mp3',
                path_take_a_life='sound_take_a_life.mp3',
                path_loading_start_screen='sound_loading_screen.mp3')
sounds.music_loading_start_screen.play()
icon = pygame.image.load(os.path.join('data', 'icon.png'))
pygame.display.set_icon(icon)
pygame.display.set_caption('UnderWater')
lvl = start_window()
if not lvl:
    pygame.quit()
    sys.exit()
level = load_level(f'levels/level{lvl}.csv')
tile_size = 40
size = width, height = 1280, len(level) * tile_size
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 10
tile_images = {x: load_image(os.path.join('tiles', f'tile0{str(x).rjust(2, "0")}.png')) for x in range(53)}
level = Level(level, screen, lvl)
bg_photo = pygame.transform.scale(load_image('background.png'), (2000, 720))
bg = BackGround(bg_photo)

game()
