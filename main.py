
import pygame
from pygame import gfxdraw
from pygame.locals import QUIT, MOUSEBUTTONDOWN, K_LALT, K_RALT, K_F4, K_SPACE

from sys import exit as sys_exit
from os import environ
from os.path import join as os_path_join
from gc import collect as gc_collect
from configparser import ConfigParser

from win32gui import SetWindowLong, GetWindowLong, SetLayeredWindowAttributes, SetWindowPos, EnableWindow
from win32con import GWL_EXSTYLE, WS_EX_LAYERED, LWA_COLORKEY
from win32api import RGB

from socket import gethostname, gethostbyname
from webbrowser import open as open_web


WIDTH = 250
HEIGHT = 300

FPS = 15

COL_WG = (56, 42, 29)   #382a1d | mocha
COL_BG = (222, 203, 177)   #decbb1 | whip
COL_S1 = (182, 155, 125)   #b69b7d | heavy cream

COL_MAC_RED = (255, 96, 92)   #ff605c | sunset orange
COL_MAC_YELLOW = (255, 189, 68)   #ffbd44 | pastel orange
COL_MAC_GREEN = (0, 202, 78)   #00ca4e | malachite

CONFIGPATH = os_path_join('config.ini')
FONTPATH = os_path_join('Fonts', 'JetBrainsMonoNL-Bold.ttf')
ABOUTSITE = 'https://www.buymeacoffee.com/ntduck'


class SysButton:   # 10 x 10
    def __init__(self, pos: tuple[int], size: int, col: tuple[int], slot: int):
        self.pos = pos
        self.size = (size, size)
        self.col = col
        self.slot = slot   # [0, 1, 2]

    def render(self, window: pygame.Surface) -> pygame.Rect:
        return pygame.draw.rect(window, self.col, self.pos + self.size)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]) -> bool:
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.render(window).collidepoint(mouse_pos)

    def onToggle(self):
        if self.slot == 0:
            pygame.quit()
            sys_exit()
        elif self.slot == 1:
            pygame.display.iconify()
        else:
            pygame.display.iconify()


class SettingButton:   # 32 x 32
    def __init__(self, pos: tuple[int], col: tuple[int]):
        self.pos = pos
        self.col = col

        self.img_app = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        for _rectvalue in [pos + (8, 8) for pos in ((0, 0), (12, 0), (24, 0), (0, 12), (12, 12), (24, 12), (0, 24), (12, 24), (24, 24))]:
            pygame.draw.rect(self.img_app, self.col, _rectvalue)

        self.img_cfg = pygame.Surface((31.5, 31.5), pygame.SRCALPHA).convert_alpha()
        for _rectvalue in [pos + (17.5, 3.5) for pos in ((0, 3.5), (14, 14), (14, 24.5))] + [pos + (10.5, 3.5) for pos in ((21, 3.5), (0, 14), (0, 24.5))] + [pos + (3.5, 10.5) for pos in ((21, 0), (7, 10.5), (14, 21))]:
            pygame.draw.rect(self.img_cfg, self.col, _rectvalue)

        self.isAppOn = True

    def render(self, window: pygame.Surface) -> pygame.Rect:
        if self.isAppOn:
            return window.blit(self.img_app, self.pos)
        return window.blit(self.img_cfg, (self.pos[0]+0.5, self.pos[1]))

    def isToggled(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                self.isAppOn = not self.isAppOn


class Number:   # 80
    def __init__(self, pos: tuple[int], col: tuple[int], size: int, slot: int):
        self.pos = pos
        self.col = col
        self.slot = slot   # [0, 1, 2, 3]
        self.font = pygame.font.Font(FONTPATH, size)

    def num_to_display(self, time: int) -> str:
        minute, second = divmod(time, 60)
        return f'{minute:02d}{second:02d}'[self.slot]

    def render(self, window: pygame.Surface, time: int) -> pygame.Rect:
        text = self.font.render(self.num_to_display(time), True, self.col).convert_alpha()
        text_rect = text.get_rect(center=self.pos)
        return window.blit(text, text_rect)


class Colon:   # 80
    def __init__(self, pos: tuple[int], col: tuple[int], size: int):
        self.pos = pos
        self.col = col
        self.font = pygame.font.Font(FONTPATH, size)

    def render(self, window: pygame.Surface) -> pygame.Rect:
        text = self.font.render(':', True, self.col).convert_alpha()
        text_rect = text.get_rect(center=self.pos)
        return window.blit(text, text_rect)


class MainButton:   # 32 x 32
    def __init__(self, pos: tuple[int], col: tuple[int]):
        self.pos = pos
        self.col = col

        self.img_play = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        for _rectvalue in [(2, 0, 9.5, 32), (20.5, 0, 9.5, 32)]:
            pygame.draw.rect(self.img_play, self.col, _rectvalue)

        self.img_pause = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        gfxdraw.aapolygon(self.img_pause, ((3, 0), (29, 16), (3, 32)), self.col)
        gfxdraw.filled_polygon(self.img_pause, ((3, 0), (29, 16), (3, 32)), self.col)

        self.isPaused = True
        self.key_ready = False   # track

    def render(self, window: pygame.Surface) -> pygame.Rect:
        if self.isPaused:
            return window.blit(self.img_pause, self.pos)
        return window.blit(self.img_play, self.pos)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                self.isPaused = not self.isPaused


class SkipButton:   # 32 x 32
    def __init__(self, pos: tuple[int], col: tuple[int]):
        self.pos = pos
        self.col = col

        self.img = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        gfxdraw.aapolygon(self.img, ((0, 0), (22.5, 16), (0, 32)), self.col)
        gfxdraw.filled_polygon(self.img, ((0, 0), (22.5, 16), (0, 32)), self.col)
        pygame.draw.rect(self.img, self.col, (26.5, 0, 5.5, 32))

        self.isPressed = False

    def render(self, window: pygame.Surface) -> pygame.Rect:
        return window.blit(self.img, self.pos)
    
    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                self.isPressed = True


class ConfigNumber:   # 30
    def __init__(self, pos: tuple[int], col: tuple[int], size: int, val: int):
        self.pos = pos
        self.col = col
        self.val = val
        self.font = pygame.font.Font(FONTPATH, size)

        self.isChangeReset = True

    def render(self, window: pygame.Surface) -> pygame.Rect:
        text = self.font.render(str(self.val), True, self.col).convert_alpha()
        text_rect = text.get_rect(center=self.pos)
        return window.blit(text, text_rect)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]) -> bool:
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                if self.val == 9:
                    self.val = 0
                else:
                    self.val += 1
                self.isChangeReset = False


