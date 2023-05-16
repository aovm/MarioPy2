from game_chunk import Chunk

from components.level_map import LevelMap, Tile

from entities.goomba import Goomba
from entities.koopa import Koopa
from entities.kin_object import KinecticObject
from entities.bricks import Bricks
from entities.iblock import iBlock
from entities.mysteryblock import MysteryBlock
from entities.flag import Flag
from entities.tube import Tube
from entities.coin import Coin
from entities.castle_door import CastleDoor
from entities.oflag import OFlag

import pygame, constants as c
from constants import BR

# key: bg -> Surface, la imagen de fondo del nivel principal
# key: mario1 -> Surface, fotograma de mario estático

@staticmethod
def load() -> dict:
    pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
    pygame.mixer.init()

    main_menu_path = c.absolutePath(f"res{BR}tilesets{BR}SMB_Title_Screen_disp.png")
    main_menu_surf = pygame.image.load(main_menu_path)

    # Chunks de 64 px de largo y 240 px de altura, excepto el último de 48 px.
    bg_path_1_1 = c.absolutePath(f"res{BR}levels{BR}1-1{BR}first_stage_map.png")
    bg_surf_1_1 = pygame.image.load(bg_path_1_1).convert_alpha()
    csv_1_1 = parseCSVData()
    lenghts_1_1 = [64 for i in range(0, 52)]
    lenghts_1_1.append(48)

    return { 'menu' : main_menu_surf,
             'mario_states' : {
                'small' : s_mario_resc(),
                'big' : b_mario_resc(),
                'transition' : t_mario_resc()
             },
             'entities' : entitiesDict(),
             'blocks' : blockDict(),
             'objects' : objectDict(),
             'UI' : uiDict(),
             '1-1' : parseLevel1Maps(bg_surf_1_1, csv_1_1),
             'audio' : audioDict()
            }

# Mario standing asset: 0
# Mario movement assets: 1 - 3.
# Mario braking asset: 4
@staticmethod
def s_mario_resc():
    playersheet_path = c.absolutePath(f"res{BR}tilesets{BR}mario_tileset.png")
    sheet = pygame.image.load(playersheet_path).convert_alpha()

    mario_size = (16, 16)
    m_width = mario_size[0]
    m_height = mario_size[1]

    static_mario = mario_select_resc(sheet, (0, 0), (0, 8, m_width, m_height), False)

    return { '0' : static_mario,
            '1' : mario_select_resc(sheet, (0, 0), (20, 8, m_width, m_height), False),
            '2' : mario_select_resc(sheet, (0, 0), (38, 8, m_width, m_height), False),
            '3' : mario_select_resc(sheet, (0, 0), (56, 8, m_width, m_height), False),
            '4' : mario_select_resc(sheet, (0, 0), (76, 8, m_width, m_height), False),
            '5' : mario_select_resc(sheet, (0, 0), (96, 8, m_width, m_height), False),
            '6' : mario_select_resc(sheet, (0, 0), (116, 8, m_width, m_height), False),
            '7' : mario_select_resc(sheet, (0, 0), (136, 8, m_width, m_height), False),
            '8' : mario_select_resc(sheet, (0, 0), (154, 8, m_width, m_height), False),
            '9' : mario_select_resc(sheet, (0, 0), (174, 8, m_width, m_height), False),
            '0_f' : mario_select_resc(sheet, (0, 0), (0, 8, m_width, m_height), True),
            '1_f' : mario_select_resc(sheet, (0, 0), (20, 8, m_width, m_height), True),
            '2_f' : mario_select_resc(sheet, (0, 0), (38, 8, m_width, m_height), True),
            '3_f' : mario_select_resc(sheet, (0, 0), (56, 8, m_width, m_height), True),
            '4_f' : mario_select_resc(sheet, (0, 0), (76, 8, m_width, m_height), True),
            '5_f' : mario_select_resc(sheet, (0, 0), (96, 8, m_width, m_height), True),
            '6_f' : mario_select_resc(sheet, (0, 0), (116, 8, m_width, m_height), True),
            '7_f' : mario_select_resc(sheet, (0, 0), (136, 8, m_width, m_height), True),
            '8_f' : mario_select_resc(sheet, (0, 0), (154, 8, m_width, m_height), True),
            '9_f' : mario_select_resc(sheet, (0, 0), (174, 8, m_width, m_height), True),
            'hb_size' : (c.S_MARIO_HITBOX_W, c.S_MARIO_HITBOX_H)}

