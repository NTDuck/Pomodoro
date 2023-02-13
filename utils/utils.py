
import sys, webbrowser
import pygame

from configparser import ConfigParser

from pygame import gfxdraw
from pygame.locals import MOUSEBUTTONDOWN

from globals import *


class Config:
    def __init__(self) -> None:
        ...


class FirstSideSystemButton:

    def __init__(self, spritePosition: tuple[int, int], spriteOrder: int, colorRGBValue: tuple[int, int, int]) -> None:
        self.spritePosition = spritePosition
        self.spriteOrder = spriteOrder   # (0, 1, 2)
        self.colorRGBValue = colorRGBValue

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        return pygame.draw.rect(displayWindow, self.colorRGBValue, self.spritePosition + (10, 10))

    def isMouseOn(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1)):
            return self.render(displayWindow).collidepoint(currentMousePosition)

            # do not return bool, modify self bool instead

    def onToggle(self) -> None:
        if self.spriteOrder == 0:
            pygame.quit()
            sys.exit()
        elif self.spriteOrder == 1:
            pygame.display.iconify()
        else:
            pygame.display.iconify()


class BothSideSettingsButton:

    def __init__(self, spritePosition: tuple[int, int], colorRGBValue: tuple[int, int, int]) -> None:
        self.spritePosition = spritePosition
        self.colorRGBValue = colorRGBValue

        self.displayImageFirstSide = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()

        rectValues = [_pointPosition + (8, 8) for _pointPosition in ((0, 0), (12, 0), (24, 0), (0, 12), (12, 12), (24, 12), (0, 24), (12, 24), (24, 24))]
        for _rectValue in rectValues:
            pygame.draw.rect(self.displayImageFirstSide, self.colorRGBValue, _rectValue)

        self.displayImageSecondSide = pygame.Surface((31.5, 31.5), pygame.SRCALPHA).convert_alpha()

        rectValues = [_pointPosition + (17.5, 3.5) for _pointPosition in ((0, 3.5), (14, 14), (14, 24.5))] + [_pointPosition + (10.5, 3.5) for _pointPosition in ((21, 3.5), (0, 14), (0, 24.5))] + [_pointPosition + (3.5, 10.5) for _pointPosition in ((21, 0), (7, 10.5), (14, 21))]
        for _rectValue in rectValues:
            pygame.draw.rect(self.displayImageSecondSide, self.colorRGBValue, _rectValue)
        del rectValues

        self.isOnFirstSide = True

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        return displayWindow.blit(self.displayImageFirstSide, self.spritePosition) if self.isOnFirstSide else displayWindow.blit(self.displayImageSecondSide, self.spritePosition[0] + 0.5, self.spritePosition[1])

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):
            self.isOnFirstSide ^= True


class FirstSideDisplayNumber:

    def __init__(self, spritePosition: tuple[int, int], spriteSize: int, spriteOrder: int, colorRGBValue: tuple[int, int, int], FONT_PATH: str) -> None:
        self.spritePosition = spritePosition
        self.spriteOrder = spriteOrder
        self.colorRGBValue = colorRGBValue
        self.font = pygame.font.Font(FONT_PATH, spriteSize)   # 80

    def render(self, displayWindow: pygame.Surface, currentTotalSeconds: int) -> pygame.Rect:
        convertTo4DigitString = lambda currentTotalSeconds: f"{currentTotalSeconds // 60:02d}{currentTotalSeconds % 60:02d}"[self.spriteOrder]
        displayText = self.font.render(convertTo4DigitString(currentTotalSeconds), True, self.colorRGBValue).convert_alpha()
        displayTextRect = displayText.get_rect(center = self.spritePosition)
        return displayWindow.blit(displayText, displayTextRect)


class FirstSideDisplayColon:

    def __init__(self, spritePosition: tuple[int, int], spriteSize: int, colorRGBValue: tuple[int, int, int], FONT_PATH: str) -> None:
        self.spritePosition = spritePosition
        self.colorRGBValue = colorRGBValue
        self.font = pygame.font.Font(FONT_PATH, spriteSize)   # 80

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        displayText = self.font.render(":", True, self.colorRGBValue).convert_alpha()
        displayTextRect = displayText.get_rect(center=self.spritePosition)
        return displayWindow.blit(displayText, displayTextRect)


