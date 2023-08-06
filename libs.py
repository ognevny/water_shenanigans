import pygame as pg
from config import *
import random as r

pg.font.init(); pg.mixer.init(); pg.init()

font = pg.font.Font("assets/font.ttf", FONT_SIZE)

#sounds
move = pg.mixer.Sound("assets/sounds/move.wav")
attack = pg.mixer.Sound("assets/sounds/attack.wav")
card_get = pg.mixer.Sound("assets/sounds/card_choice.wav")
loot_collected = pg.mixer.Sound("assets/sounds/loot_collected.wav")
door = pg.mixer.Sound("assets/sounds/door.wav")
door.set_volume(0.1)
select = pg.mixer.Sound("assets/sounds/select.wav")

class Game():

    def __init__(self, colors: dict[str : tuple[int, int, int]]) -> None:
        self.screen = pg.display.set_mode((640, 480)); pg.display.set_caption('water shenanigans')
        self.running = True
        self.clock = pg.time.Clock()
        self.colors = colors
        self.load_screen = pg.Surface((640, 480)); self.load_screen.fill(self.colors["black"])

        self.player = Entity("player", 10, 1, 10)
        self.player_offset = 48
        self.entities: list[Entity] = []
        self.move_tiles: list[int] = []

        self.generate_map()
        self.playing = True
        self.current_level = 1

        self.blue = 0
        self.changing_color = True

        self.canteen_anim: list[pg.Surface] = []
        for canteen_file in range(1, 5):
            self.canteen_anim.append(pg.transform.scale(pg.image.load(f"assets/canteen/canteen00{canteen_file}.png").convert_alpha(), (200, 200)))
        self.canteen_prog = 0
        self.canteen_spr: pg.Surface

        self.buildings = {"lighthouse" : 10}
        self.sprites = {"lighthouse" : pg.image.load("assets/lighthouse.png").convert_alpha()}

        self.gamestate = "game"

        self.current_money = 0
        self.full_money = 5000

        #elements
        self.hud_elements: list[MainMenuElement] = []
        self.hud_elements.append(MainMenuElement("menu_element", (0, 330)))
        q = MainMenuElement("quit_button", (0, 400))
        q.type = "quit"
        self.hud_elements.append(q)

    def generate_map(self):
        self.map: list[Tile] = []
        if USE_MAP_LEN:
            map = []
            for _ in range(MAP_LEN):
                l = []
                for _ in range(MAP_LEN):
                    l.append(0)
                map.append(l)

            for j, row in enumerate(map):
                for i in range(len(row)): 
                    coord = return_isometry(i, j)
                    self.map.append(Tile(coord[0], coord[1]))

            for n in get_close_tiles(self.playerpos):
                coords = self.map[n].pos
                self.map[n] = Tile(coords[0], coords[1], "chosen_tile")
            self.move_tiles = get_close_tiles(self.playerpos)

        else:
            for j, row in enumerate(TEXT_MAP):
                for i, char in enumerate(row):
                    coord = return_isometry(i, j)
                    if char == 0:
                        self.map.append(Tile(coord[0], coord[1]))
                    elif char == 1 or char == 2:
                        self.map.append(Tile(coord[0], coord[1], "water_tile"))
                    elif char == 3:
                        self.map.append(Tile(coord[0], coord[1], "sand_tile"))
            add_tiles = []
            for n in get_close_tiles(self.player.pos):
                if self.player.stamina > 0:
                    coords = self.map[n].pos
                    self.map[n] = Tile(coords[0], coords[1], "chosen_tile")
                    add_tiles.append(n)
            self.move_tiles = add_tiles

    def run(self):
        while self.running: 
            if self.current_money < self.full_money:
                self.current_money += 0.5
            self.change_color()
            self.change_canteen()
            if self.gamestate == "game":
                for entity in self.entities:
                    entity.update()
                self.player.update()

                self.screen.fill((30, 30, int(self.blue)))
                for tile in self.map:
                    tile.show(self.screen)             #updating the screen

                for tile2 in self.map:
                    if DEBUG:
                        surf = pg.Surface((tile2.rect.width, tile2.rect.height))
                        surf.fill((255, 255, 255))
                        self.screen.blit(surf, (tile2.pos[0] + RECT_OFFSET_X, tile2.pos[1] + RECT_OFFSET_Y))
                for building in self.buildings:
                    self.screen.blit(self.sprites[building], (self.map[self.buildings[building]].x, self.map[self.buildings[building]].y - 64)) #To do this
                self.screen.blit(self.canteen_spr, (440, 280))
                self.screen.blit(self.player.spr, (self.map[self.playerpos].pos[0], self.map[self.playerpos].pos[1] - self.player_offset))
                self.screen.blit(font.render(str(int(self.current_money)), False, (255, 255, 255)), (440, 0))
                pg.display.update()

                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN:
                        mouse = pg.mouse.get_pos()
                        for i in range(0, len(self.map)):
                            tile = self.map[i]
                            if tile.rect.collidepoint(mouse[0], mouse[1]) and (i in self.move_tiles) and self.player.stamina > 0:
                                self.player.pos = i
                                self.generate_map()
                                self.player.stamina -= 1 * (2 - int(not self.player_on_water))
                                move.play()
                                if self.player.pos == self.buildings['lighthouse']:
                                    door.play()
                                    self.gamestate = "menu"
                                break
                        self.generate_map()
                    if event.type == 256:
                        self.running = False
                self.clock.tick(FPS)

            elif self.gamestate == "menu":
                self.screen.fill((30, 30, int(self.blue)))

                for hud_element in self.hud_elements:
                    self.screen.blit(hud_element.image, hud_element.pos)

                pg.display.update()

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        for elem in self.hud_elements:
                            rect = elem.rect
                            if rect.collidepoint((pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])) and elem.type == "quit":
                                self.running = False
                self.clock.tick(FPS)
        
    def change_color(self):
        if self.blue == 200:
            self.changing_color = False
        if self.blue == 30:
            self.changing_color = True

        if self.changing_color:
            self.blue += 0.5
        else:
            self.blue -= 0.5

    def change_canteen(self):
        self.canteen_prog += CANTEEN_FRAME_DURATION
        self.canteen_prog %= 3
        self.canteen_spr = self.canteen_anim[int(self.canteen_prog)]

    def new_level(self):
        map = []
        for _ in range(MAP_LEN):
            l = []
            for _ in range(MAP_LEN):
                l.append(0)
            map.append(l)
        
        for row in range(0, len(map)):
            pass #TODO

    @property
    def playerpos(self):
        return self.player.pos
    
    @property
    def player_on_water(self):
        tile = self.map[self.player.pos].tile_type
        if tile == "water_tile":
            return True
        else:
            return False

