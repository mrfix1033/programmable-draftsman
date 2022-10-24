import pygame


class MyGame:
    def __init__(self, WIDTH=852, HEIGHT=480, FPS=30, SCALE=1):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.FPS = FPS
        self.CENTER_X = WIDTH // 2
        self.CENTER_Y = HEIGHT // 2
        self.SCALE = SCALE
        self.initPyGame()
        self.extraInit()
        self.gameCycle()

    def initPyGame(self):
        pygame.init()
        pygame.mixer.init()
        self.display = pygame.display
        self.screen = self.display.set_mode((self.WIDTH, self.HEIGHT))
        self.display.set_caption("My Game")
        self.clock = pygame.time.Clock()

    def gameCycle(self):
        self.running = True
        while self.running:
            self.clock.tick(self.FPS)
            self.doTick()
            self.display.flip()
        pygame.quit()

    def doTick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        self.extraDoTick()

    def extraInit(self):
        self.drawObjects = []
        # self.x = LoopedInt(0, self.WIDTH - 1)
        # self.y = LoopedInt(0, self.HEIGHT - 1)
        self.radius = 35
        self.x = BounceInt(0 + self.radius, self.WIDTH - 1 - self.radius)
        self.y = BounceInt(0 + self.radius, self.HEIGHT - 1 - self.radius)
        self.counter_colors = BounceInt(0, 256 * 3 - 1)

    def extraDoTick(self):
        self.handlePixels()
        self.x += 3
        self.y += 2
        self.counter_colors += 1
        r = max(0, int(self.counter_colors) - 512)
        g = min(255, max(0, int(self.counter_colors) - 256))
        b = min(int(self.counter_colors), 255)
        self.drawObjects.append(DrawObject(pygame.draw.circle, (r, g, b),
                                           self.display.get_surface(), center=(int(self.x), int(self.y)),
                                           radius=self.radius, objectLiveTicks=150))

    def handlePixels(self):
        need_to_delete_indexes = []
        for i in range(len(self.drawObjects)):
            if self.drawObjects[i].doTick():
                need_to_delete_indexes.append(i)
        for i in need_to_delete_indexes:
            del self.drawObjects[i]


class DrawObject:
    def __init__(self, drawFunc, color, *args, objectLiveTicks=60, **kwargs):
        self.drawFunc = drawFunc
        self.color = color
        self.args = args
        self.kwargs = kwargs
        self.liveTicks = objectLiveTicks
        self.alwaysLive = self.liveTicks == -1
        self.remainedTicks = self.liveTicks

    def doTick(self):
        if self.alwaysLive:
            self.drawFunc(*self.args, color=self.color, **self.kwargs)
            return False
        self.drawFunc(*self.args, color=self.multiplicateColor(self.color, self.remainedTicks / self.liveTicks),
                      **self.kwargs)
        self.remainedTicks -= 1
        return self.remainedTicks == -1

    def multiplicateColor(self, color, multiplier):
        out = []
        for i in color:
            out.append(round(i * multiplier))
        return out


class LoopedInt:
    def __init__(self, start, end, num=0):
        self.shift = start
        self.end = end - self.shift
        self.num = (num - self.shift) % self.end + self.shift

    def __int__(self):
        return self.num

    def __add__(self, other):
        self.end += self.shift
        self.num = (self.num + other.__int__() - self.shift) % self.end + self.shift
        return self

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __eq__(self, other):
        return self.num == other.num


class BounceInt:
    def __init__(self, start, end, num=0):
        self.start = start
        self.end = end
        self.num = num
        if not self.start <= self.num <= self.end:
            self.num = self.start
        self.multiplier = 1

    def __int__(self):
        return self.num

    def __add__(self, other):
        self.num += other * self.multiplier
        while not self.start <= self.num <= self.end:
            if self.num < self.start:
                self.num += self.start - self.num
                self.multiplier = 1
            if self.num > self.end:
                self.num -= self.num - self.end
                self.multiplier = -1
        return self

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __eq__(self, other):
        return self.num == other.num


game = MyGame()
