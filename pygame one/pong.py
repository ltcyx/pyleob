#!/bin/python
from abc import abstractmethod
import pygame
import math


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_angle_magnitude(cls, angle, magnitude):
        return Vector2(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    @property
    def magnitude_sq(self):
        return self.x * self.x + self.y * self.y

    @property
    def magnitude(self):
        return math.sqrt(self.magnitude_sq)

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    def clone(self):
        return Vector2(self.x, self.y)

    def to_tuple(self):
        result = (self.x, self.y)
        return result

    def to_array(self):
        result = [self.x, self.y]
        return result

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        else:
            return Vector2(self.x * other, self.y * other)


class Rect:
    def __init__(self, pos: Vector2, size: Vector2):
        self.pos = pos
        self.size = size

    @property
    def bottom_right(self):
        return Vector2(self.right, self.bottom)

    @property
    def top_left(self):
        return self.pos

    @property
    def left(self):
        return self.pos.x

    @property
    def right(self):
        return self.pos.x + self.size.x

    @property
    def top(self):
        return self.pos.y

    @property
    def bottom(self):
        return self.pos.y + self.size.y

    @property
    def horizontal_center(self):
        return self.pos.x + self.size.x * 0.5

    @property
    def vertical_center(self):
        return self.pos.y + self.size.y * 0.5

    @property
    def center(self):
        return Vector2(self.horizontal_center, self.vertical_center)

    def intersects(self, other):
        return self.left < other.right and self.right > other.left and \
               self.top < other.bottom and self.bottom > other.top

    def contains(self, other):
        return other.right < self.right and other.left > self.left and \
               other.top > self.top and other.bottom < self.bottom


class Drawable:
    def __init__(self, width, height):
        self._pos = Vector2(0, 0)
        self._size = Vector2(width, height)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, val):
        self._pos_setter(val)

    def _pos_setter(self, val):
        self._pos = val

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, val):
        self._size = val

    @abstractmethod
    def draw(self, screen):
        pass

    def get_rect(self):
        return Rect(self.pos, self.size)


class Rectangle(Drawable):
    def __init__(self, width, height, color):
        super(Rectangle, self).__init__(width, height)
        self.color = color

    def draw(self, screen):
        pos = self.pos
        size = self.size
        pygame.draw.rect(screen, self.color, [pos.x, pos.y, size.x, size.y])


class Sprite(Drawable):
    def __init__(self, imagepath, width, height):
        super(Sprite, self).__init__(width, height)
        self.sourceImage = pygame.image.load(imagepath)
        self.image = pygame.transform.scale(self.sourceImage, (width, height))

    def draw(self, screen: pygame.display):
        screen.blit(self.image, self.pos.to_tuple())


class Paddle:
    def __init__(self, drawable: Drawable, key_up, key_down, playfield):
        self.drawable = drawable
        self.key_up = key_up
        self.key_down = key_down
        self.playfield = playfield
        self.speed = 200.0

    def update(self, elapsedtime, keys):
        if keys[self.key_up]:
            self.drawable.pos.y -= self.speed * elapsedtime
        if keys[self.key_down]:
            self.drawable.pos.y += self.speed * elapsedtime

        rect = self.drawable.get_rect()
        if rect.top < self.playfield.top:
            self.drawable.pos.y = self.playfield.top
        if rect.bottom > self.playfield.bottom:
            self.drawable.pos.y = self.playfield.bottom - self.drawable.size.y

    def draw(self, screen):
        self.drawable.draw(screen)


class Ball:
    def __init__(self, drawable: Drawable):
        self.drawable = drawable
        self.velocity = Vector2(200.0, 100.0)
        self.initialPos = drawable.pos.clone()
        self.initialVelocity = self.velocity.clone()

    def update(self, elapsedtime):
        self.drawable.pos += self.velocity * elapsedtime

    def reset(self):
        self.drawable.pos = self.initialPos.clone()
        self.velocity = self.initialVelocity.clone()

    def draw(self, screen):
        self.drawable.draw(screen)


