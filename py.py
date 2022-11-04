import pygame
from copy import deepcopy


class MyGame:
    def __init__(self, WIDTH=852, HEIGHT=480, FPS=30, SCALE=1.0):
        self.WIDTH = WIDTH * SCALE
        self.HEIGHT = HEIGHT * SCALE
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
        self.colorHandler = ColorGradientHandler()
        self.drawObjects = []
        # see LoopedInt and run program
        self.x = LoopedInt(0, self.WIDTH - 1)
        self.y = LoopedInt(0, self.HEIGHT - 1)
        self.radius = 35 * self.SCALE
        # after comment previous code, uncomment this code, see BounceInt, run program
        # self.x = BounceInt(0 + self.radius, self.WIDTH - 1 - self.radius)
        # self.y = BounceInt(0 + self.radius, self.HEIGHT - 1 - self.radius)
        self.counter_colors = BounceInt(0, 256 * 3 - 1)
        # I want to add a gradient

    def extraDoTick(self):
        self.handleDrawObjects()
        self.x += 3
        self.y += 2
        self.counter_colors += 1
        self.drawObjects.append(DrawObject(pygame.draw.circle, self.colorHandler.nextColor(),
                                           self.display.get_surface(), center=(int(self.x), int(self.y)),
                                           radius=self.radius, objectLiveTicks=150))

    def handleDrawObjects(self):
        need_to_delete_indexes = []
        for i in range(len(self.drawObjects)):
            if self.drawObjects[i].doTick():
                need_to_delete_indexes.append(i)
        for i in need_to_delete_indexes:
            del self.drawObjects[i]


class DrawObject:
    def __init__(self, drawFunc, color, *args, objectLiveTicks=60, **kwargs):
        # args, kwargs - arguments for drawFunc
        # drawFunc - function that draws an object (circle, rectangle, pixel, etc.)
        # if objectLiveTicks == -1, object isn't vanish
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
        # function that multiplies values of color
        out = []
        for i in color:
            out.append(round(i * multiplier))
        return out


# start = 0, end = 10, num = 0
# always +3
# 0, 3, 6, 9, 2, 5, 8, 1, 4, 7, 10, 3, ...
class LoopedInt:
    def __init__(self, start, end, num=0):
        self.shift = start
        self.end = end - self.shift
        self.num = int((num - self.shift) % self.end + self.shift)

    def __int__(self):
        return self.num

    def __add__(self, other):
        self.end += self.shift
        self.num = int((self.num + other.__int__() - self.shift) % self.end + self.shift)
        return self

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __eq__(self, other):
        return self.num == other.num


# start = 0, end = 10, num = 0
# always +3
# 0, 3, 6, 9, 8, 5, 2, 1, 4, 7, 10, 7, ...
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
        # need to optimize
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


class ColorGradientHandler:
    def __init__(self, start_colors=[[0, 0, 0], [255, 0, 0]],
                 looped_colors=[[255, 255, 0], [0, 255, 255], [255, 0, 255]],
                 transition_time=255):
        self.start_colors = deepcopy(start_colors)
        self.looped_colors = deepcopy(looped_colors)
        self.transition_time = transition_time
        self.transition_time_now = 0
        if isinstance(self.start_colors[0], int):
            self.start_colors = [self.start_colors]
        if isinstance(self.looped_colors[0], int):
            self.looped_colors = [self.looped_colors]
        self.r = self.g = self.b = 0
        self.color_now = 0
        self.color_next = 1
        self.startIsEnd = False
        self.startIsPreEnd = False

    def nextColor(self):
        return self.handleNextColor()

    def handleNextColor(self):
        self.oldR, self.oldB, self.oldG = self.r, self.g, self.b
        if self.startIsEnd:
            self.r = self.looped_colors[self.color_now][0] + \
                     (self.looped_colors[self.color_next][0] - self.looped_colors[self.color_now][0]) * \
                     (self.transition_time_now / self.transition_time)
            self.g = self.looped_colors[self.color_now][1] + \
                     (self.looped_colors[self.color_next][1] - self.looped_colors[self.color_now][1]) * \
                     (self.transition_time_now / self.transition_time)
            self.b = self.looped_colors[self.color_now][2] + \
                     (self.looped_colors[self.color_next][2] - self.looped_colors[self.color_now][2]) * \
                     (self.transition_time_now / self.transition_time)
        else:
            if self.color_next == len(self.start_colors):
                self.startIsPreEnd = True
                self.color_next = 0
                return self.handleNextColor()
            elif self.color_now == len(self.start_colors):
                self.startIsEnd = True
                self.color_now = 0
                return self.handleNextColor()
            elif self.startIsPreEnd:
                self.r = self.start_colors[self.color_now][0] + \
                         (self.looped_colors[self.color_next][0] - self.start_colors[self.color_now][0]) * \
                         (self.transition_time_now / self.transition_time)
                self.g = self.start_colors[self.color_now][1] + \
                         (self.looped_colors[self.color_next][1] - self.start_colors[self.color_now][1]) * \
                         (self.transition_time_now / self.transition_time)
                self.b = self.start_colors[self.color_now][2] + \
                         (self.looped_colors[self.color_next][2] - self.start_colors[self.color_now][2]) * \
                         (self.transition_time_now / self.transition_time)
            else:
                self.r = self.start_colors[self.color_now][0] + \
                         (self.start_colors[self.color_next][0] - self.start_colors[self.color_now][0]) * \
                         (self.transition_time_now / self.transition_time)
                self.g = self.start_colors[self.color_now][1] + \
                         (self.start_colors[self.color_next][1] - self.start_colors[self.color_now][1]) * \
                         (self.transition_time_now / self.transition_time)
                self.b = self.start_colors[self.color_now][2] + \
                         (self.start_colors[self.color_next][2] - self.start_colors[self.color_now][2]) * \
                         (self.transition_time_now / self.transition_time)

        self.transition_time_now += 1
        self.checkGlobalNextColor()
        return self.oldR, self.oldB, self.oldG

    def checkGlobalNextColor(self):
        if self.transition_time == self.transition_time_now:
            self.color_now = (self.color_now + 1) % \
                             (len(self.looped_colors) if self.startIsEnd else len(self.start_colors) + 1)
            self.color_next = (self.color_next + 1) % \
                              (len(self.looped_colors) if self.startIsPreEnd else len(self.start_colors) + 1)
            self.transition_time_now = 0
            # return: color was changed?
            return True
        return False


game = MyGame()
