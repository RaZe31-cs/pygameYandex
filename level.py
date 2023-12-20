import pygame
import os
import sys


def load_level(filename):
    filename = "data/" + filename
    if not os.path.isfile(filename):
        print(f"Файл '{filename}' не найден")
        sys.exit()
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


pygame.init()
level = load_level('lvl1.txt')
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
            fullname = path + '/' + img
            image = pygame.image.load(fullname).convert_alpha()
            images.append(image)
    return images


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.tile_type = tile_type
        self.image.fill(tile_images[tile_type])
        '''self.image = tile_images[tile_type]'''
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
        self.jump_speed = -5

        self.on_ground = False
        self.on_left = False
        self.on_right = False

    def import_character_assets(self):
        character_path = 'data/character/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}

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

        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        else:
            self.rect = self.image.get_rect(center=self.rect.center)

    def get_status(self):
        self.animation_speed = 0.2
        if self.direction.y < 0:
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

        if keys[pygame.K_SPACE]:  # добавить self.on_ground, если надо ограничить прыжок
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


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill('green')
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.setup_level(level_data)
        self.lives = [pygame.rect.Rect(20 * (i + 1) + 5 * i, 20, 20, 20) for i in range(3)]

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.world_shift = 0

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if cell == '#':
                    tile = Tile('ground', (x, y), tile_size)
                    self.tiles.add(tile)

                if cell == '|':
                    tile = Tile('support', (x, y), tile_size)
                    self.tiles.add(tile)

                if cell == '@':
                    player = Player((x, y))
                    self.player.add(player)

                if cell == '%':
                    obstacle = Obstacle((x, y), tile_size - 15)
                    self.obstacles.add(obstacle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction = player.direction.x

        if player_x < width / 4 and direction < 0:
            self.world_shift = 4
            player.speed = 0
        elif player_x > width / 4 * 3 and direction > 0:
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

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    player.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    player.current_x = player.rect.right

        if player.on_left and (player.rect.left < player.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > player.current_x or player.direction.x <= 0):
            player.on_right = False

        for sprite in self.obstacles.sprites():
            if sprite.rect.colliderect(player.rect):
                self.live()
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right + tile_size
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left - tile_size

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

        if player.on_ground and (player.direction.y < 0 or player.direction.y > 1):
            player.on_ground = False

        for sprite in self.obstacles.sprites():
            if sprite.rect.colliderect(player.rect):
                self.live()
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top - tile_size // 2
                    if player.direction.x < 0:
                        player.rect.left = sprite.rect.right + tile_size // 2
                    elif player.direction.x >= 0:
                        player.rect.right = sprite.rect.left - tile_size // 2
                    player.direction.y = 0
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom + tile_size // 2
                    if player.direction.x < 0:
                        player.rect.left = sprite.rect.right + tile_size // 2
                    elif player.direction.x >= 0:
                        player.rect.right = sprite.rect.left - tile_size // 2
                    player.direction.y = 0

    def draw(self):
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.obstacles.update(self.world_shift)
        self.obstacles.draw(self.display_surface)
        self.scroll_x()

        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player.draw(self.display_surface)
        for l in self.lives:
            pygame.draw.rect(self.display_surface, 'red', l)


tile_images = {
    'ground': 'grey',
    'support': 'lightgrey'
}

level = Level(level, screen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    level.draw()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