class Tile():

    def __init__(self, x: int, y: int, sprite: str = "grass_tile", length: int = 1) -> None:
        self.x = x
        self.y = y
        self.sprite = pg.image.load(f"assets/{sprite}.png").convert_alpha()
        self.tile_type = sprite

        self.length = length
        if sprite == "grass_tile":
            self.sprite2 = pg.image.load("assets/dirt_tile.png").convert_alpha()
        elif sprite == "cobblestone_tile":
            self.sprite2 = pg.image.load("assets/cobblestone_tile.png").convert_alpha()

    def show(self, screen: pg.Surface):
        if self.length == 1:
            screen.blit(self.sprite, self.pos)
        else:
            n = 0
            for i in range(0, self.length - 1):
                screen.blit(self.sprite2, (self.x, self.y - i * W / 2))
                n = i
            screen.blit(self.sprite, (self.x, self.y - (n + 1) * H / 2))
        
    @property
    def pos(self):
        return (self.x, self.y)
    
    @property
    def rect(self):
        ret_rect = pg.Rect(0, 0, 40, 40)
        ret_rect.bottomleft = (self.x + RECT_OFFSET_X, self.y + RECT_OFFSET_Y)
        return ret_rect
    
class Entity():

    def __init__(self, name: str, hp: int, dmg: int, pos: int) -> None:
        self.anim: list[pg.Surface] = []
        for i in range(1, 5):
            self.anim.append(pg.transform.scale(pg.image.load(f"assets/{name}/{name}00{i}.png").convert_alpha(), (64, 64)))
        self.anim_prog = 0
        self.spr: pg.Surface
        self.health = hp
        self.damage = dmg
        self.pos = pos
        self.stamina = 10

    def update(self):
        self.anim_prog += 0.15 / FPS * 38
        self.anim_prog %= 3
        self.spr = self.anim[int(self.anim_prog)]

class WorldCollectable():
    def __init__(self, sprite: str, pos: int, price_zone: int = 1) -> None:
        self.sprite = pg.image.load(f"assets/{sprite}.png").convert_alpha()
        self.pos = pos
        if price_zone == 1: 
            self.price = r.randint(20, 30)
        elif price_zone == 2:
            self.price = r.randint(40, 50)
        elif price_zone == 3:
            self.price = r.randint(80, 100)


def get_close_tiles(pos: int) -> list[int]:
    ret_list = []
    if pos % 9 != 0:
        ret_list.append(pos - 1)
    if pos % 9 != 8 or pos == 0:
        ret_list.append(pos + 1)
    if pos > 8:
        ret_list.append(pos - 9)
    if pos < 72:
        ret_list.append(pos + 9)

    return ret_list

def return_isometry(x: int, y: int):
    xpos = (x - y) * W / 2 + GLOBAL_X_OFFSET
    ypos = (0.5 * x + 0.5 * y) * H / 2 + GLOBAL_Y_OFFSET
    return (xpos, ypos)

def calculate_len(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    x1 = p1[0]; y1 = p1[1]
    x2 = p2[0]; y2 = p2[1]

    x = (x2 - x1) ** 2; y = (y2 - y1) ** 2
    return (x + y) ** 0.5

def calc_menu_hud_offset(hud_pos: tuple[int, int]):
    distance = calculate_len(pg.mouse.get_pos(), hud_pos)
    offset = -500 * (distance / 750) - 100
    return (hud_pos[0] + offset, hud_pos[1])

class MainMenuElement():
    def __init__(self, image: str, pos: tuple[int, int]) -> None:
        self.image = pg.image.load(f"assets/{image}.png").convert_alpha()
        self.x = pos[0]; self.y = pos[1]
        self.type = "play"
    
    @property
    def pos(self):
        offset = calc_menu_hud_offset((100, self.y))
        return offset
    
    @property
    def rect(self):
        rect = self.image.get_rect()
        rect.topleft = self.pos
        return rect
