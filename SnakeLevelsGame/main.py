import random
import sys
import pygame


class LevelConfig:
    def __init__(self, LevelNumber, SnakeSpeed, FieldRect, Obstacles):
        self.LevelNumber = LevelNumber
        self.SnakeSpeed = SnakeSpeed
        self.FieldRect = FieldRect
        self.Obstacles = Obstacles


class Button:
    def __init__(self, Rect, Text, BackgroundColor, TextColor):
        self.Rect = pygame.Rect(Rect)
        self.Text = Text
        self.BackgroundColor = BackgroundColor
        self.TextColor = TextColor

    def drawButton(self, Screen, Font):
        pygame.draw.rect(Screen, self.BackgroundColor, self.Rect, border_radius=8)
        TextSurface = Font.render(self.Text, True, self.TextColor)
        TextRect = TextSurface.get_rect(center=self.Rect.center)
        Screen.blit(TextSurface, TextRect)

    def isClicked(self, MousePosition):
        return self.Rect.collidepoint(MousePosition)


class Snake:
    def __init__(self, StartPosition, SegmentSize):
        self.SegmentSize = SegmentSize
        self.Body = [StartPosition, (StartPosition[0] - SegmentSize, StartPosition[1]), (StartPosition[0] - 2 * SegmentSize, StartPosition[1])]
        self.Direction = (SegmentSize, 0)
        self.PendingDirection = self.Direction

    def setDirection(self, NewDirection):
        OppositeDirection = (-self.Direction[0], -self.Direction[1])
        if NewDirection != OppositeDirection:
            self.PendingDirection = NewDirection

    def move(self, Grow=False):
        self.Direction = self.PendingDirection
        HeadX, HeadY = self.Body[0]
        NewHead = (HeadX + self.Direction[0], HeadY + self.Direction[1])
        self.Body.insert(0, NewHead)
        if not Grow:
            self.Body.pop()

    def getHead(self):
        return self.Body[0]


class Food:
    def __init__(self, Position):
        self.Position = Position