class PlayerUI:
    def __init__(self, pos: Vector2):
        self.pos = pos
        self.score = 0
        self.font = pygame.font.Font(None, 48)  # default font
        self.color = (128, 128, 128)

    def increment_score(self):
        self.score += 1

    def draw(self, screen):
        text = self.font.render(str(self.score), True, self.color)
        screen.blit(text, self.pos.to_tuple())


class Pong:

    def __init__(self):
        self.backgroundColor = (0, 0, 0)
        self.paddleColor = (255, 255, 255)
        self.ballColor = (255, 255, 255)
        self.clock = pygame.time.Clock()
        self.playfield = Rect(Vector2(0, 0), Vector2(800, 600))
        self.paddleMaxAngleDeflection = math.radians(60)

        pygame.init()

        paddlesize = Vector2(10, 100)
        paddlewalldistance = 30

        player1drawable = Rectangle(paddlesize.x, paddlesize.y, self.paddleColor)
        player1drawable.pos = Vector2(0 + paddlewalldistance, 0)
        self.player1 = Paddle(player1drawable, pygame.K_w, pygame.K_s, self.playfield)
        self.player1Score = PlayerUI(Vector2(200, 0))

        player2drawable = Rectangle(paddlesize.x, paddlesize.y, self.paddleColor)
        player2drawable.pos = Vector2(self.playfield.size.x - paddlesize.x - paddlewalldistance, 0)
        self.player2 = Paddle(player2drawable, pygame.K_UP, pygame.K_DOWN, self.playfield)
        self.player2Score = PlayerUI(Vector2(self.playfield.size.x - 200, 0))

        balldrawable = Rectangle(10, 10, self.ballColor)
        #balldrawable = Sprite("drevil-icon.png", 10, 10)
        balldrawable.pos = Vector2(100, 300)
        self.ball = Ball(balldrawable)

        self.screen = None

    def update(self, elapsedtime):
        keys = pygame.key.get_pressed()

        self.player1.update(elapsedtime, keys)
        self.player2.update(elapsedtime, keys)
        self.ball.update(elapsedtime)

        if self.ball.drawable.get_rect().top < self.playfield.top or self.ball.drawable.get_rect().bottom > self.playfield.bottom:
            self.ball.velocity.y *= -1

        ballrect = self.ball.drawable.get_rect()
        player2rect = self.player2.drawable.get_rect()

        if self.ball.drawable.get_rect().intersects(self.player1.drawable.get_rect()):
            #self.ball.velocity.x = abs(self.ball.velocity.x)
            self.deflect(self.ball, self.player1, 1)

        if self.ball.drawable.get_rect().intersects(self.player2.drawable.get_rect()):
            #self.ball.velocity.x = abs(self.ball.velocity.x) * -1
            self.deflect(self.ball, self.player2, -1)

        if self.ball.drawable.get_rect().left < self.playfield.left:
            self.player2Score.increment_score()
            self.ball.reset()
        if self.ball.drawable.get_rect().right > self.playfield.right:
            self.player1Score.increment_score()
            self.ball.reset()

    def deflect(self, ball: Ball, paddle: Paddle, direction: int):
        ballrect = ball.drawable.get_rect()
        paddlerect = paddle.drawable.get_rect()
        ballcenter = ballrect.vertical_center
        paddlecenter = paddlerect.vertical_center

        distance = ballcenter - paddlecenter
        distancenorm = max(min(distance / (paddlecenter - paddlerect.top), 1), -1)  # clamp at (-1, 1) just in case - collision can cause us to be above the paddle's bounds

        magnitude = ball.velocity.magnitude
        straightangle = (direction - 1) * 0.5 * math.pi
        angle = distancenorm * self.paddleMaxAngleDeflection * direction + straightangle
        ball.velocity = Vector2.from_angle_magnitude(angle, magnitude)

    def draw(self):
        self.screen.fill(self.backgroundColor)

        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        self.ball.draw(self.screen)
        self.player1Score.draw(self.screen)
        self.player2Score.draw(self.screen)

        pygame.display.flip()

    def run(self):
        self.screen = pygame.display.set_mode(self.playfield.size.to_tuple())
        pygame.display.set_caption("LUMPong")

        loop = True

        while loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False

            elapsedtime = self.clock.get_time() / 1000.0

            self.update(elapsedtime)
            self.draw()

            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__" :

    game = Pong()
    game.run()
