#!/bin/python

import pygame
import math
from enum import Enum
from typing import Callable
from abc import abstractmethod
from pyleob.pyleob import Game2D, Vector2, GameObject, Rectangle, Rect, Drawable, EventHook


class Brick(GameObject):

    def __init__(self, pos: Vector2, size: Vector2, color, on_ball_collision: Callable[[GameObject], None]):
        super(Brick, self).__init__(Rectangle(size.x, size.y, color), 2)
        self.drawable.pos = pos
        self._on_ball_collision = on_ball_collision

    def update(self, elapsedtime: float, keys: dict):
        pass

    def on_collision(self, other: GameObject):
        if isinstance(other, Ball):
            self._on_ball_collision(self)


class Paddle(GameObject):
    def __init__(self, size: Vector2, playfield: Rect):
        super(Paddle, self).__init__(Rectangle(size.x, size.y, (255, 255, 255)), 1)
        self.playfield = playfield
        self.speed = 400.0
        self.key_left = pygame.K_LEFT
        self.key_right = pygame.K_RIGHT

    def update(self, elapsedtime: float, keys: dict):
        if keys[self.key_left]:
            self.drawable.pos.x -= self.speed * elapsedtime
        if keys[self.key_right]:
            self.drawable.pos.x += self.speed * elapsedtime

        rect = self.drawable.get_rect()
        if rect.left < self.playfield.left:
            self.drawable.pos.x = self.playfield.left
        if rect.right > self.playfield.right:
            self.drawable.pos.x = self.playfield.right - self.drawable.size.x

    def on_collision(self, other: GameObject):
        pass


class Ball(GameObject):
    def __init__(self, pos: Vector2, size: Vector2, playfield: Rect, paddleMaxAngleDeflection: float):
        super(Ball, self).__init__(Rectangle(size.x, size.y, (255, 255, 255)), 0)
        self.drawable.pos = pos
        self.velocity = Vector2(300.0, 200.0)
        self.initialPos = self.drawable.pos.clone()
        self.lastPos = self.initialPos
        self.initialVelocity = self.velocity.clone()
        self.playfield = playfield
        self.paddleMaxAngleDeflection = paddleMaxAngleDeflection

    def update(self, elapsedtime: float, keys: dict):
        self.lastPos = self.drawable.pos
        self.drawable.pos += self.velocity * elapsedtime

        rect = self.drawable.get_rect()
        if rect.left < self.playfield.left:
            self.drawable.pos.x = self.playfield.left
            self.velocity.x = -self.velocity.x
        if rect.right > self.playfield.right:
            self.drawable.pos.x = self.playfield.right - self.drawable.size.x
            self.velocity.x = -self.velocity.x
        if rect.top < self.playfield.top:
            self.drawable.pos.y = self.playfield.top
            self.velocity.y = -self.velocity.y
        if rect.bottom > self.playfield.bottom:
            #death
            self.reset()

    def reset(self):
        self.drawable.pos = self.initialPos.clone()
        self.velocity = self.initialVelocity.clone()

    def on_collision(self, other: GameObject):
        if isinstance(other, Brick):
            other_rect = other.drawable.get_rect()

            self_rect_last = Rect(self.lastPos, self.drawable.size)

            if self_rect_last.left > other_rect.right:
                self.velocity.x = abs(self.velocity.x)
            if self_rect_last.right < other_rect.left:
                self.velocity.x = abs(self.velocity.x) * -1
            if self_rect_last.top > other_rect.bottom:
                self.velocity.y = abs(self.velocity.y)
            if self_rect_last.bottom < other_rect.top:
                self.velocity.y = abs(self.velocity.y) * -1

        if isinstance(other, Paddle):
            self.deflect(other, -1)

    def deflect(self, paddle: Paddle, direction: int):
        ballrect = self.drawable.get_rect()
        paddlerect = paddle.drawable.get_rect()
        ballcenter = ballrect.horizontal_center
        paddlecenter = paddlerect.horizontal_center

        distance = paddlecenter - ballcenter
        distancenorm = max(min(distance / (paddlecenter - paddlerect.left), 1), -1)  # clamp at (-1, 1) just in case - collision can cause us to be above the paddle's bounds

        magnitude = self.velocity.magnitude
        straightangle = (direction - 1) * 0.5 * math.pi + math.pi * 0.5
        angle = distancenorm * self.paddleMaxAngleDeflection * direction + straightangle
        self.velocity = Vector2.from_angle_magnitude(angle, magnitude)


