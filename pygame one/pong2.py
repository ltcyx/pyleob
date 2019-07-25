#!/bin/python

import pygame
import math
from pyleob.pyleob import Game2D, Vector2, GameObject, Rectangle, Rect, Drawable, EventHook


class Ball(GameObject):
    def __init__(self, drawable: Drawable, playfield: Rect):
        super(Ball, self).__init__(drawable, 1)
        self.drawable = drawable
        self.velocity = Vector2(200.0, 100.0)
        self.initialPos = drawable.pos.clone()
        self.initialVelocity = self.velocity.clone()
        self.playfield = playfield

    def update(self, elapsedtime, keys):
        self.drawable.pos += self.velocity * elapsedtime
        rect = self.drawable.get_rect()
        if rect.top < self.playfield.top or rect.bottom > self.playfield.bottom:
            self.velocity.y *= -1

    def reset(self):
        self.drawable.pos = self.initialPos.clone()
        self.velocity = self.initialVelocity.clone()


class Paddle(GameObject):
    def __init__(self, drawable: Drawable, key_up: int, key_down: int, playfield: Rect, deflect_direction: int):
        super(Paddle, self).__init__(drawable, 0)
        self.drawable = drawable
        self.key_up = key_up
        self.key_down = key_down
        self.playfield = playfield
        self.speed = 200.0
        self.deflect_direction = deflect_direction
        self.paddleMaxAngleDeflection = math.radians(60)

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

    def on_collision(self, other: GameObject):
        if isinstance(other, Ball):
            self.deflect(other, self.deflect_direction)

    def deflect(self, ball: Ball, direction: int):
        ballrect = ball.drawable.get_rect()
        paddlerect = self.drawable.get_rect()
        ballcenter = ballrect.vertical_center
        paddlecenter = paddlerect.vertical_center

        distance = ballcenter - paddlecenter
        distancenorm = max(min(distance / (paddlecenter - paddlerect.top), 1), -1)  # clamp at (-1, 1) just in case - collision can cause us to be above the paddle's bounds

        magnitude = ball.velocity.magnitude
        straightangle = (direction - 1) * 0.5 * math.pi
        angle = distancenorm * self.paddleMaxAngleDeflection * direction + straightangle
        ball.velocity = Vector2.from_angle_magnitude(angle, magnitude)


class PlayerUI(Drawable):
    def __init__(self, pos: Vector2):
        super(PlayerUI, self).__init__(1, 1)
        self.pos = pos
        self.score = 0
        self.font = pygame.font.Font(None, 48)  # default font
        self.color = (128, 128, 128)

    def increment_score(self):
        self.score += 1

    def draw(self, screen):
        text = self.font.render(str(self.score), True, self.color)
        screen.blit(text, self.pos.to_tuple())


class Pong(Game2D):

    def __init__(self, screen_size: Vector2):
        super(Pong, self).__init__("Pong2", screen_size, [0b10])
        self.backgroundColor = (0, 0, 0)
        self.paddleColor = (255, 255, 255)
        self.ballColor = (255, 255, 255)
        self.clock = pygame.time.Clock()
        self.playfield = Rect(Vector2(0, 0), screen_size)

        paddlesize = Vector2(10, 100)
        paddlewalldistance = 30

        player1drawable = Rectangle(paddlesize.x, paddlesize.y, self.paddleColor)
        player1drawable.pos = Vector2(0 + paddlewalldistance, 0)
        self.player1 = Paddle(player1drawable, pygame.K_w, pygame.K_s, self.playfield, 1)
        self.add_game_object(self.player1)
        self.player1Score = PlayerUI(Vector2(200, 0))
        self.add_drawable(self.player1Score)

        player2drawable = Rectangle(paddlesize.x, paddlesize.y, self.paddleColor)
        player2drawable.pos = Vector2(self.playfield.size.x - paddlesize.x - paddlewalldistance, 0)
        self.player2 = Paddle(player2drawable, pygame.K_UP, pygame.K_DOWN, self.playfield, -1)
        self.add_game_object(self.player2)
        self.player2Score = PlayerUI(Vector2(self.playfield.size.x - 200, 0))
        self.add_drawable(self.player2Score)

        balldrawable = Rectangle(10, 10, self.ballColor)
        #balldrawable = Sprite("drevil-icon.png", 10, 10)
        balldrawable.pos = Vector2(100, 300)
        self.ball = Ball(balldrawable, self.playfield)
        self.add_game_object(self.ball)

    def late_update(self, elapsedtime: float, keys: dict):

        if self.ball.drawable.get_rect().left < self.playfield.left:
            self.player2Score.increment_score()
            self.ball.reset()
        if self.ball.drawable.get_rect().right > self.playfield.right:
            self.player1Score.increment_score()
            self.ball.reset()

    def draw(self):
        pass


if __name__ == "__main__":

    game = Pong(Vector2(800, 600))
    game.run()