@staticmethod
def b_mario_resc():
    playersheet_path = c.absolutePath(f"res{BR}tilesets{BR}mario_tileset.png")
    sheet = pygame.image.load(playersheet_path).convert_alpha()

    bigmario_size = (16, 32)
    m_width = bigmario_size[0]
    m_height = bigmario_size[1]

    static_bigmario = bigmario_select_resc(sheet, (0, 0), (0, 32, m_width, m_height), False)
    alt_bigmario = bigmario_select_resc(sheet, (0, 0), (116, 40, m_width, m_height - 8), False)

    # 0, 20, 38, 56, 76, 96, 106, 126, 144
    return { '0' : static_bigmario,
            '1' : bigmario_select_resc(sheet, (0, 0), (20, 32, m_width, m_height), False),
            '2' : bigmario_select_resc(sheet, (0, 0), (38, 32, m_width, m_height), False),
            '3' : bigmario_select_resc(sheet, (0, 0), (56, 32, m_width, m_height), False),
            '4' : bigmario_select_resc(sheet, (0, 0), (76, 32, m_width, m_height), False),
            '5' : bigmario_select_resc(sheet, (0, 0), (96, 32, m_width, m_height), False),
            '6' : alt_bigmario,
            '7' : bigmario_select_resc(sheet, (0, 0), (136, 32, m_width, m_height - 1), False),
            '8' : bigmario_select_resc(sheet, (0, 0), (154, 32, m_width, m_height - 1), False),
            '9' : bigmario_select_resc(sheet, (0, 0), (174, 32, m_width, m_height - 1), False),
            'fireball' : bigmario_select_resc(sheet, (0, 0), (136, 72, m_width, m_height), False),
            '0_f' : bigmario_select_resc(sheet, (0, 0), (0, 32, m_width, m_height), True),
            '1_f' : bigmario_select_resc(sheet, (0, 0), (20, 32, m_width, m_height), True),
            '2_f' : bigmario_select_resc(sheet, (0, 0), (38, 32, m_width, m_height), True),
            '3_f' : bigmario_select_resc(sheet, (0, 0), (56, 32, m_width, m_height), True),
            '4_f' : bigmario_select_resc(sheet, (0, 0), (76, 32, m_width, m_height), True),
            '5_f' : bigmario_select_resc(sheet, (0, 0), (96, 32, m_width, m_height), True),
            '6_f' : bigmario_select_resc(sheet, (0, 0), (116, 40, m_width, m_height - 8), True),
            '7_f' : bigmario_select_resc(sheet, (0, 0), (136, 32, m_width, m_height - 1), True),
            '8_f' : bigmario_select_resc(sheet, (0, 0), (154, 32, m_width, m_height - 1), True),
            '9_f' : bigmario_select_resc(sheet, (0, 0), (174, 32, m_width, m_height - 1), True),
            'fireball_f' : bigmario_select_resc(sheet, (0, 0), (136, 72, m_width, m_height), True),
            'hb_size' : (c.B_MARIO_HITBOX_W, c.B_MARIO_HITBOX_H),
            'hb_6_size' : (c.B_MARIO6_HITBOX_W, c.B_MARIO6_HITBOX_H)}

@staticmethod
def t_mario_resc() -> dict:
    playersheet_path = c.absolutePath(f"res{BR}tilesets{BR}mario_tileset.png")
    sheet = pygame.image.load(playersheet_path).convert_alpha()

    mario_sizes = ((16, 16), (16, 24), (16, 32))

    return { '0' : t_mario_select_resc(sheet, (0, 0), (0, 88, 16, 16), False),
        '1' : t_mario_select_resc(sheet, (0, 0), (18, 80, 16, 24), False),
        '2' : t_mario_select_resc(sheet, (0, 0), (36, 72, 16, 32), False),
        '0_f' : t_mario_select_resc(sheet, (0, 0), (0, 88, 16, 16), True),
        '1_f' : t_mario_select_resc(sheet, (0, 0), (18, 80, 16, 24), True),
        '2_f' : t_mario_select_resc(sheet, (0, 0), (36, 72, 16, 32), True)
    }

