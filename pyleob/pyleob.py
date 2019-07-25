#!/bin/python

from __future__ import annotations
from abc import abstractmethod
import pygame
import math

COLLISION_MATRIX_DEPTH = 8

class EventHook:

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, other):
        self.__handlers.append(other)
        return self

    def __isub__(self, other):
        self.__handlers.remove(other)
        return self

    def invoke(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)


class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @classmethod
    def from_angle_magnitude(cls, angle: float, magnitude: float):
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


class Component:

    def __init__(self):
        self._active = True;

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, val: bool):
        self.set_active(val)

    def set_active(self, val: bool):
        self._active = val


class Drawable(Component):
    def __init__(self, width: float, height: float):
        super(Drawable, self).__init__()
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

    def sort_key_y(self):
        return self.pos.y


class Rectangle(Drawable):
    def __init__(self, width: float, height: float, color):
        super(Rectangle, self).__init__(width, height)
        self.color = color

    def draw(self, screen):
        pos = self.pos
        size = self.size
        pygame.draw.rect(screen, self.color, [pos.x, pos.y, size.x, size.y])


class Sprite(Drawable):
    def __init__(self, imagepath: str, width: float, height: float):
        super(Sprite, self).__init__(width, height)
        self.sourceImage = pygame.image.load(imagepath)
        self.image = pygame.transform.scale(self.sourceImage, (width, height))

    def draw(self, screen: pygame.display):
        screen.blit(self.image, self.pos.to_tuple())


class Entity(Component):

    @abstractmethod
    def update(self, elapsedtime: float, keys: dict):
        pass


class GameObject(Entity):

    def __init__(self, drawable: Drawable, collision_layer: int = -1):
        super(GameObject, self).__init__()
        self.drawable = drawable
        self._collision_layer = collision_layer

    @property
    def collision_layer(self):
        return self._collision_layer

    def get_collider(self):
        return self.drawable.get_rect()

    def set_active(self, val: bool):
        super(GameObject, self).set_active(val)
        self.drawable.set_active(val)

    @abstractmethod
    def update(self, elapsedtime: float, keys: dict):
        pass

    @abstractmethod
    def on_collision(self, other: GameObject):
        pass


class Game2D:

    def __init__(self, gameName: str, screenSize: Vector2, collisionMatrix):
        self.gameName = gameName
        self.backgroundColor = (0, 0, 0)
        self.clock = pygame.time.Clock()
        self.screenSize = screenSize
        self.screen = None
        self.entities = []
        self.entities_by_collision_layer = {}
        self.drawables = []
        self.game_objects_to_remove = []
        self.collision_matrix = collisionMatrix

        matrix_size_diff = COLLISION_MATRIX_DEPTH - len(self.collision_matrix)
        if matrix_size_diff > 0:
            for i in range(matrix_size_diff):
                self.collision_matrix.append(0)

        pygame.init()

    def add_game_object(self, game_object: GameObject):
        self.add_entity(game_object)
        self.add_drawable(game_object.drawable)
        self.add_game_object_to_collision_layer(game_object)

    def remove_game_object(self, game_object: GameObject):
        game_object.active = False
        self.game_objects_to_remove.append(game_object)

    def remove_game_object_now(self, game_object: GameObject):
        self.remove_drawable(game_object.drawable)
        self.remove_entity(game_object)
        self.remove_game_object_from_collision_layer(game_object)

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def remove_entity(self, entity: Entity):
        self.entities.remove(entity)

    def add_drawable(self, drawable: Drawable):
        self.drawables.append(drawable)

    def remove_drawable(self, drawable: Drawable):
        self.drawables.remove(drawable)

    def remove_game_object_from_collision_layer(self, game_object: GameObject):
        if game_object.collision_layer >= 0:
            self.entities_by_collision_layer[game_object.collision_layer].remove(game_object)

    def add_game_object_to_collision_layer(self, game_object: GameObject):
        if game_object.collision_layer >= 0:
            self._add_game_object_to_collision_layer(game_object, game_object.collision_layer)

    def _add_game_object_to_collision_layer(self, game_object: GameObject, layer: int):
        if layer not in self.entities_by_collision_layer:
            self.entities_by_collision_layer[layer] = []

        self.entities_by_collision_layer[layer].append(game_object)

    def get_mask_value_for_layer(self, layer: int) -> int:
        return 1 << layer

    def collision_enabled_between_layers(self, layer1:int, layer2:int) -> bool:
        return self.collision_matrix[layer1] & self.get_mask_value_for_layer(layer2) != 0

    def get_entities_by_collision_layer(self, layer:int) -> [GameObject]:
        if layer in self.entities_by_collision_layer.keys():
            return self.entities_by_collision_layer[layer]
        else:
            return []

    def __main_update(self, elapsedtime: float):
        keys = pygame.key.get_pressed()

        self.early_update(elapsedtime, keys)

        for entity in self.entities:
            if entity.active:
                entity.update(elapsedtime, keys)

        self.calculate_collisions()

        self.late_update(elapsedtime, keys)

        for obj in self.game_objects_to_remove:
            self.remove_game_object_now(obj)
        self.game_objects_to_remove = []

    @abstractmethod
    def early_update(self, elapsedtime: float, keys: dict):
        pass

    def calculate_collisions(self):
        for i in range(COLLISION_MATRIX_DEPTH):
            for j in range(i, COLLISION_MATRIX_DEPTH):
                if self.collision_enabled_between_layers(i, j):
                    layer1 = self.get_entities_by_collision_layer(i)
                    layer2 = self.get_entities_by_collision_layer(j)
                    for ob1 in layer1:
                        for ob2 in layer2:
                            if ob1 != ob2 and ob1.get_collider().intersects(ob2.get_collider()):
                                ob1.on_collision(ob2)
                                ob2.on_collision(ob1)

    @abstractmethod
    def late_update(self, elapsedtime: float, keys: dict):
        pass

    def __main_draw(self):
        self.screen.fill(self.backgroundColor)

        self.draw()

        self.drawables.sort(key=Drawable.sort_key_y)
        for drawable in self.drawables:
            if drawable.active:
                drawable.draw(self.screen)

        pygame.display.flip()

    @abstractmethod
    def draw(self):
        pass

    def run(self):
        self.screen = pygame.display.set_mode(self.screenSize.to_tuple())
        pygame.display.set_caption(self.gameName)

        loop = True

        while loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False

            elapsedtime = self.clock.get_time() / 1000.0

            self.__main_update(elapsedtime)
            self.__main_draw()

            self.clock.tick(60)

        pygame.quit()

