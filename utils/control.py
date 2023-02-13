
import socket

from win32gui import SetWindowLong, GetWindowLong, SetLayeredWindowAttributes, SetWindowPos, EnableWindow
from win32con import GWL_EXSTYLE, WS_EX_LAYERED, LWA_COLORKEY
from win32api import RGB

from utils import *


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

    def __init__(self, configFile: ConfigParser) -> None:
        self.configFile = configFile
        self.displayWindowPosition = (pygame.display.get_desktop_sizes()[0][0]-310, 50)   # 50 px from top right corner

    def resetConfigFileToDefault(self) -> None:   # called if config.ini is messed up

        try:

            self.configFile.read(CONFIG_PATH)

        except:
            
            self.configFile.clear()

            self.configFile.add_section("numberValues")
            for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:4]:
                self.configFile.set("timeValues", configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])
            
            self.configFile.add_section("boolValues")
            for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[4:6]:
                self.configFile.set("boolValues", configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])

        else:

            for configFileSection in ("timeValues", "boolValues"):
                if not self.configFile.has_section(configFileSection):
                    self.configFile.add_section(configFileSection)

            for configFileSection in self.configFile.sections():

                if configFileSection == "timeValues":

                    for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:4]:
                        if not self.configFile.has_option(configFileSection, configFileOption):
                            self.configFile.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])

                    for (configFileOption, configFileValue) in self.configFile.items(configFileSection):
                        if configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:3]:
                            if any((not configFileValue.isnumeric(), int(configFileValue) < 60, int(configFileValue) > 5940)):
                                self.configFile.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])
                        elif configFileOption == tuple(CONFIG_DEFAULT_VALUES.keys())[3]:
                            if any((not configFileValue.isnumeric(), int(configFileValue) < 1, int(configFileValue) > 99)):
                                self.configFile.set(configFileSection, configFileValue, CONFIG_DEFAULT_VALUES[configFileOption])
                        else:
                            self.configFile.remove_option(configFileSection, configFileOption)

                elif configFileSection == "boolValues":

                    for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[4:6]:
                        if not self.configFile.has_option(configFileSection, configFileOption):
                            self.configFile.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])

                    for (configFileOption, configFileValue) in self.configFile.items(configFileSection):
                        if configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[4:6]:
                            if any((not configFileValue.isnumeric(), configFileValue not in ("0", "1"))):
                                self.configFile.set(configFileSection, configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])
                        else:
                            self.configFile.remove_option(configFileSection, configFileOption)
                
                else:

                    self.configFile.remove_section(configFileSection)

        finally:

            with open(CONFIG_PATH, "w") as modifiedConfigFile:
                self.configFile.write(modifiedConfigFile)

        global configFileValueTimeLengths, configFileValueInterval, configFileValueIsAutoSwitchOn, configFileValueIsSoundOn

        configFileValueTimeLengths = [self.configFile.getint("timeValues", configFileOption) for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:3]]
        configFileValueInterval = self.configFile.getint("timeValues", tuple(CONFIG_DEFAULT_VALUES.keys())[3])
        configFileValueIsAutoSwitchOn = self.configFile.getboolean("boolValues", tuple(CONFIG_DEFAULT_VALUES.keys())[4])
        configFileValueIsSoundOn = self.configFile.getboolean("boolValues", tuple(CONFIG_DEFAULT_VALUES.keys())[5])

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

    def createTwoDisplayWindows(self, displayWindowDeviation: int, transparentColorRGBValue: tuple[int, int, int]) -> tuple[pygame.Surface, pygame.Surface]:

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
        DefaultTimeTracker: pygame.time.Clock,
        displayWindowDeviation: int,   # 10
        transparentColorRGBValue: tuple[int, int, int]   # (0, 0, 0)
    ) -> None:   # create instances? no, that's done in main.py
        
        pygame.font.init()
        pygame.init()

        self.ControlTimerFunctions = ControlTimerFunctions
        self.ControlOtherFunctions =  ControlOtherFunctions
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
        self.DefaultTimeTracker = DefaultTimeTracker
        
        self.displayWindowMaster, self.displayWindowMain = self.ControlOtherFunctions.createTwoDisplayWindows(displayWindowDeviation, transparentColorRGBValue)

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

                for SecondSideSprite in self.SecondSideDisplayBlockNumbers:
                    SecondSideSprite.resetChangesIfNotSaved()

            


    def masterControlKeyboardInputs(self) -> None:
        ...

    def masterControlRuntime(self) -> None:
        ...