@staticmethod
def audioDict() -> dict:
    pathPrefix = f"res{BR}audio{BR}"
    return {
                '1-1_path' : c.absolutePath(f"{pathPrefix}1_1Level.ogg"),
                '1-1_path_underground' : c.absolutePath(f"{pathPrefix}1_1Level_Underground.ogg"),
                '1-1_ow_hurry_path' : c.absolutePath(f"{pathPrefix}overworld_hurry_up.ogg"),
                '1-1_ug_hurry_path' : c.absolutePath(f"{pathPrefix}underground_hurry_up.ogg"),
                'timescore' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}time_score.ogg")),
                'star' : c.absolutePath(f"{pathPrefix}star.ogg"),
                'warning' : c.absolutePath(f"{pathPrefix}hurry_up.wav"),
                'jump_small' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}jump_small.wav")),
                'jump_big' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}jump_big.wav")), 
                'bricksmash' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}bricksmash.wav")), 
                'bump' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}bump.wav")), 
                'coin' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}coin.wav")), 
                'down_flagpole' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}down_flagpole.wav")), 
                'fireball' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}fireball.wav")), 
                'kick' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}kick.wav")), 
                'pause' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}pause.wav")), 
                'pipe' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}pipe.wav")), 
                'powerup' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}powerup.wav")), 
                'powerup_appear' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}powerup_appear.wav")), 
                'stomp' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}stomp.wav")), 
                '1-up' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}1-up.wav")),
                'stage_clear' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}stage_clear.wav")),
                'gameover' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}gameover.wav")),
                'mariogg' : pygame.mixer.Sound(c.absolutePath(f"{pathPrefix}mariogg.wav"))
            }

@staticmethod
def objectDict():
    pygame.display.update()
    obj_path = c.absolutePath(f"res{BR}tilesets{BR}object_tileset.png")
    obj_surf = pygame.image.load(obj_path).convert_alpha()
    
    return {
            'shroom' : { 
                '1' : select_resc(obj_surf, (0, 0), (0, 8, 16, 16)),
                'hb_size' : (16, 16)
            },
            'shroom_1-up' : { 
                '1' : select_resc(obj_surf, (0, 0), (0, 26, 16, 16)),
                'hb_size' : (16, 16)
            },
            'fireflower' : {
                # 1 varies depending upon mario/fire state
                '1' : select_resc(obj_surf, (0, 0), (32, 8, 16, 16)),
                '2' : select_resc(obj_surf, (0, 0), (50, 8, 16, 16)),
                '3' : select_resc(obj_surf, (0, 0), (68, 8, 16, 16)),
                '4' : select_resc(obj_surf, (0, 0), (86, 8, 16, 16)),
                'hb_size' : (16, 16)
            },
            'star' : {
                # 1 varies depending upon mario/fire state
                '1' : select_resc(obj_surf, (0, 0), (106, 8, 16, 16)),
                '2' : select_resc(obj_surf, (0, 0), (124, 8, 16, 16)),
                '3' : select_resc(obj_surf, (0, 0), (142, 8, 16, 16)),
                '4' : select_resc(obj_surf, (0, 0), (160, 8, 16, 16)),
                'hb_size' : (16, 16)
            },
            'flag' : select_flag(obj_surf, (92, 90), (16, 16)),
            'oflag': select_resc(obj_surf, (0, 0), (110, 90, 16, 16)),
            'bricks_particle' : {
                '1' : select_resc(obj_surf, (0, 0), (180, 26, 8, 8)),
                '2' : select_resc(obj_surf, (0, 0), (190, 26, 8, 8)),
                '3' : select_resc(obj_surf, (0, 0), (200, 26, 8, 8)),
                '4' : select_resc(obj_surf, (0, 0), (210, 26, 8, 8))
            },
            'coin_particle' : {
                '1' : select_resc(obj_surf, (0, 0), (180, 36, 8, 16)),
                '2' : select_resc(obj_surf, (0, 0), (190, 36, 8, 16)),
                '3' : select_resc(obj_surf, (0, 0), (200, 36, 8, 16)),
                '4' : select_resc(obj_surf, (0, 0), (210, 36, 8, 16))
            },
            'fireball_particle' : {
                '1' : select_resc(obj_surf, (0, 0), (180, 54, 8, 8)),
                '2' : select_resc(obj_surf, (0, 0), (190, 54, 8, 8)),
                '3' : select_resc(obj_surf, (0, 0), (200, 54, 8, 8)),
                '4' : select_resc(obj_surf, (0, 0), (210, 54, 8, 8))
            },
            'fireball_exp_particle' : {
                '1' : select_resc(obj_surf, (0, 0), (180, 64, 16, 16)),
                '2' : select_resc(obj_surf, (0, 0), (198, 64, 16, 16)),
                '3' : select_resc(obj_surf, (0, 0), (216, 64, 16, 16))
            },
            'scores' : {
                '100' : select_resc(obj_surf, (0, 0), (234, 26, 16, 8)),
                '200' : select_resc(obj_surf, (0, 0), (234, 36, 16, 8)),
                '400' : select_resc(obj_surf, (0, 0), (234, 46, 16, 8)),
                '500' : select_resc(obj_surf, (0, 0), (234, 56, 16, 8)),
                '800' : select_resc(obj_surf, (0, 0), (234, 66, 16, 8)),
                '1000' : select_resc(obj_surf, (0, 0), (252, 26, 16, 8)),
                '2000' : select_resc(obj_surf, (0, 0), (252, 36, 16, 8)),
                '4000' : select_resc(obj_surf, (0, 0), (252, 46, 16, 8)),
                '5000' : select_resc(obj_surf, (0, 0), (252, 56, 16, 8)),
                '8000' : select_resc(obj_surf, (0, 0), (252, 66, 16, 8)),
                '1-up' : select_resc(obj_surf, (0, 0), (252, 76, 16, 8)),
            }
           }

