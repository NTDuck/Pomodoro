
from utils.control import *


def main():
    
    pygame.font.init()
    pygame.init()

    ControlOtherFunctionsInstance = ControlOtherFunctions()   # executed first to get global variable `configFileValueTimeLengths`
    
    ControlTimerFunctionsInstance = ControlTimerFunctions()
    FirstSideSystemButtonInstances = (
        FirstSideSystemButton((25, 25), 0, COLOR_MACOS_RED),
        FirstSideSystemButton((40, 25), 1, COLOR_MACOS_YELLOW),
        FirstSideSystemButton((55, 25), 2, COLOR_MACOS_GREEN)
    )
    BothSideSettingsButtonInstance = BothSideSettingsButton((193, 25), COLOR_PRIMARY)
    FirstSideDisplayNumberInstances = (
        FirstSideDisplayNumber((45, 155), 80, 0, COLOR_PRIMARY, FONT_PATH),
        FirstSideDisplayNumber((87, 155), 80, 1, COLOR_PRIMARY, FONT_PATH),
        FirstSideDisplayNumber((163, 155), 80, 2, COLOR_PRIMARY, FONT_PATH),
        FirstSideDisplayNumber((205, 155), 80, 3, COLOR_PRIMARY, FONT_PATH)
    )
    FirstSideDisplayColonInstance = FirstSideDisplayColon((125, 150), 80, COLOR_PRIMARY, FONT_PATH)
    FirstSidePlayPauseButtonInstance = FirstSidePlayPauseButton((109, 243), COLOR_PRIMARY)
    FirstSideSkipButtonInstance = FirstSideSkipButton((193, 243), COLOR_PRIMARY)
    SecondSideDisplayBlockNumberInstances = (
        SecondSideDisplayBlockNumber((35, 92), "work", COLOR_MACOS_RED),
        SecondSideDisplayBlockNumber((50, 139), "shortBreak", COLOR_MACOS_RED),
        SecondSideDisplayBlockNumber((35, 186), "longBreak", COLOR_MACOS_RED),
        SecondSideDisplayBlockNumber((135, 92), "interval", COLOR_MACOS_RED)
    )
    SecondSideDisplayBlockBoolInstances = (
        SecondSideDisplayBlockBool((150, 139), COLOR_SECONDARY, "isAutoSwitchOn"),
        SecondSideDisplayBlockBool((135, 186), COLOR_SECONDARY, "isSoundOn")
    )
    SecondSideSaveButtonInstance = SecondSideSaveButton((109, 243), COLOR_PRIMARY)
    SecondSideResetButtonInstance = SecondSideResetButton((156, 243), COLOR_PRIMARY)
    SecondSideAboutButtonInstance = SecondSideAboutButton((62, 243), COLOR_PRIMARY)

    Daemon = pygame.time.Clock()

    PomodoroTimerApplication = ControlMainFunctions(
        ControlTimerFunctions=ControlTimerFunctionsInstance,
        ControlOtherFunctions=ControlOtherFunctionsInstance,
        FirstSideSystemButtons=FirstSideSystemButtonInstances,
        BothSideSettingsButton=BothSideSettingsButtonInstance,
        FirstSideDisplayNumbers=FirstSideDisplayNumberInstances,
        FirstSideDisplayColon=FirstSideDisplayColonInstance,
        FirstSidePlayPauseButton=FirstSidePlayPauseButtonInstance,
        FirstSideSkipButton=FirstSideSkipButtonInstance,
        SecondSideDisplayBlockNumbers=SecondSideDisplayBlockNumberInstances,
        SecondSideDisplayBlockBools=SecondSideDisplayBlockBoolInstances,
        SecondSideSaveButton=SecondSideSaveButtonInstance,
        SecondSideResetButton=SecondSideResetButtonInstance,
        SecondSideAboutButton=SecondSideAboutButtonInstance,
        DaemonGlobal=Daemon,
        displayWindowDeviation=10,
        displayWindowCaption="POM",
        iconColorRGBValue=COLOR_MACOS_YELLOW,
        transparentColorRGBValue=(0, 0, 0)
    )

    PomodoroTimerApplication.masterControlRuntime()


if __name__ == "__main__":
    main()