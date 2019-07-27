#!/bin/python

from __future__ import annotations
from abc import abstractmethod
import pygame
import math

COLLISION_MATRIX_DEPTH = 8


class EventHook:
    """
    A C#-style Event that allows handlers to be added and removed with += and -=
    """

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, other):
        self.__handlers.append(other)
        return self

    def __isub__(self, other):
        if other in self.__handlers:
            self.__handlers.remove(other)
        return self

    def invoke(self, *args, **keywargs):
        """
        Invoke the event, causing all the handlers to be called
        """
        for handler in self.__handlers:
            handler(*args, **keywargs)


class Vector2:
    """
    A 2-dimensional point or vector. Can be used to represent positions, velocities, sizes, directions, etc.
    """

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    @classmethod
    def from_angle_magnitude(cls, angle: float, magnitude: float) -> Vector2:
        """
        Create a new Vector2 representing a direction or vector using an angle (in radians) and magnitude (or length)
        """
        return Vector2(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    @property
    def magnitude_sq(self) -> float:
        """
        Square of the Vector2's magnitude, or length, assuming that the Vector2 represents a vector
        """
        return self.x * self.x + self.y * self.y

    @property
    def magnitude(self) -> float:
        """
        The Vector2's magnitude, or length, assuming that the Vector2 represents a vector
        """
        return math.sqrt(self.magnitude_sq)

    @property
    def angle(self) -> float:
        """
        The Vector2's angle, assuming that the Vector2 represents a vector
        """
        return math.atan2(self.y, self.x)

    def clone(self) -> Vector2:
        """
        Creates a copy of the Vector2
        """
        return Vector2(self.x, self.y)

    def to_tuple(self) -> (int, int):
        """
        Returns the Vector2's x, y values as a Python tuple (pygame likes it like that sometimes)
        """
        result = (self.x, self.y)
        return result

    def to_array(self) -> [int]:
        """
        Returns the Vector2's x, y values as a Python array (pygame likes it like that sometimes)
        """
        result = [self.x, self.y]
        return result

    def __add__(self, other:Vector2) -> Vector2:
        """
        Adds two Vector2's together. This overrides the + operator, so you can add them like v1 + v2
        """
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other:Vector2) -> Vector2:
        """
        Subtracts a Vector2 from another. This overrides the - operator, so you can use it like v1 - v2
        """
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other) -> Vector2:
        """
        Multiplies a Vector2 by either another Vector2 or a float. This overrides the * operator, so you can use it
        like v1 * v2 or v * f
        """
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        else:
            return Vector2(self.x * other, self.y * other)


class Rect:
    """
    A mathematical representation of a rectangle, or a 2-dimensional box, with a top-left corner (its position) and a
    size
    """
    def __init__(self, pos: Vector2, size: Vector2):
        self.pos = pos
        self.size = size

    @property
    def bottom_right(self) -> Vector2:
        """
        The Rect's bottom-right corner
        """
        return Vector2(self.right, self.bottom)

    @property
    def top_left(self) -> Vector2:
        """
        The Rect's top-left corner
        """
        return self.pos

    @property
    def left(self) -> float:
        """
        The x-value for the Rect's left edge
        """
        return self.pos.x

    @property
    def right(self) -> float:
        """
        The x-value for the Rect's right edge
        """
        return self.pos.x + self.size.x

    @property
    def top(self) -> float:
        """
        The y-value for the Rect's top edge
        """
        return self.pos.y

    @property
    def bottom(self) -> float:
        """
        The y-value for the Rect's bottom edge
        """
        return self.pos.y + self.size.y

    @property
    def horizontal_center(self) -> float:
        """
        The x-value for the Rect's horizontal center
        """
        return self.pos.x + self.size.x * 0.5

    @property
    def vertical_center(self) -> float:
        """
        The y-value for the Rect's vertical center
        """
        return self.pos.y + self.size.y * 0.5

    @property
    def center(self) -> Vector2:
        """
        The Rect's center
        """
        return Vector2(self.horizontal_center, self.vertical_center)

    def intersects(self, other: Rect) -> bool:
        """
        Returns true if the two Rects intersect (i.e. are colliding)
        """
        return self.left < other.right and self.right > other.left and \
               self.top < other.bottom and self.bottom > other.top

    def contains(self, other: Rect) -> bool:
        """
        Returns true if this Rect completely contains 'other', i.e., if Rect 'other' is completely inside it.
        """
        return other.right < self.right and other.left > self.left and \
               other.top > self.top and other.bottom < self.bottom