@staticmethod
def blockDict():
    pygame.display.update()
    map_path = c.absolutePath(f"res{BR}tilesets{BR}map_tileset.png")
    map_sheet = pygame.image.load(map_path)
    map_sheet.convert_alpha()

    return {
            'bricks' : select_resc(map_sheet, (0, 0), (17, 16, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
            'bricks_flat' : select_resc(map_sheet, (0, 0), (34, 16, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
            'coin' : {
                '1' : select_resc(map_sheet, (0, 0), (394, 95, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
                '2' : select_resc(map_sheet, (0, 0), (411, 95, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
                '3' : select_resc(map_sheet, (0, 0), (428, 95, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
                'hb_size' : (12, 16)
            },
            '?block' : {
                '1' : select_resc(map_sheet, (0, 0), (298, 78, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
                '2' : select_resc(map_sheet, (0, 0), (315, 78, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
                '3' : select_resc(map_sheet, (0, 0), (332, 78, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
                '4' : select_resc(map_sheet, (0, 0), (349, 78, 16, 16), c.MAP_TEXTURE_ALPHA_COLOR),
            }
           }

@staticmethod
def uiDict():
    pygame.display.update()
    playersheet_path = c.absolutePath(f"res{BR}tilesets{BR}mario_tileset.png")
    sheet = pygame.image.load(playersheet_path).convert_alpha()

    icon = mario_select_resc(sheet, (0,0), (0, 8, 16, 16), False).convert_alpha()

    main_menu_path = c.absolutePath(f"res{BR}tilesets{BR}SMB_Title_Screen.png")
    main_menu_surf = pygame.image.load(main_menu_path)

    coin_icon = pygame.Surface((5, 8))
    coin_icon.blit(main_menu_surf, (0, 0), (89, 16, 5, 8))
    coin_icon.set_colorkey((146,144,255))

    # EQUIS DE LA UI
    x_path = c.absolutePath(f"res{BR}tilesets{BR}x.png")
    x_surf = pygame.image.load(x_path)
    x_surf.set_colorkey(c.TEXTURE_ALPHA_COLOR)
    x_surf.convert_alpha()

    s_surf = pygame.Surface((8, 8))
    s_surf.blit(main_menu_surf, (0, 0), (72, 136, 8, 8))
    s_surf.set_colorkey(c.TEXTURE_ALPHA_COLOR)
    s_surf.convert_alpha()

    pygame.display.set_icon(icon)

    return {
            'coin_icon' : coin_icon,
            'mario_icon' : icon,
            'x' : x_surf,
            'selector' : s_surf,
            'font_path' : c.absolutePath(f"res{BR}fonts{BR}super_mario_bros_fon.ttf")
            }

@staticmethod
def entitiesDict():
    enemies_path = c.absolutePath(f"res{BR}tilesets{BR}enemies_tileset.png")
    enemies_surf = pygame.image.load(enemies_path)

    return {
             'goomba' : {
                '1' : select_resc(enemies_surf, (0, 0), (0, 16, 16, 16)), 
                '2' : select_resc(enemies_surf, (0, 0), (18, 16, 16, 16)), 
                '3' : select_resc(enemies_surf, (0, 0), (36, 24, 16, 8)),
                'hb_size' : (16, 16),
                'hb_size_3' : (16, 8)
             },
             'koopa' : {
                '1' : select_resc(enemies_surf, (0, 0), (0, 112, 16, 24)),
                '2' : select_resc(enemies_surf, (0, 0), (18, 112, 16, 24)),
                '3' : select_resc(enemies_surf, (0, 0), (72, 120, 16, 14)),
                '4' : select_resc(enemies_surf, (0, 0), (90, 120, 16, 14)),
                '1_f' : pygame.transform.flip(select_resc(enemies_surf, (0, 0), (0, 112, 16, 24)), True, False),
                '2_f' : pygame.transform.flip(select_resc(enemies_surf, (0, 0), (18, 112, 16, 24)), True, False),
                '3_f' : pygame.transform.flip(select_resc(enemies_surf, (0, 0), (72, 120, 16, 14)), True, False),
                '4_f' : pygame.transform.flip(select_resc(enemies_surf, (0, 0), (90, 120, 16, 14)), True, False),
                'hb_size' : (16, 24),
                'hb_size_2' : (16, 16)
             }
           }

@staticmethod
def parseCSVData():
    # df = pd.read_csv(c.absolutePath("resources\\levels\\1-1\\1-1_interactuables.csv"))
    csv_data = []
    with open(c.absolutePath(f"res{BR}levels{BR}1-1{BR}1-1_interactuables.csv"), 'r') as csv:
        lines = csv.readlines()
        for i, line in enumerate(lines):
            if i == 0: continue

            if line.strip() == "": continue
            f = line.split(",")
            if len(f) != 5: continue
            a, b, g, d, e = f
            e = e.strip()

            csv_data.append( (a, b, int(g), int(d), e) )
    # (chunk_index, type, x, y, data)    
    # df.to_records(index = False)
    return csv_data

# CHECK CSV DATA WHILE FOR IS LOOPING
@staticmethod
def parseLevelMap(sheet: pygame.Surface, pos1: tuple, pos2: tuple, csv_data: list[tuple], worldID: str, data: dict, tilesize: int = 16, x_offsets = (-64, 64), y_offsets = (-64, 64)):
    x1, y1 = pos1
    x2, y2 = pos2
    level_map_li = []  
    xo1, xo2 = x_offsets
    yo1, yo2 = y_offsets
    for xi in range(x1, x2, tilesize):
        column = []
        for yi in range(y1, y2, tilesize):
            tile = pygame.Surface((tilesize, tilesize))
            tile.blit(sheet, (0, 0), (xi, yi, tilesize, tilesize))
            column.append( Tile((xi, yi), tile ) )
        level_map_li.append(column)

    level_map = LevelMap(level_map_li, (0 + xo1, abs(x2 - x1) + xo2), (0 + yo1, abs(y2 - y1) + yo2), tilesize, data)

    for entry in csv_data:
        if entry[0] != worldID: continue

        w_id, obj_type, x, y, data = entry 
        if obj_type == c.GROUND:
            if data == "o":
                level_map.overlay.append(KinecticObject((16, 16), (x, y), c.GROUND))
            level_map.objects.append(KinecticObject((16, 16), (x, y), c.GROUND))
        elif obj_type == c.BRICKS:
            level_map.objects.append(Bricks((x, y), data))
        elif obj_type == c.Q_BLOCK:
            level_map.objects.append(MysteryBlock((x, y), data))
        elif obj_type == c.I_BLOCK:
            level_map.objects.append(iBlock((x, y), data))
        elif obj_type == c.TUBE:
            level_map.overlay.append(Tube((x, y), data))
            level_map.objects.append(Tube((x, y), data))
        elif obj_type == c.FLAG:
            level_map.objects.append(Flag((x, y), data))
        elif obj_type == c.COIN:
            level_map.objects.append(Coin((x, y), data))
        elif obj_type == c.GOOMBA:
            level_map.entities.append(Goomba((x, y), data))
        elif obj_type == c.KOOPA:
            level_map.entities.append(Koopa((x, y), data))
        elif obj_type == "oflag":
            level_map.miniFlag = OFlag((x, y), data)
            level_map.objects.append(level_map.miniFlag)
        elif obj_type == c.CASTLEDOOR:
            level_map.castledoor = CastleDoor((x, y), data)
    return level_map

@staticmethod
def parseLevel1Maps(sheet: pygame.Surface, csv_data: list[tuple]):
    return {
        'bg' : sheet,
        'A' : parseLevelMap(sheet, (0, 0), (3376, 240), csv_data, 
                    'A', data={ 'map_type' : c.MAP_OVERWORLD }, x_offsets=(-64, 64) ),
        'B' : parseLevelMap(sheet, (768, 240), (768 + 256, 480), csv_data, 
                    'B', data={ 'map_type' : c.MAP_UNDERGROUND }, x_offsets=(-64, 64)),
        'objects' : 'None',
        'entities' : parseEntities(csv_data)
    }

@staticmethod
def parseEntities(csv: list[tuple]):
    for entry in csv:
        pass
    return []

@staticmethod
def select_resc(sheet: pygame.Surface, coords: tuple, area: tuple, alpha_color: tuple = c.TEXTURE_ALPHA_COLOR):

    r_size = (area[2], area[3])
    result = pygame.Surface(r_size)
    result.convert_alpha()
    result.blit(sheet, coords, area)
    result.set_colorkey(alpha_color)
    return result

@staticmethod
def select_flag(sheet: pygame.Surface, coords: tuple, size: tuple):
    flag = select_resc(sheet, (0, 0), (coords[0], coords[1], size[0], size[1])) 
    return flag

@staticmethod
def mario_select_resc(sheet : pygame.Surface, coords: tuple, size: pygame.Rect, flip: bool):
    # Color chroma: NEGRO
    ALPHA_COL = (0, 0, 0)

    mario_size = (16, 16)
    mario_0 = pygame.Surface(mario_size)
    mario_0.blit(sheet, coords, size)
    mario_0 = mario_0 if not flip else pygame.transform.flip(mario_0, True, False)
    mario_0.set_colorkey(ALPHA_COL)
    mario_0.convert_alpha()
    return mario_0

@staticmethod
def bigmario_select_resc(sheet : pygame.Surface, coords: tuple, size: pygame.Rect, flip: bool):
    # Color chroma: NEGRO
    ALPHA_COL = (0, 0, 0)

    mario_size = (size[2], size[3])
    mario_0 = pygame.Surface(mario_size)
    mario_0.blit(sheet, coords, size)
    mario_0 = mario_0 if not flip else pygame.transform.flip(mario_0, True, False)
    mario_0.set_colorkey(ALPHA_COL)
    mario_0.convert_alpha()
    return mario_0

@staticmethod
def t_mario_select_resc(sheet : pygame.Surface, coords: tuple, size: tuple, flip: bool):
    # Color chroma: NEGRO
    ALPHA_COL = (0, 0, 0)

    mario_size = (size[2], size[3])
    mario_0 = pygame.Surface(mario_size)
    mario_0.blit(sheet, coords, size)
    mario_0 = mario_0 if not flip else pygame.transform.flip(mario_0, True, False)
    mario_0.set_colorkey(ALPHA_COL)
    mario_0.convert_alpha()
    return mario_0

###