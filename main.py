
import pygame
from pygame.locals import QUIT, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_LALT, K_RALT, K_F4, K_SPACE

from sys import exit as sys_exit
from os import environ
from os.path import join as os_path_join
from gc import collect as gc_collect
from ctypes import windll, WinDLL, wintypes

from random import randint


pygame.font.init()


"""
def color_setup(value):
    if isinstance(value, str):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    elif isinstance(value, tuple):
        return '#%02x%02x%02x' % value

def image_setup(folder: str, path: str) -> pygame.Surface:
    return pygame.image.load(os.path.join(f'{FOLDER}\{folder}', path))

def audio_setup(folder: str, path: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(os.path.join(f'{FOLDER}\{folder}', path))
"""

def font_setup(folder: str, path: str, size: int) -> pygame.font.Font:
    return pygame.font.Font(os_path_join(folder, path), size)


# 'Resources'


WIDTH = 250
HEIGHT = 300


COL_BLACK = (7, 5, 2)   #070502
COL_MOCHA = (56, 42, 29)   #382a1d
COL_CARAMEL = (143, 97, 75)   #8f614b
COL_HEAVYCREAM = (182, 155, 125)   #b69b7d
COL_WHIP = (222, 203, 177)   #decbb1

COL_MAC_RED = (255, 96, 92)   #ff605c | sunset orange
COL_MAC_YELLOW = (255, 189, 68)   #ffbd44 | pastel orange
COL_MAC_GREEN = (0, 202, 78)   #00ca4e | malachite


FONT_NUM = font_setup('Python\Project Pomodoro\Fonts', 'JetBrainsMonoNL-Bold.ttf', 80)
FONT_CHR = font_setup('Python\Project Pomodoro\Fonts', 'RobotoCondensed-Regular.ttf', 15)


MODE = 0   # {0: 'light', 1: 'dark'}
FPS = 30

TOTAL_TIME = 1500