class PowerUpToken(GameObject):
    def __init__(self, brick: Brick, color, playfield: Rect):
        super(PowerUpToken, self).__init__(Rectangle(brick.drawable.size.x, brick.drawable.size.y, color), 4)
        self.drawable.pos = brick.drawable.pos.clone()
        self.on_activation = EventHook()
        self.velocity = Vector2(0, 50)
        self.playfield = playfield

    def update(self, elapsedtime: float, keys: dict):
        self.drawable.pos += self.velocity * elapsedtime

        if self.drawable.get_rect().top > self.playfield.bottom:
            # die
            pass

    def on_collision(self, other: GameObject):
        if isinstance(other, Paddle):
            self.handle_activation(other)
            self.on_activation.invoke(self, other)

    @abstractmethod
    def handle_activation(self, paddle):
        pass


class InstantPowerUpToken(PowerUpToken):
    def __init__(self, brick:Brick, color, playfield: Rect):
        super(InstantPowerUpToken, self).__init__(brick, color, playfield)

    @abstractmethod
    def handle_activation(self, paddle):
        pass


class MultiBallPowerUpToken(InstantPowerUpToken):
    def __init__(self, brick: Brick, color, playfield: Rect):
        super(InstantPowerUpToken, self).__init__(brick, color, playfield)

    def handle_activation(self, paddle):
        pass


class Breakton(Game2D):

    def __init__(self, screen_size: Vector2, bricks_per_row: int, rows: int):
        super(Breakton, self).__init__("Breakton", screen_size, [0b110])
        self.paddleMaxAngleDeflection = math.radians(60)

        playfieldSize = screen_size * Vector2(0.95, 0.9)
        playfieldPos = Vector2((screen_size.x - playfieldSize.x)/2, screen_size.y - playfieldSize.y)

        self.playfield = Rect(playfieldPos, playfieldSize)
        self.bricks = []

        #screen corners
        border_color = (40, 40, 40)
        left_edge = Rectangle(self.playfield.pos.x, screen_size.y, border_color)
        top_edge = Rectangle(screen_size.x, screen_size.y - self.playfield.size.y, border_color)
        right_edge = Rectangle(self.playfield.pos.x, screen_size.y, border_color)
        right_edge.pos = Vector2(self.playfield.right, 0)
        self.add_drawable(left_edge)
        self.add_drawable(top_edge)
        self.add_drawable(right_edge)

        #bricks
        brick_spacing = 4
        top_space = self.playfield.top + (self.playfield.size.y / 16) + brick_spacing / 2
        left_space = self.playfield.left + brick_spacing / 2
        brick_width = (playfieldSize.x / bricks_per_row) - brick_spacing
        brick_height = 10

        def kill_brick(br):
            self.remove_game_object(br)

        for i in range(0, rows):
            for j in range(0, bricks_per_row):
                brick = Brick(Vector2(left_space + (j * (brick_width + brick_spacing)), top_space + (i * (brick_height + brick_spacing))),
                              Vector2(brick_width, brick_height), (255, 255, 255), kill_brick)
                self.add_game_object(brick)
                self.bricks.append(brick)

        self.paddle = Paddle(Vector2(80, 10), self.playfield)
        self.paddle.drawable.pos = Vector2(self.playfield.horizontal_center - self.paddle.drawable.size.x / 2, self.playfield.bottom - self.paddle.drawable.size.y)
        self.add_game_object(self.paddle)

        self.ball = Ball(self.playfield.size.clone() * 0.5, Vector2(10, 10), self.playfield, self.paddleMaxAngleDeflection)
        self.add_game_object(self.ball)


if __name__ == "__main__":

    game = Breakton(Vector2(800, 600), 16, 5)
    game.run()