class FirstSidePlayPauseButton:

    def __init__(self, spritePosition: tuple[int, int], colorRGBValue: tuple[int, int, int]) -> None:
        self.spritePosition = spritePosition
        self.colorRGBValue = colorRGBValue

        self.displayImagePlay = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        for _rectValue in ((2, 0, 9.5, 32), (20.5, 0, 9.5, 32)):
            pygame.draw.rect(self.displayImagePlay, self.colorRGBValue, _rectValue)
        
        self.displayImagePause = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        gfxdraw.aapolygon(self.displayImagePause, ((3, 0), (29, 16), (3, 32)), self.colorRGBValue)
        gfxdraw.filled_polygon(self.displayImagePause, ((3, 0), (29, 16), (3, 32)), self.colorRGBValue)

        self.isOnPause = True   # True: Paused, False: Playing
        self.isKeyReady = False   # track

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        return displayWindow.blit(self.displayImagePlay, self.spritePosition) if self.isOnPause else displayWindow.blit(self.displayImagePause, self.spritePosition)


    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):
            self.isOnPause ^= True


class FirstSideSkipButton:

    def __init__(self, spritePosition: tuple[int, int], colorRGBValue: tuple[int, int, int]) -> None:
        self.spritePosition = spritePosition
        self.colorRGBValue = colorRGBValue

        self.displayImage = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        gfxdraw.aapolygon(self.displayImage, ((0, 0), (22.5, 16), (0, 32)), self.colorRGBValue)
        gfxdraw.filled_polygon(self.displayImage, ((0, 0), (22.5, 16), (0, 32)), self.colorRGBValue)
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (26.5, 0, 5.5, 32))

        self.isPressed = False

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        return displayWindow.blit(self.displayImage, self.spritePosition)

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):
            self.isPressed = True


class SecondSideDisplayNumber:

    def __init__(self, spritePosition: tuple[int, int], spriteSize: int, spriteValue: int, colorRGBValue: tuple[int, int, int], FONT_PATH: str) -> None:
        self.spritePosition = spritePosition
        self.spriteValue = spriteValue
        self.colorRGBValue = colorRGBValue
        self.font = pygame.font.Font(FONT_PATH, spriteSize)

        self.isAllChangesReset = True

        # really need to decide if val in our val out. make both numbers similar.

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        displayText = self.font.render(str(self.spriteValue), True, self.colorRGBValue).convert_alpha()
        displayTextRect = displayText.get_rect(center=self.spritePosition)
        return displayWindow.blit(displayText, displayTextRect)

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):
            if self.spriteValue != 9:
                self.spriteValue += 1
            else:
                self.spriteValue = 0
            self.isAllChangesReset = False