class Component:
    """
    A basic component in Pyleob
    """

    def __init__(self):
        self._active = True

    @property
    def active(self) -> bool:
        """
        Whether the component is active. It will be ignored by Game2D if it's not.
        """
        return self._active

    @active.setter
    def active(self, val: bool):
        self.set_active(val)

    def set_active(self, val: bool):
        """
        This exists as a method to have a virtual @active.setter
        """
        self._active = val


class Drawable(Component):
    """
    Abstract class that represents something that can be drawn on screen. Has a position, width and height.
    """

    def __init__(self, width: float, height: float):
        super(Drawable, self).__init__()
        self._pos = Vector2(0, 0)
        self._size = Vector2(width, height)

    @property
    def pos(self) -> Vector2:
        """
        The Drawable's position
        """
        return self._pos

    @pos.setter
    def pos(self, val):
        self._pos = val

    @property
    def size(self) -> Vector2:
        """
        The Drawable's size
        """
        return self._size

    @size.setter
    def size(self, val):
        self._size = val

    @abstractmethod
    def draw(self, screen):
        """
        Abstract. Draw the drawable. Needs to be implemented by the concrete implementation of the class, which will
        know what to actually draw.
        """
        pass

    def get_rect(self) -> Rect:
        """
        Gets the Rect representing this Drawable
        """
        return Rect(self.pos, self.size)

    def sort_key_y(self) -> float:
        """
        Returns the Drawable's position's y component for sorting purposes
        """
        return self.pos.y


class Rectangle(Drawable):
    """
    A Rectangle that can be drawn on screen. Has a position, size, and color.
    """

    def __init__(self, width: float, height: float, color):

        super(Rectangle, self).__init__(width, height)
        self.color = color

    def draw(self, screen):
        """
        Draw the drawable. Draws a Rectangle on its current position on the provided screen (pygame)
        """
        pos = self.pos
        size = self.size
        pygame.draw.rect(screen, self.color, [pos.x, pos.y, size.x, size.y])


class Sprite(Drawable):
    """
    A Sprite that can be drawn on screen. Has a position, size, and image.
    """

    def __init__(self, imagepath: str, width: float, height: float):
        super(Sprite, self).__init__(width, height)
        self.sourceImage = pygame.image.load(imagepath)
        self.image = pygame.transform.scale(self.sourceImage, (width, height))

    def draw(self, screen: pygame.display):
        """
        Draw the drawable. Draws the Sprite on its current position on the provided screen (pygame)
        """
        screen.blit(self.image, self.pos.to_tuple())


class Entity(Component):
    """
    An Entity is a Component that can receive updates from Game2D
    """

    @abstractmethod
    def update(self, elapsedtime: float, keys: dict):
        """
        Update the state of the Entity.

        :param elapsedtime: time since the last update
        :param keys: state of the keys
        """
        pass


class GameObject(Entity):
    """
    A GameObject - an Entity that owns/controls a Drawable and that can collide with other GameObjects.
    Collisions are calculated by Game2D based on the supplied collision_layer and the collisionMatrix configured in the
    Game2D implementation.
    """

    def __init__(self, drawable: Drawable, collision_layer: int = -1):
        super(GameObject, self).__init__()
        self.drawable = drawable
        self._collision_layer = collision_layer

    @property
    def collision_layer(self) -> int:
        """
        The collision layer this GameObject is assigned to
        """
        return self._collision_layer

    def get_collider(self) -> Rect:
        """
        Get this object's collision Rect
        """
        return self.drawable.get_rect()

    def set_active(self, val: bool):
        """
        Override this object's set_active to also propagate the active state to its drawable
        """
        super(GameObject, self).set_active(val)
        self.drawable.active = val

    @abstractmethod
    def update(self, elapsedtime: float, keys: dict):
        """
        Update the state of the GameObject

        :param elapsedtime: time since the last update
        :param keys: state of the keys
        """
        pass

    @abstractmethod
    def on_collision(self, other: GameObject):
        """
        Called when a collision is detected on this object. 'other' is the object it collided with. When a collision
        happens, this method is called for both objects.
        """
        pass