class MoveWindowHandler:
    def __init__(self, start_pos: tuple[int]):
        self.start_pos = start_pos
        self.win_coords = [-i for i in self.start_pos]
        self.isMousePressed = False

    def move_window(self, pos: tuple[int]):
        # handle to window
        hwnd = pygame.display.get_wm_info()['window']

        # user32.MoveWindow receives new size for window
        width, height = pygame.display.get_surface().get_size()
        windll.user32.MoveWindow(hwnd, -pos[0], -pos[1], width, height, False)
        del hwnd, width, height

    def onToggle(self, event: pygame.event.Event, mouse_pos: tuple[int]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.isMousePressed = True
            self.start_pos = pygame.mouse.get_pos()
        
        elif event.type == MOUSEMOTION:
            if self.isMousePressed:
                if mouse_pos[1] < pygame.display.get_window_size()[1]*0.2:
                    new_pos = pygame.mouse.get_pos()
                    self.win_coords[0] += self.start_pos[0] - new_pos[0]
                    self.win_coords[1] += self.start_pos[1] - new_pos[1]
                    self.move_window(self.win_coords)
        
        elif event.type == MOUSEBUTTONUP:
            self.isMousePressed = False


class Menu:   # directly reads & modifies config.ini (pending)
    def __init__(self):
        self.font_num = FONT_NUM
        self.font_alp = FONT_CHR

        self.display_str_1 = '2'
        self.display_str_2 = '5'
        self.display_str_banner = 'Dark mode: ON'

        self.menuSurf = pygame.Surface((250, 200))
        self.menuSurf.fill(COL_HEAVYCREAM)

        self.btn_changeWork = pygame.Surface((30, 30))
        self.btn_changeWork.fill(COL_MAC_RED)

        self.btn_changeShortBreak = pygame.Surface((30, 30))
        self.btn_changeShortBreak.fill(COL_MAC_YELLOW)

        self.btn_changeLongBreak = pygame.Surface((30, 30))
        self.btn_changeLongBreak.fill(COL_MAC_GREEN)

        self.btn_changeInterval = pygame.Surface((30, 30))
        self.btn_changeInterval.fill(COL_MOCHA)

        self.btn_toggleAutoStart = pygame.Surface((30, 30))
        self.btn_toggleAutoStart.fill(COL_MOCHA)

        self.btn_toggleBGM = pygame.Surface((30, 30))
        self.btn_toggleBGM.fill(COL_MOCHA)

        self.btn_toggleDarkMode = pygame.Surface((30, 30))
        self.btn_toggleDarkMode.fill(COL_MOCHA)

        self.btn_resetToDefault = pygame.Surface((30, 30))
        self.btn_resetToDefault.fill(COL_MOCHA)
        
        self.displaySlot_num_1 = self.font_num.render(self.display_str_1, True, COL_WHIP)
        self.displaySlot_num_1_rect = self.displaySlot_num_1.get_rect(center=(60, 100))

        self.displaySlot_num_2 = self.font_num.render(self.display_str_2, True, COL_WHIP)
        self.displaySlot_num_2_rect = self.displaySlot_num_2.get_rect(center=(110, 100))

        self.displaySlot_banner = self.font_alp.render(self.display_str_banner, True, COL_WHIP)
        self.displaySlot_banner_rect = self.displaySlot_banner.get_rect(center=(85, 40))

        self.toggleBar = None   # ToggleBar(...)

        self.menuSurf.blit(self.btn_changeWork, (155, 25))
        self.menuSurf.blit(self.btn_changeShortBreak, (155, 65))
        self.menuSurf.blit(self.btn_changeLongBreak, (155, 105))
        self.menuSurf.blit(self.btn_changeInterval, (155, 145))
        self.menuSurf.blit(self.btn_toggleAutoStart, (195, 25))
        self.menuSurf.blit(self.btn_toggleBGM, (195, 65))
        self.menuSurf.blit(self.btn_toggleDarkMode, (195, 105))
        self.menuSurf.blit(self.btn_resetToDefault, (195, 145))
        del self.btn_changeWork, self.btn_changeShortBreak, self.btn_changeLongBreak, self.btn_changeInterval, self.btn_toggleAutoStart, self.btn_toggleBGM, self.btn_toggleDarkMode, self.btn_resetToDefault

        self.menuSurf.blit(self.displaySlot_num_1, self.displaySlot_num_1_rect)
        self.menuSurf.blit(self.displaySlot_num_2, self.displaySlot_num_2_rect)
        self.menuSurf.blit(self.displaySlot_banner, self.displaySlot_banner_rect)
        del self.displaySlot_num_1, self.displaySlot_num_1_rect, self.displaySlot_num_2, self.displaySlot_num_2_rect, self.displaySlot_banner, self.displaySlot_banner_rect

    def render(self):
        return self.menuSurf
        

class ToggleBar:
    def __init__(self):
        ...

    def render(self, window: pygame.Surface):
        return ...


class SysButton:
    def __init__(self, pos: tuple[int], size: int, col: tuple[int], slot: int):
        self.pos = pos
        self.size = (size, size)
        self.col = col
        self.slot = slot   # [0, 1, 2]

        self.pgb_width = 0
        self.pgb_progress = 1
    
    def minimize_window(self):
        user32 = WinDLL('user32')   # some unnecessary setups
        user32.GetForegroundWindow.argtypes = ()
        user32.GetForegroundWindow.restype = wintypes.HWND
        user32.ShowWindow.argtypes = wintypes.HWND, wintypes.BOOL
        user32.ShowWindow.restype = wintypes.BOOL

        hwnd = user32.GetForegroundWindow()
        user32.ShowWindow(hwnd, 6)   # SW_MAXIMIZE = 3, SW_MINIMIZE = 6

        del user32, hwnd

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
            self.minimize_window()
        else:
            print('Green SysButton toggled.')


class SettingButton:
    def __init__(self, pos: tuple[int]):
        self.pos = pos
        self.img = pygame.Surface((27, 27), pygame.SRCALPHA).convert_alpha()

        # need adjustment
        rectvalues = ((0, 3, 15, 3), (21, 3, 6, 3), (0, 12, 6, 3), (12, 12, 15, 3), (0, 21, 9, 3), (15, 21, 12, 3), (18, 0, 3, 9), (6, 9, 3, 9), (12, 18, 3, 9))
        for rectvalue in rectvalues:
            pygame.draw.rect(self.img, COL_MOCHA, rectvalue)
        del rectvalues

        self.fadeSurf = pygame.Surface((WIDTH, HEIGHT))
        self.fadeSurf.fill(COL_BLACK)

        self.progress = 0

        self.menuSurf = Menu().render()

        self.isToggled = False

    def render(self, window: pygame.Surface) -> pygame.Rect:
        return window.blit(self.img, self.pos)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if not self.isToggled:
                if self.render(window).collidepoint(mouse_pos):
                    self.isToggled = True
            else:
                if mouse_pos[1] < 100:
                    self.isToggled = False

    def onToggle(self, window: pygame.Surface, status: bool):
        window.blit(self.menuSurf, (0, 300-self.progress))

        self.fadeSurf.set_alpha(self.progress//2)
        window.blit(self.fadeSurf, (0, 0))

        if status:
            if self.progress < 200:
                self.progress += 20
        else:
            if self.progress > 0:
                self.progress -= 20

    
class Number:
    def __init__(self, pos: tuple[int], slot: int):
        self.pos = pos
        self.slot = slot   # [0, 1, 2, 3]

        self.font = FONT_NUM

    def num_to_display(self, current_time: float) -> str:
        minute, second = divmod(int(current_time), 60)
        return f'{minute:02d}{second:02d}'[self.slot]

    def render(self, window: pygame.Surface, current_time: int):
        text = self.font.render(self.num_to_display(current_time), True, COL_MOCHA).convert_alpha()
        text_rect = text.get_rect(center=(self.pos[0]+20, self.pos[1]+45))
        window.blit(text, text_rect)
        del text, text_rect


class Colon:
    def __init__(self):
        self.font = FONT_NUM

    def render(self, window: pygame.Surface):
        text = self.font.render(':', True, COL_MOCHA).convert_alpha()
        text_rect = text.get_rect(center=([i//2 for i in pygame.display.get_window_size()]))
        window.blit(text, text_rect)
        del text, text_rect


class MainButton:
    def __init__(self, pos: tuple[int]):
        self.pos = pos

        self.img_play = pygame.Surface((35, 35), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.img_play, COL_MOCHA, (3.5, 0, 10, 35))
        pygame.draw.rect(self.img_play, COL_MOCHA, (21.5, 0, 10, 35))

        self.img_pause = pygame.Surface((35, 35), pygame.SRCALPHA).convert_alpha()
        pygame.draw.polygon(self.img_pause, COL_MOCHA, ((3.5, 0), (31.5, 17.5), (3.5, 35)))

        pygame.time.set_timer(pygame.USEREVENT, 1000)

        self.isPaused = True

        self.progress = 0

        self.current_time = 0

    def render(self, window: pygame.Surface):
        if not self.isPaused:
            return window.blit(self.img_play, self.pos)
        return window.blit(self.img_pause, self.pos)

    def isMouseOn(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int]):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.render(window).collidepoint(mouse_pos):
                self.isPaused = not self.isPaused

    def onToggle(self, event: pygame.event.Event):
        if event.type == pygame.USEREVENT:
            if not self.isPaused and self.current_time > 0:
                self.current_time -= 1


class SkipButton:
    def __init__(self, pos: tuple[int]):
        self.pos = pos
        self.img = ...

    def render(self):
        ...
    
    def isMouseOn(self):
        ...

    def onToggle(self):
        ...


class StatsButton:
    def __init__(self, pos: tuple[int]):
        self.pos = pos
        self.img = ...

    def render(self):
        ...

    def isMouseOn(self):
        ...

    def onToggle(self):
        ...


class App:
    def __init__(self):
        self.place_pos = (pygame.display.get_desktop_sizes()[0][0]-300, 50)   # 50px from top right corner
        environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % self.place_pos
        pygame.display.set_caption('focus()')

        self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

        self.MoveWindowHandler = MoveWindowHandler(self.place_pos)
        del self.place_pos

        self.isMenuToggled = False

        self.SysButton_0 = SysButton((25, 25), 10, COL_MAC_RED, 0)
        self.SysButton_1 = SysButton((40, 25), 10, COL_MAC_YELLOW, 1)
        self.SysButton_2 = SysButton((55, 25), 10, COL_MAC_GREEN, 2)

        self.SettingButton = SettingButton((198, 25))

        self.Number_0 = Number((25, 110), 0)
        self.Number_1 = Number((67.5, 110), 1)
        self.Number_2 = Number((142.5, 110), 2)
        self.Number_3 = Number((185, 110), 3)

        self.Colon = Colon()

        self.MainButton = MainButton((107.5, 240))
        self.MainButton.current_time = TOTAL_TIME

        self.FPS_clock = pygame.time.Clock()

    def render(self, window: pygame.Surface, SysButtons: list[SysButton], SettingButton: SettingButton, Numbers: list[Number], Colon: Colon, MainButton: MainButton):
        self.isMenuToggled = self.SettingButton.isToggled
        window.fill(COL_WHIP)
        pygame.draw.polygon(window, COL_HEAVYCREAM, ((0, 0), (0, 60), (90, 60), (150, 0)))
        
        if self.isMenuToggled:
            SettingButton.onToggle(window, True)

        else:
            SettingButton.onToggle(window, False)

            for Number in Numbers:
                Number.render(window, MainButton.current_time)

            Colon.render(window)

            MainButton.render(window)

        for SysButton in SysButtons:
            SysButton.render(window)

        SettingButton.render(window)

    def handle_mouse(self, window: pygame.Surface, event: pygame.event.Event, mouse_pos: tuple[int], SysButtons: list[SysButton], SettingButton: SettingButton, MainButton: MainButton):
        if pygame.mouse.get_focused():

            SettingButton.isMouseOn(window, event, mouse_pos)

            MainButton.isMouseOn(window, event, mouse_pos)

            if not self.isMenuToggled:

                self.MoveWindowHandler.onToggle(event, mouse_pos)

                for SysButton in SysButtons:
                    if SysButton.isMouseOn(window, event, mouse_pos):
                        SysButton.onToggle()
        
        MainButton.onToggle(event)

    def handle_key(self, keys: any, MainButton: MainButton):
        if keys[K_LALT] or keys[K_RALT]:
            if keys[K_F4]:
                pygame.quit()
                sys_exit()
        if keys[K_SPACE]:
            MainButton.isPaused = not MainButton.isPaused

        # space for mainbutton

    def main(self):
        self.MoveWindowHandler.move_window(self.MoveWindowHandler.win_coords)

        while 1:
            self.FPS_clock.tick(FPS)

            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            self.render(self.window, [self.SysButton_0, self.SysButton_1, self.SysButton_2], self.SettingButton, [self.Number_0, self.Number_1, self.Number_2, self.Number_3], self.Colon, self.MainButton)

            for event in events:
                if event.type == QUIT:
                    pygame.quit()
                    sys_exit()

                self.handle_mouse(self.window, event, mouse_pos, [self.SysButton_0, self.SysButton_1, self.SysButton_2], self.SettingButton, self.MainButton)
                pygame.event.clear()

            self.handle_key(pygame.key.get_pressed(), self.MainButton)

            pygame.display.update()

            del events, mouse_pos
            gc_collect()


if __name__ == '__main__':
    pygame.init()
    #pygame.mixer.init()
    app = App()
    app.main()

"""
main features:
- Pomodoro timer (25 min - work, 5 min - short break, 20 min - long break)
- Change default configurations (time length)
- Add-ons: SOUND on/off, DARK MODE on/off
- Task list
"""

"""
CREDIT:
- ICON: https://www.flaticon.com/authors/google
- COLOR PALETTE - LATTE: https://images.squarespace-cdn.com/content/v1/59d296dc6f4ca35b8e07d4f8/1522427986525-RLR682SPN3YUPG8ET2HP/15+Color+Palettes-06.png?format=750w
- COLOR CHANGER: https://pinetools.com/colorize-image
- FONT: https://www.jetbrains.com/lp/mono/#font-family
https://www.deviantart.com/gasara/art/Medianoid-Pixel-Font-371029921
"""