import pygame
import os
import sys
import csv
import random


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


pygame.init()
icon = pygame.image.load(os.path.join('data', 'icon.png'))
pygame.display.set_icon(icon)
level = load_level('levels/level1.csv')
len_level_x = len(level[0])
len_level_y = len(level)
tile_size = 40
size = width, height = 1280, len(level) * tile_size
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 10


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def import_folder(path):
    images = []
    for _, __, img_file in os.walk(path):
        for img in img_file:
            fullname = os.path.join(path, img)
            image = pygame.image.load(fullname).convert_alpha()
            images.append(image)
    return images


class Sounds:
    def __init__(self, path_running=None, path_jump=None, path_drop=None, path_star=None, path_take_a_life=None):
        self.set_sound_running(path_running)
        self.set_sound_star(path_star)
        self.set_sound_jump(path_jump)
        self.set_sound_drop(path_drop)
        self.set_sound_take_a_life(path_take_a_life)

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
        self.jump_speed = -5.7

        self.on_ground = False

    def import_character_assets(self):
        character_path = os.path.join('data', 'character')
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}

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

    def get_status(self):
        self.animation_speed = 0.2
        if self.direction.y < 0:
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
        if self.rect.right + level.world_shift_sum + tile_size * 2 >= (len_level_x - 1) * tile_size:
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
        else:
            screen.blit(self.path, (self.x / 20, 0))


class Decor(pygame.sprite.Sprite):
    def __init__(self, pos, size, image):
        super().__init__()
        self.image = load_image(image)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.setup_level(level_data)
        self.live_img = load_image('lives.png')
        self.lives = [(20 * (i + 1) + 5 * i, 20) for i in range(3)]
        self.world_shift_sum = 0

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.stars_count, self.player_stars = 0, 0
        self.player = pygame.sprite.GroupSingle()
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

                if cell == '*':
                    star = Decor((x, y), tile_size, 'coins.png')
                    self.stars.add(star)
                    self.stars_count += 1

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction = player.direction.x
        tiles = self.tiles.sprites()
        if player_x < width / 4 and direction < 0 and tiles[0].rect.x + 4 < 1:
            self.world_shift = 4
            player.speed = 0

            self.world_shift_sum -= 4

        elif player_x > width / 4 * 3 and direction > 0 and tiles[-1].rect.x - 4 >= 1280:
            self.world_shift = -4
            player.speed = 0

            self.world_shift_sum += 4
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

        if player.on_ground and (player.direction.y < 0 or player.direction.y > 1):
            player.on_ground = False


    def draw_end(self):
        def text(list_text):
            f1 = pygame.font.Font(None, 50)
            for number, i in enumerate(list_text):
                text1 = f1.render(i, True, 'black')
                self.screen_end.blit(text1, ((list_x_y[number], 142)))
        self.screen_end = load_image('ending.png')
        list_x_y = ((self.screen_end.get_width() / 4.2), (self.screen_end.get_width() / 2), (self.screen_end.get_width() / 1.25))
        text([str(self.player_stars), 'N', 'N'])

        screen.blit(self.screen_end, (width / 2 - self.screen_end.get_width() / 2, height / 2 - self.screen_end.get_height() / 2))


    def draw(self):
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.stars.update(self.world_shift)
        self.stars.draw(self.display_surface)
        self.scroll_x()

        
        if self.player.sprite.end:
            self.draw_end()
        else:
            self.player.update()
            self.horizontal_movement_collision()
            self.vertical_movement_collision()
            self.player.draw(self.display_surface)
            for l in self.lives:
                self.display_surface.blit(self.live_img, l)
            self.seaweeds.update(self.world_shift)
            self.seaweeds.draw(self.display_surface)



tile_images = {x: load_image(os.path.join('tiles', f'tile0{str(x).rjust(2, "0")}.png')) for x in range(21)}
level = Level(level, screen)

bg_photo = pygame.transform.scale(load_image('background.png'), (2000, 720))
bg = BackGround(bg_photo)

sounds = Sounds(path_jump='sound_jump.mp3', 
                path_drop='sound_drop.mp3', 
                path_running='sound_running.mp3', 
                path_star='sound_star.mp3', 
                path_take_a_life='sound_take_a_life.mp3')



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    bg.draw_and_update()
    level.draw()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