class SecondSideDisplayBlockNumber:
    
    def __init__(self, spritePosition: tuple[int, int], spriteType: str, colorRGBValue: tuple[int, int, int], configFile: ConfigParser, SecondSideDisplayNumber0: SecondSideDisplayNumber, SecondSideDisplayNumber1: SecondSideDisplayNumber) -> None:
        self.spritePosition = spritePosition
        self.spriteType = spriteType   # config.ini variable
        self.colorRGBValue = colorRGBValue
        self.configFile = configFile
        configFileValue = self.configFile.getint("numbervalues", self.spriteType)
        self.spriteValue = "{:02d}".format(configFileValue) if self.spriteType == "interval" else "{:02d}".format(configFileValue//60)

        self.displayImage = pygame.Surface((63, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (0, 0, 10, 32))

        self.SecondSideDisplayNumber0 = SecondSideDisplayNumber0
        self.SecondSideDisplayNumber1 = SecondSideDisplayNumber1

        # self.SecondSideDisplayNumber0 = SecondSideDisplayNumber((self.spritePosition[0]+31, self.spritePosition[1]+16), COLOR_BACKGROUND, 30, int(self.spriteValue[0]))
        # self.SecondSideDisplayNumber1 = SecondSideDisplayNumber((self.spritePosition[0]+47, self.spritePosition[1]+16), COLOR_BACKGROUND, 30, int(self.spriteValue[1]))

    def render(self, displayWindow: pygame.Surface) -> None:
        pygame.draw.rect(self.displayImage, COLOR_SECONDARY, (15, 0, 48, 32))
        displayWindow.blit(self.displayImage, self.spritePosition)
        for SecondSideDisplayNumberObject in (self.SecondSideDisplayNumber0, self.SecondSideDisplayNumber1):
            SecondSideDisplayNumberObject.render(displayWindow)

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        for SecondSideDisplayNumberObject in (self.SecondSideDisplayNumber0, self.SecondSideDisplayNumber1):
            SecondSideDisplayNumberObject.isMouseRightClicked(displayWindow, event, currentMousePosition)

    def saveChangesToConfigFile(self) -> None:
        saveValue = str(self.SecondSideDisplayNumber0.spriteValue * 10 + self.SecondSideDisplayNumber1.spriteValue) if self.spriteType == "interval" else str(self.SecondSideDisplayNumber0.spriteValue * 600 + self.SecondSideDisplayNumber1.spriteValue * 60)
        self.configFile.set("numberValues", self.spriteType, saveValue)

    def resetConfigFileToDefault(self) -> None:
        configFileValue = self.configFile.getint("numberValues", self.spriteType) if self.spriteType == "interval" else self.configFile.getint("numberValues", self.spriteType)//60
        self.spriteValue = "{:02d}".format(configFileValue)
        for (index, SecondSideDisplayNumberObject) in enumerate((self.SecondSideDisplayNumber0, self.SecondSideDisplayNumber1)):
            SecondSideDisplayNumberObject.spriteValue = int(self.spriteValue[index])

    def resetChangesIfNotSaved(self) -> None:
        if any([not SecondSideDisplayNumberObject.isAllChangesReset for SecondSideDisplayNumberObject in (self.SecondSideDisplayNumber0, self.SecondSideDisplayNumber1)]):
            self.resetConfigFileToDefault()
            for SecondSideDisplayNumberObject in (self.SecondSideDisplayNumber0, self.SecondSideDisplayNumber1):
                SecondSideDisplayNumberObject.isAllChangesReset = True

    
class SecondSideDisplayBlockBool:

    def __init__(self, spritePosition: tuple[int, int], spriteType: str, colorRGBValue: tuple[int, int, int], configFile: ConfigParser) -> None:
        self.spritePosition = spritePosition
        self.spriteType = spriteType
        self.colorRGBValue = colorRGBValue
        self.configFile = configFile
        self.spriteValue = self.configFile.getint("boolValues", self.spriteType)

        self.displayImage = pygame.Surface((63, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (0, 0, 10, 32))

        self.isAllChangesReset = True

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        pygame.draw.rect(self.displayImage, COLOR_PRIMARY, (15, 0, 48, 32))
        displayWindow.blit(self.displayImage, self.spritePosition)
        return pygame.draw.rect(displayWindow, COLOR_MACOS_RED, (self.spritePosition[0] + 18, self.spritePosition[1] + 3, 21, 26)) if not self.spriteValue else pygame.draw.rect(displayWindow, COLOR_MACOS_GREEN, (self.spritePosition[0] + 39, self.spritePosition[1] + 3, 21, 26))

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):
            self.spriteValue ^= True
            self.isAllChangesReset = False

    def saveChangesToConfigFile(self) -> None:
        self.configFile.set("boolValues", self.spriteType, str(self.spriteValue))

    def resetConfigFileToDefault(self) -> None:
        self.spriteValue = self.configFile.getint("boolValues", self.spriteType)

    def resetChangesIfNotSaved(self) -> None:
        if not self.isAllChangesReset:
            self.resetConfigFileToDefault()
            self.isAllChangesReset = True


class SecondSideSaveButton:

    def __init__(self, spritePosition: tuple[int, int], colorRGBValue: tuple[int, int, int], configFile: ConfigParser) -> None:
        self.spritePosition = spritePosition
        self.colorRGBValue = colorRGBValue
        self.configFile = configFile

        self.displayImage = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (10, 0, 12, 11.5))
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (3, 29, 26, 3))
        gfxdraw.aapolygon(self.displayImage, ((3, 11.5), (16, 24.5), (29, 11.5)), self.colorRGBValue)
        gfxdraw.filled_polygon(self.displayImage, ((3, 11.5), (16, 24.5), (29, 11.5)), self.colorRGBValue)

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        return displayWindow.blit(self.displayImage, self.spritePosition)

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int], SecondSideDisplayBlockNumbers: tuple[SecondSideDisplayBlockNumber], SecondSideDisplayBlockBools: tuple[SecondSideDisplayBlockBool]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):

            for SecondSideDisplayBlockNumber in SecondSideDisplayBlockNumbers:
                SecondSideDisplayBlockNumber.saveChangesToConfigFile()
            for SecondSideDisplayBlockBool in SecondSideDisplayBlockBools:
                SecondSideDisplayBlockBool.saveChangesToConfigFile()

            with open(CONFIG_PATH, "w") as modifiedConfigFile:
                self.configFile.write(modifiedConfigFile)


