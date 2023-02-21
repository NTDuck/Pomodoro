
import gc

from win32gui import SetWindowLong, GetWindowLong, SetLayeredWindowAttributes, SetWindowPos
from win32con import GWL_EXSTYLE, WS_EX_LAYERED, LWA_COLORKEY
from win32api import RGB

from pygame.locals import QUIT

from utils.utils import *


class ControlTimerFunctions:

    def __init__(self) -> None:

        self.currentTotalSeconds = configFileValueTimeLengths[0]
        self.trackerPreviousMode = 0   # 0: "work" | 1: "shortBreak"
        self.trackerInterval = 0

        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def switchMode(self) -> None:
        
        if self.trackerInterval == configFileValueInterval:
            
            self.currentTotalSeconds = configFileValueTimeLengths[2]
            self.trackerInterval = 0

        else:
            
            self.trackerPreviousMode ^= True
            self.currentTotalSeconds = configFileValueTimeLengths[self.trackerPreviousMode]
            if self.trackerPreviousMode == 1:
                self.trackerInterval += 1

    def masterControlTimerFunctions(self, event: pygame.event.Event, FirstSidePlayPauseButton: FirstSidePlayPauseButton, FirstSideSkipButton: FirstSideSkipButton) -> None:

        if event.type == pygame.USEREVENT:

            if not FirstSidePlayPauseButton.isKeyReady:
                FirstSidePlayPauseButton.isKeyReady = True
            
            if not FirstSidePlayPauseButton.isOnPause:

                if self.currentTotalSeconds > 0:
                    self.currentTotalSeconds -= 1
                else:
                    if not configFileValueIsAutoSwitchOn:
                        FirstSidePlayPauseButton.isOnPause = True
                    self.switchMode()
        
        if FirstSideSkipButton.isPressed:

            FirstSideSkipButton.isPressed = False
            FirstSidePlayPauseButton.isOnPause = True
            self.switchMode()