class Game2D:
    """
    The skeleton for a simple 2D game. This drives a simple game loop and handles pygame initialization, cleanup,
    drawing, updates and collision detection.
    """

    def __init__(self, gameName: str, screenSize: Vector2, collisionMatrix: []):
        """

        :param gameName: name of the game, shown as the window title
        :param screenSize: size of the game screen framebuffer, in pixels
        :param collisionMatrix: the collision matrix, as an array of ints with each int representing a line on the matrix. If the matrix is incomplete, it will be filled with zeroes.
        """

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
        """
        Adds a GameObject to the game. This takes care of adding it as an Entity and adding its Drawable as well.
        GameObjects added to the game will be updated, drawn and have collision detection handled automatically.
        """
        self.add_entity(game_object)
        self.add_drawable(game_object.drawable)
        self.add_game_object_to_collision_layer(game_object)

    def remove_game_object(self, game_object: GameObject):
        """
        Removes a GameObject from the game. This will not remove the GameObject right away but, instead, deactivate
        the GameObject and remove it at the end of frame, so it's safe to call this while iterating over lists of
        GameObjects.
        This will remove it as an Entity and also remove its Drawable from the game as well.
        """
        game_object.active = False
        self.game_objects_to_remove.append(game_object)

    def remove_game_object_now(self, game_object: GameObject):
        """
        Instantly removes a GameObject from the game. This will remove it as an Entity and also remove its Drawable
        from the game as well.
        """
        self.remove_drawable(game_object.drawable)
        self.remove_entity(game_object)
        self.remove_game_object_from_collision_layer(game_object)

    def add_entity(self, entity: Entity):
        """
        Add an Entity to the game. Entities added to the game will be updated automatically (the 'update' method will
        be called on them).
        """
        self.entities.append(entity)

    def remove_entity(self, entity: Entity):
        """
        Remove an Entity from the game.
        """
        if entity in self.entities:
            self.entities.remove(entity)

    def add_drawable(self, drawable: Drawable):
        """
        Add a Drawable to the game. Drawables added to the game are drawn automatically (the 'draw' method will be
        called on them).
        """
        self.drawables.append(drawable)

    def remove_drawable(self, drawable: Drawable):
        """
        Remove a Drawable from the game.
        """
        if drawable in self.drawables:
            self.drawables.remove(drawable)

    def remove_game_object_from_collision_layer(self, game_object: GameObject):
        """
        Removes a GameObject from the collision layer it's assigned to. You should never need to call this directly.
        """
        if game_object.collision_layer >= 0:
            if game_object in self.entities_by_collision_layer[game_object.collision_layer]:
                self.entities_by_collision_layer[game_object.collision_layer].remove(game_object)

    def add_game_object_to_collision_layer(self, game_object: GameObject):
        """
        Adds a GameObject to the collision layer it's assigned to. You should never need to call this directly.
        """
        if game_object.collision_layer >= 0:
            self.__add_game_object_to_collision_layer(game_object, game_object.collision_layer)

    def __add_game_object_to_collision_layer(self, game_object: GameObject, layer: int):
        """
        Adds a GameObject to an arbitrary collision layer. You should definitely not call this directly.
        """
        if layer not in self.entities_by_collision_layer:
            self.entities_by_collision_layer[layer] = []

        self.entities_by_collision_layer[layer].append(game_object)

    def get_mask_value_for_layer(self, layer: int) -> int:
        """
        Transforms the layer number into the mask value for that layer
        """
        return 1 << layer

    def collision_enabled_between_layers(self, layer1:int, layer2:int) -> bool:
        """
        Returns true if collision is enabled between layer1 and layer2. It does so by selecting the row in the matrix
        for layer1, then bitwise-and-ing it with the bit for layer 2. If the result is zero, it means that there was
        a zero in that bit, meaning that collision between the two layers was disabled.
        """
        return self.collision_matrix[layer1] & self.get_mask_value_for_layer(layer2) != 0

    def get_entities_by_collision_layer(self, layer:int) -> [GameObject]:
        """
        Gets all entities by collision layer. You shouldn't care.
        """
        if layer in self.entities_by_collision_layer.keys():
            return self.entities_by_collision_layer[layer]
        else:
            return []

    def __main_update(self, elapsedtime: float):
        """
        Game2D's main update loop handler. This dispatches early_update, late_update, all the Entity updates, collision
        detection, and captures keyboard state for everyone.
        """
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
        """
        Called before anything else happens in the frame
        """
        pass

    def calculate_collisions(self):
        """
        Calculates all collisions between objects
        """
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
        """
        Called after all Entities have been updated and all collisions have been resolved.
        """
        pass

    def __main_draw(self):
        """
        This drives drawing of the screen. It will sort all Drawables and call draw on them.
        """
        self.screen.fill(self.backgroundColor)

        self.draw()

        self.drawables.sort(key=Drawable.sort_key_y)
        for drawable in self.drawables:
            if drawable.active:
                drawable.draw(self.screen)

        pygame.display.flip()

    @abstractmethod
    def draw(self):
        """
        In case your game needs to draw something
        """
        pass

    def run(self):
        """
        Run the main game
        """
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