class Game:
    def __init__(self):
        pygame.init()
        self.ScreenWidth = 900
        self.ScreenHeight = 700
        self.Screen = pygame.display.set_mode((self.ScreenWidth, self.ScreenHeight))
        pygame.display.set_caption("Snake Levels Game")
        self.Clock = pygame.time.Clock()

        self.BackgroundColor = (22, 22, 30)
        self.TextColor = (240, 240, 240)
        self.SnakeColor = (80, 220, 120)
        self.FoodColor = (230, 80, 90)
        self.ObstacleColor = (140, 140, 170)
        self.FieldColor = (35, 35, 48)
        self.ButtonColor = (70, 70, 95)

        self.TitleFont = pygame.font.SysFont("arial", 46, bold=True)
        self.MainFont = pygame.font.SysFont("arial", 30)
        self.SmallFont = pygame.font.SysFont("arial", 24)

        self.CellSize = 20
        self.GameState = "Menu"
        self.SelectedLevel = None
        self.CurrentScore = 0
        self.GameStarted = False
        self.GameOver = False

        self.LevelConfigs = self.createLevelConfigs()

        self.MenuButtons = [
            Button((self.ScreenWidth // 2 - 120, 240, 240, 60), "Уровень 1", self.ButtonColor, self.TextColor),
            Button((self.ScreenWidth // 2 - 120, 330, 240, 60), "Уровень 2", self.ButtonColor, self.TextColor),
            Button((self.ScreenWidth // 2 - 120, 420, 240, 60), "Уровень 3", self.ButtonColor, self.TextColor),
        ]

        self.StartButton = Button((self.ScreenWidth // 2 - 75, 640, 150, 50), "Начать", self.ButtonColor, self.TextColor)
        self.MenuButton = Button((self.ScreenWidth // 2 - 140, 390, 280, 56), "В меню", self.ButtonColor, self.TextColor)
        self.RestartButton = Button((self.ScreenWidth // 2 - 140, 470, 280, 56), "Повторить", self.ButtonColor, self.TextColor)

        self.Snake = None
        self.Food = None

    def createLevelConfigs(self):
        return {
            1: LevelConfig(1, 7, pygame.Rect(80, 120, 740, 500), []),
            2: LevelConfig(2, 10, pygame.Rect(100, 120, 700, 500), [
                pygame.Rect(320, 260, 120, 20),
                pygame.Rect(460, 380, 20, 120),
                pygame.Rect(180, 430, 120, 20),
            ]),
            3: LevelConfig(3, 14, pygame.Rect(140, 140, 620, 440), [
                pygame.Rect(240, 220, 160, 20),
                pygame.Rect(500, 220, 20, 160),
                pygame.Rect(320, 400, 180, 20),
                pygame.Rect(180, 320, 20, 140),
                pygame.Rect(580, 360, 120, 20),
            ]),
        }

    def alignToGrid(self, Value):
        return (Value // self.CellSize) * self.CellSize

    def resetGame(self):
        Level = self.LevelConfigs[self.SelectedLevel]
        CenterX = self.alignToGrid(Level.FieldRect.centerx)
        CenterY = self.alignToGrid(Level.FieldRect.centery)
        self.Snake = Snake((CenterX, CenterY), self.CellSize)
        self.CurrentScore = 0
        self.GameStarted = False
        self.GameOver = False
        self.spawnFood()

    def spawnFood(self):
        Level = self.LevelConfigs[self.SelectedLevel]
        AvailablePositions = []
        StartX = Level.FieldRect.left
        EndX = Level.FieldRect.right - self.CellSize
        StartY = Level.FieldRect.top
        EndY = Level.FieldRect.bottom - self.CellSize

        for X in range(StartX, EndX + 1, self.CellSize):
            for Y in range(StartY, EndY + 1, self.CellSize):
                Position = (X, Y)
                SnakeBlocked = Position in self.Snake.Body
                HeadRect = pygame.Rect(X, Y, self.CellSize, self.CellSize)
                ObstacleBlocked = any(Obstacle.colliderect(HeadRect) for Obstacle in Level.Obstacles)
                if not SnakeBlocked and not ObstacleBlocked:
                    AvailablePositions.append(Position)

        if AvailablePositions:
            self.Food = Food(random.choice(AvailablePositions))
        else:
            self.Food = None

    def startLevel(self, LevelNumber):
        self.SelectedLevel = LevelNumber
        self.GameState = "Playing"
        self.resetGame()

    def handleEvents(self):
        for Event in pygame.event.get():
            if Event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if Event.type == pygame.KEYDOWN and self.GameState == "Playing" and self.GameStarted and not self.GameOver:
                if Event.key == pygame.K_UP:
                    self.Snake.setDirection((0, -self.CellSize))
                elif Event.key == pygame.K_DOWN:
                    self.Snake.setDirection((0, self.CellSize))
                elif Event.key == pygame.K_LEFT:
                    self.Snake.setDirection((-self.CellSize, 0))
                elif Event.key == pygame.K_RIGHT:
                    self.Snake.setDirection((self.CellSize, 0))

            if Event.type == pygame.MOUSEBUTTONDOWN and Event.button == 1:
                MousePosition = Event.pos
                if self.GameState == "Menu":
                    for Index, MenuButton in enumerate(self.MenuButtons, start=1):
                        if MenuButton.isClicked(MousePosition):
                            self.startLevel(Index)
                            break
                elif self.GameState == "Playing":
                    if not self.GameStarted and self.StartButton.isClicked(MousePosition):
                        self.GameStarted = True
                    if self.GameOver:
                        if self.MenuButton.isClicked(MousePosition):
                            self.GameState = "Menu"
                        elif self.RestartButton.isClicked(MousePosition):
                            self.resetGame()

    def _checkCollision(self):
        Level = self.LevelConfigs[self.SelectedLevel]
        HeadX, HeadY = self.Snake.getHead()
        HeadRect = pygame.Rect(HeadX, HeadY, self.CellSize, self.CellSize)

        if not Level.FieldRect.contains(HeadRect):
            return True

        if self.Snake.getHead() in self.Snake.Body[1:]:
            return True

        for Obstacle in Level.Obstacles:
            if Obstacle.colliderect(HeadRect):
                return True
        return False

    def updateGame(self):
        if self.GameState != "Playing" or not self.GameStarted or self.GameOver:
            return

        HeadX, HeadY = self.Snake.getHead()
        NextHead = (
            HeadX + self.Snake.PendingDirection[0],
            HeadY + self.Snake.PendingDirection[1],
        )
        GrowSnake = self.Food and NextHead == self.Food.Position
        self.Snake.move(Grow=GrowSnake)

        if self._checkCollision():
            self.GameOver = True
            return

        if self.Food and self.Snake.getHead() == self.Food.Position:
            self.CurrentScore += 1
            self.spawnFood()

    def drawMenu(self):
        self.Screen.fill(self.BackgroundColor)
        Title = self.TitleFont.render("Snake Levels", True, self.TextColor)
        TitleRect = Title.get_rect(center=(self.ScreenWidth // 2, 140))
        self.Screen.blit(Title, TitleRect)

        for MenuButton in self.MenuButtons:
            MenuButton.drawButton(self.Screen, self.MainFont)

    def drawGame(self):
        Level = self.LevelConfigs[self.SelectedLevel]
        self.Screen.fill(self.BackgroundColor)

        Header = self.SmallFont.render(f"Уровень: {Level.LevelNumber}    Счёт: {self.CurrentScore}", True, self.TextColor)
        self.Screen.blit(Header, (80, 40))

        pygame.draw.rect(self.Screen, self.FieldColor, Level.FieldRect)
        pygame.draw.rect(self.Screen, (80, 80, 100), Level.FieldRect, width=2)

        for Obstacle in Level.Obstacles:
            pygame.draw.rect(self.Screen, self.ObstacleColor, Obstacle)

        if self.Food:
            pygame.draw.rect(self.Screen, self.FoodColor, (*self.Food.Position, self.CellSize, self.CellSize))

        for Segment in self.Snake.Body:
            pygame.draw.rect(self.Screen, self.SnakeColor, (*Segment, self.CellSize, self.CellSize))

        if not self.GameStarted and not self.GameOver:
            self.StartButton.drawButton(self.Screen, self.SmallFont)

        if self.GameOver:
            Overlay = pygame.Surface((self.ScreenWidth, self.ScreenHeight), pygame.SRCALPHA)
            Overlay.fill((0, 0, 0, 130))
            self.Screen.blit(Overlay, (0, 0))

            GameOverText = self.TitleFont.render("Игра окончена", True, self.TextColor)
            ScoreText = self.MainFont.render(f"Итоговый счёт: {self.CurrentScore}", True, self.TextColor)
            self.Screen.blit(GameOverText, GameOverText.get_rect(center=(self.ScreenWidth // 2, 280)))
            self.Screen.blit(ScoreText, ScoreText.get_rect(center=(self.ScreenWidth // 2, 340)))
            self.MenuButton.drawButton(self.Screen, self.MainFont)
            self.RestartButton.drawButton(self.Screen, self.MainFont)

    def run(self):
        while True:
            self.handleEvents()
            self.updateGame()

            if self.GameState == "Menu":
                self.drawMenu()
                self.Clock.tick(60)
            else:
                self.drawGame()
                Level = self.LevelConfigs[self.SelectedLevel]
                self.Clock.tick(Level.SnakeSpeed if self.GameStarted and not self.GameOver else 60)

            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