class ControlOtherFunctions:

    def __init__(self) -> None:
        self.displayWindowPosition = (pygame.display.get_desktop_sizes()[0][0] - 310, 50)   # 50 px from top right corner

    @staticmethod
    def initializeImportedPygameModules() -> None:
        ...

    def resetConfigFileToDefault(self) -> None:   # called if config.ini is messed up | UPDATE 02/21/22: function not called, don't know why

        try:

            CONFIGPARSER.read(CONFIG_PATH)

        except:
            
            CONFIGPARSER.clear()

            CONFIGPARSER.add_section("numberValues")
            for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:4]:
                CONFIGPARSER.set("numberValues", configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])
            
            CONFIGPARSER.add_section("boolValues")
            for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[4:6]:
                CONFIGPARSER.set("boolValues", configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])

        else:

            for configFileSection in ("numberValues", "boolValues"):
                if not CONFIGPARSER.has_section(configFileSection):
                    CONFIGPARSER.add_section(configFileSection)

            for configFileSection in CONFIGPARSER.sections():

                if configFileSection == "numberValues":

                    for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:4]:
                        if not CONFIGPARSER.has_option(configFileSection, configFileOption):
                            CONFIGPARSER.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])

                    for (configFileOption, configFileValue) in CONFIGPARSER.items(configFileSection):
                        if configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:3]:
                            if any((not configFileValue.isnumeric(), int(configFileValue) < 60, int(configFileValue) > 5940)):
                                CONFIGPARSER.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])
                        elif configFileOption == tuple(CONFIG_DEFAULT_VALUES.keys())[3]:
                            if any((not configFileValue.isnumeric(), int(configFileValue) < 1, int(configFileValue) > 99)):
                                CONFIGPARSER.set(configFileSection, configFileValue, CONFIG_DEFAULT_VALUES[configFileOption])
                        else:
                            CONFIGPARSER.remove_option(configFileSection, configFileOption)

                elif configFileSection == "boolValues":

                    for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[4:6]:
                        if not CONFIGPARSER.has_option(configFileSection, configFileOption):
                            CONFIGPARSER.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])

                    for (configFileOption, configFileValue) in CONFIGPARSER.items(configFileSection):
                        if configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[4:6]:
                            if any((not configFileValue.isnumeric(), configFileValue not in ("0", "1"))):
                                CONFIGPARSER.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])
                        else:
                            CONFIGPARSER.remove_option(configFileSection, configFileOption)
                
                else:

                    CONFIGPARSER.remove_section(configFileSection)

        finally:

            with open(CONFIG_PATH, "w") as modifiedConfigFile:
                CONFIGPARSER.write(modifiedConfigFile)

        print("Config rewritten")

        global configFileValueTimeLengths, configFileValueInterval, configFileValueIsAutoSwitchOn, configFileValueIsSoundOn

        configFileValueTimeLengths = [CONFIGPARSER.getint("numberValues", configFileOption) for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:3]]
        configFileValueInterval = CONFIGPARSER.getint("numberValues", tuple(CONFIG_DEFAULT_VALUES.keys())[3])
        configFileValueIsAutoSwitchOn = CONFIGPARSER.getboolean("boolValues", tuple(CONFIG_DEFAULT_VALUES.keys())[4])
        configFileValueIsSoundOn = CONFIGPARSER.getboolean("boolValues", tuple(CONFIG_DEFAULT_VALUES.keys())[5])

        print("values saved to global (manual)")

        print(configFileValueTimeLengths, configFileValueInterval, configFileValueIsAutoSwitchOn, configFileValueIsSoundOn)

    def setDisplayWindowPosition(self) -> None:
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % self.displayWindowPosition

    def makeDisplayWindowTransparent(self, displayWindow: pygame.Surface, colorRGBValue: tuple[int, int, int]) -> pygame.Rect:

        handleToDisplayWindow = pygame.display.get_wm_info()["window"]
        SetWindowLong(handleToDisplayWindow, GWL_EXSTYLE, GetWindowLong(handleToDisplayWindow, GWL_EXSTYLE) | WS_EX_LAYERED)
        SetLayeredWindowAttributes(handleToDisplayWindow, RGB(*colorRGBValue), 0, LWA_COLORKEY)

        return displayWindow.fill(colorRGBValue)

    def makeDisplayWindowAlwaysOnTop(self) -> None:
        return SetWindowPos(pygame.display.get_wm_info()["window"], -1, self.displayWindowPosition[0], self.displayWindowPosition[1], 0, 0, 1)

    def createDesktopIcon(self, colorRGBValue: tuple[int, int, int]) -> None:

        displayIcon = pygame.Surface((32, 32), pygame.SRCALPHA)
        for _rectValue in [_pointPosition + (8, 8) for _pointPosition in ((0, 0), (12, 0), (24, 0), (0, 12), (12, 12), (24, 12), (0, 24), (12, 24), (24, 24))]:
            pygame.draw.rect(displayIcon, colorRGBValue, _rectValue)

        pygame.display.set_icon(displayIcon)

    def setDisplayWindowCaption(self, displayWindowCaption: str) -> None:
        return pygame.display.set_caption(displayWindowCaption)

    def createTwoDisplayWindows(self, displayWindowDeviation: int, displayWindowCaption: str, iconColorRGBValue: tuple[int, int, int], transparentColorRGBValue: tuple[int, int, int]) -> tuple[pygame.Surface, pygame.Surface]:

        print("function createTwoDisplayWindows called")

        self.resetConfigFileToDefault()
        self.setDisplayWindowPosition()
        self.createDesktopIcon(iconColorRGBValue)
        self.setDisplayWindowCaption(displayWindowCaption)

        displayWindowMaster = pygame.display.set_mode([displayWindowDimension + displayWindowDeviation for displayWindowDimension in (WIDTH, HEIGHT)], pygame.NOFRAME)
        displayWindowMain = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        displayWindowDecoy = pygame.Surface((WIDTH, HEIGHT)).convert()

        self.makeDisplayWindowTransparent(displayWindowMaster, transparentColorRGBValue)
        self.makeDisplayWindowAlwaysOnTop()

        displayWindowDecoy.fill(COLOR_SECONDARY)
        displayWindowMaster.blit(displayWindowDecoy, (displayWindowDeviation, displayWindowDeviation))

        return (displayWindowMaster, displayWindowMain)


