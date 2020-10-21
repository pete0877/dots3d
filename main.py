import math
import random

import numpy as np
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

BLOB_SIZE = 1500
BLOB_POINTS = 2000
BLOB_DISTANCE = 2 * BLOB_SIZE

CAMERA_DISTANCE = 1 * BLOB_SIZE

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dots")


def get_projectection(point):
    x, y, z, _ = point
    x_proj = int(x * (CAMERA_DISTANCE / z) + (SCREEN_WIDTH / 2))
    y_proj = int(y * (CAMERA_DISTANCE / z) + (SCREEN_HEIGHT / 2))
    return (x_proj, y_proj)


def get_color(point):
    _, _, z, color_base = point
    distance = (z - BLOB_DISTANCE) / BLOB_SIZE  # 0 - close, 1 - far
    # Color brightness will be from 0 .. 155 based on the distance:
    brightness = int(155 * (1 - distance))
    brightness = min(155, brightness)
    brightness = max(0, brightness)
    return (
        color_base[0] + brightness,
        color_base[1] + brightness,
        color_base[2] + brightness,
    )


def get_rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def rotate_point(point, rotation_matrix):
    x, y, z, base_color = point
    shift_z = BLOB_DISTANCE + (BLOB_SIZE / 2)
    point_normalized = (x, y, z - shift_z)
    point_rotated = np.dot(rotation_matrix, point_normalized)
    x, y, z = point_rotated
    return x, y, z + shift_z, base_color


def get_size(point):
    x, y, z, _ = point
    distance = (z - BLOB_DISTANCE) / BLOB_SIZE  # 0 - close, 1 - far
    radius = int(1 + (3 * (1 - distance)))
    return radius


def get_random_color_base():
    # Returns random RBB color (r, g, b) where r, g and b can be anywhere between 25 and 100
    result = (
        25 + random.randint(0, 75),
        25 + random.randint(0, 75),
        25 + random.randint(0, 75),
    )
    return result


points = [
    (
        int(random.randint(0, BLOB_SIZE) - (BLOB_SIZE / 2)),
        int(random.randint(0, BLOB_SIZE) - (BLOB_SIZE / 2)),
        int(random.randint(0, BLOB_SIZE) + BLOB_DISTANCE),
        get_random_color_base(),
    )
    for _ in range(0, BLOB_POINTS)
]

running = True

rotation_vector = [10, 10, 10]
rotation_speed = 0.01

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                rotation_vector[2] += -10
            if event.key == pygame.K_RIGHT:
                rotation_vector[2] += 10
            if event.key == pygame.K_UP:
                rotation_speed += 0.005
            if event.key == pygame.K_DOWN:
                rotation_speed += -0.005

    screen.fill((0, 0, 0))
    rot_mtx = get_rotation_matrix(rotation_vector, rotation_speed)

    for point in points:
        screen_position = get_projectection(point)
        color = get_color(point)
        size = get_size(point)
        try:
            pygame.draw.circle(screen, color, screen_position, size)
        except Exception as error:
            raise Exception(f"DRAW ERROR: color: {color}, screen_position: {screen_position}, size: {size}", error)

    pygame.display.update()

    points = [rotate_point(point, rot_mtx) for point in points]

    pygame.time.delay(5)

pygame.quit()