class SecondSideResetButton:

    def __init__(self, spritePosition: tuple[int, int], colorRGBValue: tuple[int, int, int], configFile: ConfigParser) -> None:
        self.spritePosition = spritePosition
        self.colorRGBValue = colorRGBValue

        self.configFile = configFile

        self.displayImage = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (10, 1.5, 12, 2))
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (3, 3.5, 26, 3.5))
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (5, 8.5, 22, 22))

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        return displayWindow.blit(self.displayImage, self.spritePosition)

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int], SecondSideDisplayBlockNumbers: tuple[SecondSideDisplayBlockNumber], SecondSideDisplayBlockBools: tuple[SecondSideDisplayBlockBool]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):

            self.configFile.clear()
            self.configFile.add_section("numberValues")
            for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[0:4]:
                self.configFile.set("numbervalues", configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])
            self.configFile.add_section("boolValues")
            for configFileOption in tuple(CONFIG_DEFAULT_VALUES.keys())[4:6]:
                self.configFile.set("boolValues", configFileOption, CONFIG_DEFAULT_VALUES[configFileOption])

            with open(CONFIG_PATH, "w") as modifiedConfigFile:
                self.configFile.write(modifiedConfigFile)

            for SecondSideDisplayBlockNumber in SecondSideDisplayBlockNumbers:
                SecondSideDisplayBlockNumber.resetConfigFileToDefault()
            for SecondSideDisplayBlockBool in SecondSideDisplayBlockBools:
                SecondSideDisplayBlockBool.resetConfigFileToDefault()


class SecondSideAboutButton:

    def __init__(self, spritePosition: tuple[int, int], colorRGBValue: tuple[int, int, int]) -> None:
        self.spritePosition = spritePosition
        self.colorRGBValue = colorRGBValue

        self.displayImage = pygame.Surface((32, 32)).convert()
        self.displayImage.fill(COLOR_MACOS_YELLOW)
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (4, 16, 4, 4))
        pygame.draw.rect(self.displayImage, self.colorRGBValue, (24, 16, 4, 4))
        pygame.draw.rect(self.displayImage, (184, 134, 11), (12, 16, 8, 4))

    def render(self, displayWindow: pygame.Surface) -> pygame.Rect:
        return displayWindow.blit(self.displayImage, self.spritePosition)

    def isMouseRightClicked(self, displayWindow: pygame.Surface, event: pygame.event.Event, currentMousePosition: tuple[int, int]) -> None:
        if all((event.type == MOUSEBUTTONDOWN, event.button == 1, self.render(displayWindow).collidepoint(currentMousePosition))):
            webbrowser.open(ABOUT_ADDRESS, new=2, autoraise=True)