class ConfigClusterInt:   # 63 x 32
    def __init__(self, pos: tuple[int], col: tuple[int], var: str):
        self.pos = pos
        self.col = col
        self.var = var

        if self.var == 'interval':
            self.vals = '{:02d}'.format(cfg.getint('time_values', self.var))
        else:
            self.vals = '{:02d}'.format(cfg.getint('time_values', self.var)//60)

        self.img = pygame.Surface((63, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.img, self.col, (0, 0, 10, 32))

        self.ConfigNumber_0 = ConfigNumber((self.pos[0]+31, self.pos[1]+16), COL_BG, 30, int(self.vals[0]))
        self.ConfigNumber_1 = ConfigNumber((self.pos[0]+47, self.pos[1]+16), COL_BG, 30, int(self.vals[1]))
        
    def render(self, window: pygame.Surface):
        pygame.draw.rect(self.img, COL_WG, (15, 0, 48, 32))
        window.blit(self.img, self.pos)
        self.ConfigNumber_0.render(window)
        self.ConfigNumber_1.render(window)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]):
        self.ConfigNumber_0.isMouseOn(window, event, mouse_pos)
        self.ConfigNumber_1.isMouseOn(window, event, mouse_pos)

    def save_changes(self):
        if self.var == 'interval':
            cfg.set('time_values', self.var, str(self.ConfigNumber_0.val*10 + self.ConfigNumber_1.val))
        else:
            cfg.set('time_values', self.var, str(self.ConfigNumber_0.val*600 + self.ConfigNumber_1.val*60))

    def reset_to_default(self):
        if self.var == 'interval':
            self.vals = '{:02d}'.format(cfg.getint('time_values', self.var))
        else:
            self.vals = '{:02d}'.format(cfg.getint('time_values', self.var)//60)
        self.ConfigNumber_0.val = int(self.vals[0])
        self.ConfigNumber_1.val = int(self.vals[1])

    def reset_changes(self):
        if not self.ConfigNumber_0.isChangeReset or not self.ConfigNumber_1.isChangeReset:
            self.reset_to_default()
            self.ConfigNumber_0.isChangeReset = self.ConfigNumber_1.isChangeReset = True


class ConfigClusterBool:   # 63 x 32
    def __init__(self, pos: tuple[int], col: tuple[int], var: str):
        self.pos = pos
        self.col = col
        self.var = var
        self.val = cfg.getint('bool_values', self.var)

        self.img = pygame.Surface((63, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.img, self.col, (0, 0, 10, 32))

        self.isChangeReset = True

    def render(self, window: pygame.Surface) -> pygame.Rect:
        pygame.draw.rect(self.img, COL_WG, (15, 0, 48, 32))
        window.blit(self.img, self.pos)
        if not self.val:
            return pygame.draw.rect(window, COL_MAC_RED, (self.pos[0]+18, self.pos[1]+3, 21, 26))
        else:
            return pygame.draw.rect(window, COL_MAC_GREEN, (self.pos[0]+39, self.pos[1]+3, 21, 26))

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]) -> bool:
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                self.val = int(not self.val)
                self.isChangeReset = False

    def save_changes(self):
        cfg.set('bool_values', self.var, str(self.val))

    def reset_to_default(self):
        self.val = cfg.getint('bool_values', self.var)
    
    def reset_changes(self):
        if not self.isChangeReset:
            self.reset_to_default()
            self.isChangeReset = True