class ControlMainFunctions:

    def __init__(self,
        ControlTimerFunctions: ControlTimerFunctions,
        ControlOtherFunctions: ControlOtherFunctions,
        FirstSideSystemButtons: tuple[FirstSideSystemButton],
        BothSideSettingsButton: BothSideSettingsButton,
        FirstSideDisplayNumbers: tuple[FirstSideDisplayNumber],
        FirstSideDisplayColon: FirstSideDisplayColon,
        FirstSidePlayPauseButton: FirstSidePlayPauseButton,
        FirstSideSkipButton: FirstSideSkipButton,
        SecondSideDisplayBlockNumbers: tuple[SecondSideDisplayBlockNumber],
        SecondSideDisplayBlockBools: tuple[SecondSideDisplayBlockBool],
        SecondSideSaveButton: SecondSideSaveButton,
        SecondSideResetButton: SecondSideResetButton,
        SecondSideAboutButton: SecondSideAboutButton,
        DaemonGlobal: pygame.time.Clock,
        displayWindowDeviation: int,   # 10
        displayWindowCaption: str,
        iconColorRGBValue: tuple[int, int, int],
        transparentColorRGBValue: tuple[int, int, int]   # (0, 0, 0)
    ) -> None:   # create instances? no, that's done in main.py

        self.ControlOtherFunctions = ControlOtherFunctions
        
        self.displayWindowMaster, self.displayWindowMain = self.ControlOtherFunctions.createTwoDisplayWindows(displayWindowDeviation, displayWindowCaption, iconColorRGBValue, transparentColorRGBValue)

        self.ControlTimerFunctions = ControlTimerFunctions
        self.FirstSideSystemButtons = FirstSideSystemButtons
        self.BothSideSettingButton = BothSideSettingsButton
        self.FirstSideDisplayNumbers = FirstSideDisplayNumbers
        self.FirstSideDisplayColon = FirstSideDisplayColon
        self.FirstSidePlayPauseButton = FirstSidePlayPauseButton
        self.FirstSideSkipButton = FirstSideSkipButton
        self.SecondSideDisplayBlockNumbers = SecondSideDisplayBlockNumbers
        self.SecondSideDisplayBlockBools = SecondSideDisplayBlockBools
        self.SecondSideSaveButton = SecondSideSaveButton
        self.SecondSideResetButton = SecondSideResetButton
        self.SecondSideAboutButton = SecondSideAboutButton
        self.DaemonGlobal = DaemonGlobal

    def masterRender(self, displayWindow: pygame.Surface) -> None:
        
        displayWindow.fill(COLOR_BACKGROUND)
        gfxdraw.aapolygon(displayWindow, ((0, 0), (150, 0), (90, 60), (0, 60)), COLOR_SECONDARY)
        gfxdraw.filled_polygon(displayWindow, ((0, 0), (150, 0), (90, 60), (0, 60)), COLOR_SECONDARY)

        for FirstSideSystemButton in self.FirstSideSystemButtons:
            FirstSideSystemButton.render(displayWindow)

        if self.BothSideSettingButton.isOnFirstSide:

            for FirstSideDisplayNumber in self.FirstSideDisplayNumbers:
                FirstSideDisplayNumber.render(displayWindow, self.ControlTimerFunctions.currentTotalSeconds)
            
            for FirstSideSprite in (self.FirstSideDisplayColon, self.FirstSidePlayPauseButton, self.FirstSideSkipButton):
                FirstSideSprite.render(displayWindow)

        else:

            for SecondDisplayBlockNumber in self.SecondSideDisplayBlockNumbers:
                SecondDisplayBlockNumber.render(displayWindow)

            for SecondDisplayBlockBool in self.SecondSideDisplayBlockBools:
                SecondDisplayBlockBool.render(displayWindow)

            for SecondSideSprite in (self.SecondSideSaveButton, self.SecondSideResetButton, self.SecondSideAboutButton):
                SecondSideSprite.render(displayWindow)

        self.displayWindowMaster.blit(self.displayWindowMain, (0, 0))

    def masterControlMouse(self, displayWindow: pygame.surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        
        self.ControlTimerFunctions.masterControlTimerFunctions(event, self.FirstSidePlayPauseButton, self.FirstSideSkipButton)

        if pygame.mouse.get_focused():
            
            self.BothSideSettingButton.isMouseRightClicked(self.displayWindowMain, event, currentMousePosition)

            for FirstSideSystemButton in self.FirstSideSystemButtons:
                if FirstSideSystemButton.isMouseOn(displayWindow, event, currentMousePosition):
                    FirstSideSystemButton.onToggle()

            if self.BothSideSettingButton.isOnFirstSide:

                for FirstSideSprite in (self.FirstSidePlayPauseButton, self.BothSideSettingButton):
                    FirstSideSprite.isMouseRightClicked(displayWindow, event, currentMousePosition)

                for SecondSideDisplayBlockNumber in self.SecondSideDisplayBlockNumbers:
                    SecondSideDisplayBlockNumber.resetChangesIfNotSaved()

                for SecondSideDisplayBlockBool in self.SecondSideDisplayBlockBools:
                    SecondSideDisplayBlockBool.resetChangesIfNotSaved()

            else:
                
                for SecondSideDisplayBlockNumber in self.SecondSideDisplayBlockNumbers:
                    SecondSideDisplayBlockNumber.isMouseRightClicked(displayWindow, event, currentMousePosition)

                for SecondSideDisplayBlockBool in self.SecondSideDisplayBlockBools:
                    SecondSideDisplayBlockBool.isMouseRightClicked(displayWindow, event, currentMousePosition)

                for SecondSideSprite in (self.SecondSideSaveButton, self.SecondSideResetButton):
                    SecondSideSprite.isMouseRightClicked(displayWindow, event, currentMousePosition, self.SecondSideDisplayBlockNumbers, self.SecondSideDisplayBlockBools)
                
                self.SecondSideAboutButton.isMouseRightClicked(displayWindow, event, currentMousePosition)

    def masterControlKeyboardInputs(self, eventKey: pygame.key.ScancodeWrapper) -> None:
        
        if all((eventKey, self.FirstSidePlayPauseButton.isKeyReady)):

            for boolValue in (self.FirstSidePlayPauseButton.isOnPause, self.FirstSidePlayPauseButton.isKeyReady):
                boolValue ^= True

    def masterControlRuntime(self) -> None:
        
        while 1:   # used instead of `True`
            
            self.DaemonGlobal.tick(FPS)
            events = pygame.event.get()
            currentMousePosition = pygame.mouse.get_pos()

            self.masterRender(self.displayWindowMain)

            for event in events:

                if event.type == QUIT:

                    pygame.quit()
                    sys.exit()

                self.masterControlMouse(self.displayWindowMain, event, currentMousePosition)
        
            pygame.event.clear()   # originally in for loop
        
            self.masterControlKeyboardInputs(pygame.key.get_pressed())

            pygame.display.update()

            gc.collect()