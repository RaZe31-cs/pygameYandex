import pygame
import os
import sys
import csv
import random
from functions import *
from start_window import *


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

        self.status = 'idle'
        self.facing_right = True
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 4
        self.gravity = 0.15
        self.jump_speed = -5.7
        self.hurts = 0

        self.on_ground = False

    def import_character_assets(self):
        character_path = 'data/character/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'hurt': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
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
                self.status = 'run'
            else:
                self.status = 'idle'
                self.animation_speed = 0.1

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()


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


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.setup_level(level_data)
        self.live_img = load_image('lives.png')
        self.lives = [(25 * (i + 1) + 5 * i, 25) for i in range(3)]

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.stars_count, self.player_stars = 0, 0
        self.player = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
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
                    seaweed = Decor((x, y), tile_size, f'seaweeds\seaweed{random.randint(1, 9)}.png')
                    self.seaweeds.add(seaweed)

                if cell == '@':
                    player = Player((x, y))
                    self.player.add(player)

                if cell == '%':
                    enemy = Enemy((x, y), random.choice(['fish1', 'fish2', 'fish3', 'fish4']))
                    self.enemies.add(enemy)

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

        for enemy in self.enemies.sprites():
            if (player.rect.colliderect(enemy.rect) and not player.on_ground and
                    player.rect.bottom < enemy.rect.bottom and player.direction.y > 0):
                enemy.change_status()

        if player.on_ground and (player.direction.y < 0 or player.direction.y > 1):
            player.on_ground = False

    def draw(self):
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.stars.update(self.world_shift)
        self.stars.draw(self.display_surface)
        self.scroll_x()

        self.enemies.update(self.world_shift)
        for obstacle in self.obstacles:
            obstacle.x += self.world_shift
        self.player.update()
        self.vertical_movement_collision()
        self.horizontal_movement_collision()
        self.player.draw(self.display_surface)
        self.enemies.draw(self.display_surface)
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
                        level = Level(load_level(f'levels/{lvl}.csv'), screen)
                    elif level.btn_menu.is_clicked():
                        lvl = start_window(current_window=LevelMenu)
                        level = Level(load_level(f'levels/{lvl}.csv'), screen)
        if isinstance(level, Level):
            screen.blit(bg, (0, 0))
            if not level.lives:
                level = LossWindow()
        level.draw()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


pygame.init()
icon = pygame.image.load(os.path.join('data', 'icon.png'))
pygame.display.set_icon(icon)
pygame.display.set_caption('UnderWater')
lvl = start_window()
level = load_level(f'levels/{lvl}.csv')
tile_size = 40
size = width, height = 1280, len(level) * tile_size
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 10
tile_images = {x: load_image(f'tiles/tile0{str(x).rjust(2, "0")}.png') for x in range(21)}
bg = load_image('background.png')
level = Level(level, screen)
game()