class ConfigSaveButton:   # 32 x 32
    def __init__(self, pos: tuple[int], col: tuple[int]):
        self.pos = pos
        self.col = col

        self.img = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.img, self.col, (10, 0, 12, 11.5))
        pygame.draw.rect(self.img, self.col, (3, 29, 26, 3))
        gfxdraw.aapolygon(self.img, ((3, 11.5), (16, 24.5), (29, 11.5)), self.col)
        gfxdraw.filled_polygon(self.img, ((3, 11.5), (16, 24.5), (29, 11.5)), self.col)

    def render(self, window: pygame.Surface) -> pygame.Rect:
        return window.blit(self.img, self.pos)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int], ConfigClusterInts: list[ConfigClusterInt], ConfigClusterBools: list[ConfigClusterBool]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                for ConfigClusterInt in ConfigClusterInts:
                    ConfigClusterInt.save_changes()
                for ConfigClusterBool in ConfigClusterBools:
                    ConfigClusterBool.save_changes()
                with open(CONFIGPATH, 'w') as configfile:
                    cfg.write(configfile)


class ConfigResetButton:   # 32 x 32
    def __init__(self, pos: tuple[int], col: tuple[int]):
        self.pos = pos
        self.col = col

        self.img = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.img, self.col, (10, 1.5, 12, 2))
        pygame.draw.rect(self.img, self.col, (3, 3.5, 26, 3.5))
        pygame.draw.rect(self.img, self.col, (5, 8.5, 22, 22))

    def render(self, window: pygame.Surface) -> pygame.Rect:
        return window.blit(self.img, self.pos)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int], ConfigClusterInts: list[ConfigClusterInt], ConfigClusterBools: list[ConfigClusterBool]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                DEFAULT = {
                    'work': '1500',
                    'short_break': '300',
                    'long_break': '1800',
                    'interval': '4',
                    'isautoswitch': '0',
                    'issoundon': '0'
                }

                cfg.clear()
                cfg.add_section('time_values')
                for opt in tuple(DEFAULT.keys())[0:4]:
                    cfg.set('time_values', opt, DEFAULT[opt])
                cfg.add_section('bool_values')
                for opt in tuple(DEFAULT.keys())[4:6]:
                    cfg.set('bool_values', opt, DEFAULT[opt])

                with open(CONFIGPATH, 'w') as configfile:
                    cfg.write(configfile)

                for ConfigClusterInt in ConfigClusterInts:
                    ConfigClusterInt.reset_to_default()
                for ConfigClusterBool in ConfigClusterBools:
                    ConfigClusterBool.reset_to_default()

                del DEFAULT


class ConfigAboutButton:   # 32 x 32
    def __init__(self, pos: tuple[int], col: tuple[int]):
        self.pos = pos
        self.col = col

        self.img = pygame.Surface((32, 32)).convert()
        self.img.fill(COL_MAC_YELLOW)
        pygame.draw.rect(self.img, self.col, (4, 16, 4, 4))
        pygame.draw.rect(self.img, self.col, (24, 16, 4, 4))
        pygame.draw.rect(self.img, (184, 134, 11), (12, 16, 8, 4))
    
    def render(self, window: pygame.Surface) -> pygame.Rect:
        return window.blit(self.img, self.pos)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                open_web(ABOUTSITE, new=2, autoraise=True)
                    

class PPSHandler:   # play | pause | skip
    def __init__(self):
        self.time = TIMES[0]
        self.time_prev_tracker = 0   # 0: 'work' | 1: 'short break'
        self.interval_tracker = 0

        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def change_time(self):
        if self.interval_tracker == INTERVAL:
            self.time = TIMES[2]
            self.interval_tracker = 0
        else:
            self.time_prev_tracker = not self.time_prev_tracker
            self.time = TIMES[self.time_prev_tracker]
            if self.time_prev_tracker == 1:
                self.interval_tracker += 1

    def handle(self, event: pygame.event.Event, MainButton: MainButton, SkipButton: SkipButton):
        if event.type == pygame.USEREVENT:
            if not MainButton.key_ready:
                MainButton.key_ready = True
            if not MainButton.isPaused:
                if self.time > 0:
                    self.time -= 1
                else:
                    if not IS_AUTO_SWITCH:
                        MainButton.isPaused = True
                    self.change_time()
        if SkipButton.isPressed:
            SkipButton.isPressed = False
            MainButton.isPaused = True
            self.change_time()


class SetupHandler:
    def __init__(self):
        self.place_pos = (pygame.display.get_desktop_sizes()[0][0]-310, 50)   # 50px from top right corner

    def clean_config_file(self):
        DEFAULT = {
            'work': '1500',
            'short_break': '300',
            'long_break': '1800',
            'interval': '4',
            'isautoswitch': '0',
            'issoundon': '0'
        }

        global cfg
        cfg = ConfigParser()

        try:
            cfg.read(CONFIGPATH)
        except:
            cfg.clear()
            cfg.add_section('time_values')
            for opt in tuple(DEFAULT.keys())[0:4]:
                cfg.set('time_values', opt, DEFAULT[opt])
            cfg.add_section('bool_values')
            for opt in tuple(DEFAULT.keys())[4:6]:
                cfg.set('bool_values', opt, DEFAULT[opt])
        else:
            for section in ('time_values', 'bool_values'):
                if not cfg.has_section(section):
                    cfg.add_section(section)
            for section in cfg.sections():
                if section == 'time_values':
                    for opt in tuple(DEFAULT.keys())[0:4]:
                        if not cfg.has_option(section, opt):
                            cfg.set(section, opt, DEFAULT[opt])
                    for (opt, val) in cfg.items(section):
                        if opt in tuple(DEFAULT.keys())[0:3]:
                            if not val.isnumeric() or int(val) < 60 or int(val) > 5940:
                                cfg.set(section, opt, DEFAULT[opt])
                        elif opt == tuple(DEFAULT.keys())[3]:
                            if not val.isnumeric() or int(val) < 1 or int(val) > 99:
                                cfg.set(section, opt, DEFAULT[opt])
                        else:
                            cfg.remove_option(section, opt)
                elif section == 'bool_values':
                    for opt in tuple(DEFAULT.keys())[4:6]:
                        if not cfg.has_option(section, opt):
                            cfg.set(section, opt, DEFAULT[opt])
                    for (opt, val) in cfg.items(section):
                        if opt in tuple(DEFAULT.keys())[4:6]:
                            if not (val.isnumeric() or val == '0' or val == '1'):
                                cfg.set(section, opt, DEFAULT[opt])
                        else:
                            cfg.remove_option(section, opt)
                else:
                    cfg.remove_section(section)
        finally:
            with open(CONFIGPATH, 'w') as configfile:
                cfg.write(configfile)

        global TIMES, INTERVAL, IS_AUTO_SWITCH, IS_SOUND_ON

        TIMES = [cfg.getint('time_values', var) for var in tuple(DEFAULT.keys())[0:3]]
        INTERVAL = cfg.getint('time_values', tuple(DEFAULT.keys())[3])
        IS_AUTO_SWITCH = cfg.getboolean('bool_values', tuple(DEFAULT.keys())[4])
        IS_SOUND_ON = cfg.getboolean('bool_values', tuple(DEFAULT.keys())[5])

        del DEFAULT

    def define_dimension(self):
        environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % self.place_pos

    def define_icon(self, col: tuple[int]):
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        for _rectvalue in [pos + (8, 8) for pos in ((0, 0), (12, 0), (24, 0), (0, 12), (12, 12), (24, 12), (0, 24), (12, 24), (24, 24))]:
            pygame.draw.rect(icon, col, _rectvalue)

        pygame.display.set_icon(icon)
        del icon
    
    def define_transparent_col(self, col: tuple[int], window: pygame.Surface) -> pygame.Rect:   # make a color value transparent
        hwnd = pygame.display.get_wm_info()['window']
        SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED)
        SetLayeredWindowAttributes(hwnd, RGB(*col), 0, LWA_COLORKEY)
        del hwnd
        return window.fill(col)

    def set_window_on_top(self):
        return SetWindowPos(pygame.display.get_wm_info()['window'], -1, self.place_pos[0], self.place_pos[1], 0, 0, 1)


class App:
    def __init__(self):
        pygame.font.init()
        pygame.init()

        self.SetupHandler = SetupHandler()
        self.SetupHandler.clean_config_file()
        self.SetupHandler.define_dimension()
        self.SetupHandler.define_icon(COL_MAC_YELLOW)
        pygame.display.set_caption(gethostbyname(gethostname()))

        self.MasterWindow = pygame.display.set_mode((WIDTH+10, HEIGHT+10), pygame.NOFRAME)

        self.SetupHandler.define_transparent_col((0, 0, 0), self.MasterWindow)
        self.SetupHandler.set_window_on_top()

        decoywindow = pygame.Surface((WIDTH, HEIGHT)).convert()
        decoywindow.fill(COL_S1)
        self.window = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.MasterWindow.blit(decoywindow, (10, 10))
        del decoywindow

        self.PPSHandler = PPSHandler()

        self.SysButton_0 = SysButton((25, 25), 10, COL_MAC_RED, 0)
        self.SysButton_1 = SysButton((40, 25), 10, COL_MAC_YELLOW, 1)
        self.SysButton_2 = SysButton((55, 25), 10, COL_MAC_GREEN, 2)
        self.SettingButton = SettingButton((193, 25), COL_WG)
        self.Number_0 = Number((45, 155), COL_WG, 80, 0)
        self.Number_1 = Number((87, 155), COL_WG, 80, 1)
        self.Number_2 = Number((163, 155), COL_WG, 80, 2)
        self.Number_3 = Number((205, 155), COL_WG, 80, 3)
        self.Colon = Colon((125, 150), COL_WG, 80)
        self.MainButton = MainButton((109, 243), COL_WG)
        self.SkipButton = SkipButton((193, 243), COL_WG)
        self.ConfigClusterInt_0 = ConfigClusterInt((35, 92), COL_MAC_RED, 'work')
        self.ConfigClusterInt_1 = ConfigClusterInt((50, 139), COL_MAC_YELLOW, 'short_break')
        self.ConfigClusterInt_2 = ConfigClusterInt((35, 186), COL_MAC_GREEN, 'long_break')
        self.ConfigClusterInt_3 = ConfigClusterInt((135, 92), COL_S1, 'interval')
        self.ConfigClusterBool_0 = ConfigClusterBool((150, 139), COL_S1, 'isautoswitch')
        self.ConfigClusterBool_1 = ConfigClusterBool((135, 186), COL_S1, 'issoundon')
        self.ConfigSaveButton = ConfigSaveButton((109, 243), COL_WG)
        self.ConfigResetButton = ConfigResetButton((156, 243), COL_WG)
        self.ConfigAboutButton = ConfigAboutButton((62, 243), COL_WG)

        self.Clock = pygame.time.Clock()

    def render(
        self,
        window: pygame.Surface,
        SysButtons: list[SysButton],
        SettingButton: SettingButton,
        Numbers: list[Number],
        Colon: Colon,
        MainButton: MainButton,
        SkipButton: SkipButton,
        ConfigClusterInts: list[ConfigClusterInt],
        ConfigClusterBools: list[ConfigClusterBool],
        ConfigSaveButton: ConfigSaveButton,
        ConfigResetButton: ConfigResetButton,
        ConfigAboutButton: ConfigAboutButton,
        PPSHandler: PPSHandler
    ):
        window.fill(COL_BG)
        gfxdraw.aapolygon(window, ((0, 0), (150, 0), (90, 60), (0, 60)), COL_S1)
        gfxdraw.filled_polygon(window, ((0, 0), (150, 0), (90, 60), (0, 60)), COL_S1)
        
        if self.SettingButton.isAppOn:
            for Number in Numbers:
                Number.render(window, PPSHandler.time)
            Colon.render(window)
            MainButton.render(window)
            SkipButton.render(window)

        else:
            for ConfigClusterInt in ConfigClusterInts:
                ConfigClusterInt.render(window)
            for ConfigClusterBool in ConfigClusterBools:
                ConfigClusterBool.render(window)
            ConfigSaveButton.render(window)
            ConfigResetButton.render(window)
            ConfigAboutButton.render(window)

        for SysButton in SysButtons:
            SysButton.render(window)
        SettingButton.render(window)

        self.MasterWindow.blit(window, (0, 0))

    def handle_mouse(
        self,
        window: pygame.Surface,
        event: pygame.event.Event,
        mouse_pos: tuple[int],
        SysButtons: list[SysButton],
        SettingButton: SettingButton,
        MainButton: MainButton,
        SkipButton: SkipButton,
        ConfigClusterInts: list[ConfigClusterInt],
        ConfigClusterBools: list[ConfigClusterBool],
        ConfigSaveButton: ConfigSaveButton,
        ConfigResetButton: ConfigResetButton,
        ConfigAboutButton: ConfigAboutButton,
        PPSHandler: PPSHandler
    ):
        PPSHandler.handle(event, MainButton, SkipButton)

        if pygame.mouse.get_focused():

            SettingButton.isToggled(window, event, mouse_pos)

            for SysButton in SysButtons:
                if SysButton.isMouseOn(window, event, mouse_pos):
                    SysButton.onToggle()

            if SettingButton.isAppOn:
                MainButton.isMouseOn(window, event, mouse_pos)
                SkipButton.isMouseOn(window, event, mouse_pos)
                for ConfigClusterInt in ConfigClusterInts:
                    ConfigClusterInt.reset_changes()
                for ConfigClusterBool in ConfigClusterBools:
                    ConfigClusterBool.reset_changes()

            else:
                for ConfigClusterInt in ConfigClusterInts:
                    ConfigClusterInt.isMouseOn(window, event, mouse_pos)
                for ConfigClusterBool in ConfigClusterBools:
                    ConfigClusterBool.isMouseOn(window, event, mouse_pos)
                ConfigSaveButton.isMouseOn(window, event, mouse_pos, ConfigClusterInts, ConfigClusterBools)
                ConfigResetButton.isMouseOn(window, event, mouse_pos, ConfigClusterInts, ConfigClusterBools)
                ConfigAboutButton.isMouseOn(window, event, mouse_pos)

    def handle_key(self, keys: any, MainButton: MainButton):
        if keys[K_LALT] or keys[K_RALT]:
            if keys[K_F4]:
                pygame.quit()
                sys_exit()
        if keys[K_SPACE] and MainButton.key_ready:
            MainButton.isPaused = not MainButton.isPaused
            MainButton.key_ready = False

    def main(self):
        while 1:
            self.Clock.tick(FPS)
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            self.render(
                window=self.window,
                SysButtons=[self.SysButton_0, self.SysButton_1, self.SysButton_2],
                SettingButton=self.SettingButton,
                Numbers=[self.Number_0, self.Number_1, self.Number_2, self.Number_3],
                Colon=self.Colon,
                MainButton=self.MainButton,
                SkipButton=self.SkipButton,
                ConfigClusterInts=[self.ConfigClusterInt_0, self.ConfigClusterInt_1, self.ConfigClusterInt_2, self.ConfigClusterInt_3],
                ConfigClusterBools=[self.ConfigClusterBool_0, self.ConfigClusterBool_1],
                ConfigSaveButton=self.ConfigSaveButton,
                ConfigResetButton=self.ConfigResetButton,
                ConfigAboutButton=self.ConfigAboutButton,
                PPSHandler=self.PPSHandler
            )

            for event in events:
                if event.type == QUIT:
                    pygame.quit()
                    sys_exit()

                self.handle_mouse(
                    window=self.window,
                    event=event,
                    mouse_pos=mouse_pos,
                    SysButtons=[self.SysButton_0, self.SysButton_1, self.SysButton_2],
                    SettingButton=self.SettingButton,
                    MainButton=self.MainButton,
                    SkipButton=self.SkipButton,
                    ConfigClusterInts=[self.ConfigClusterInt_0, self.ConfigClusterInt_1, self.ConfigClusterInt_2, self.ConfigClusterInt_3],
                    ConfigClusterBools=[self.ConfigClusterBool_0, self.ConfigClusterBool_1],
                    ConfigSaveButton=self.ConfigSaveButton,
                    ConfigResetButton=self.ConfigResetButton,
                    ConfigAboutButton=self.ConfigAboutButton,
                    PPSHandler=self.PPSHandler
                )
                pygame.event.clear()

            self.handle_key(pygame.key.get_pressed(), self.MainButton)

            pygame.display.update()

            del events, mouse_pos
            gc_collect()


if __name__ == '__main__':
    pygame.init()
    app = App()
    app.main()