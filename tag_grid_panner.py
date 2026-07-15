"""
Pans a grid of AprilTags across the screen.
"""

import cv2, os, time
import pygame as pg
import numpy as np
from pygame.math import Vector2
from math import cos, floor, pi, sin
from random import random
from wow_tag import WowTag

class TagGridPanner:
    def __init__(self, width, height, tag_size, delta, fullscreen):
        self.width = width
        self.height = height
        self.tag_size = tag_size
        self.delta = delta
        print(f"width: {width}, height: {height}, tag_size: {tag_size}, delta: {delta}")

        os.environ['SDL_VIDEO_WINDOW_POS'] = "2200,0"
        pg.init()
        self.screen = pg.display.set_mode((width, height), flags=pg.SCALED, vsync=1)
        if fullscreen:
            pg.display.toggle_fullscreen()
        self.terminate = False

        self.tag_image_dict = {}

    def load_tag_image(self, id):
        tag_image = pg.image.load(f"tag36h11/tag36_11_{id:05}.png").convert_alpha()

        # Upsample this tiny image.
        self.tag_image_dict[id] = pg.transform.scale(tag_image, (self.tag_size, self.tag_size))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.terminate = True
        # Handle key presses (key could be held down).
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE] or keys[pg.K_q]:
            self.terminate = True
        if keys[pg.K_f]:
            pg.display.toggle_fullscreen()

    def update(self, wow_tags):
        # Fill the screen to wipe away anything from last frame
        self.screen.fill("black")

        for wow_tag in wow_tags:
            if wow_tag.id not in self.tag_image_dict:
                self.load_tag_image(wow_tag.id)

            tag_image = self.tag_image_dict[wow_tag.id]

            tag_image_rect = tag_image.get_rect()
            topleft = Vector2(wow_tag.x - tag_image_rect.width/2, wow_tag.y - tag_image_rect.height/2)
            rotated_image = pg.transform.rotate(tag_image, (180/pi)*wow_tag.angle)
            new_rect = rotated_image.get_rect(center = tag_image.get_rect(topleft = topleft).center)

            self.screen.blit(rotated_image, new_rect)

            # Check that the image drawn above is centred correctly.
            #pg.draw.circle(self.screen, "green", Vector2(wow_tag.x, wow_tag.y), 10)

        # flip() the display to put your work on screen
        pg.display.flip()
        
        # Force pygame to process all events to ensure display update is processed
        pg.event.pump()

        if self.terminate:
            self.close()

    def close(self):
        pg.display.quit()
        pg.quit()

    def compute_suitable_grid_size(self, minimum_gap=30):
        # Determine the size of the grid of tags by considering pairs of factors of the 
        # image width and height.  First compute those factors.
        width_factors = []
        height_factors = []
        for i in range(2, self.width - 1):
            if self.width % i == 0:
                width_factors.append(i)
        for i in range(2, self.height - 1):
            if self.height % i == 0:
                height_factors.append(i)
        #print(width_factors)
        #print(height_factors)
        
        # Choose increasing width factors.  For each one, select the closest
        # height factor that approximately matches the image's aspect ratio.
        suitable_m_n_pairs = []
        ideal_aspect_ratio = self.width / self.height
        for width_factor in width_factors:
            best_height_factor = None
            lowest_diff = None
            for height_factor in height_factors:
                aspect_ratio = (width_factor - 1) / (height_factor - 1)
                if lowest_diff is None or abs(ideal_aspect_ratio - aspect_ratio) < lowest_diff:
                    best_height_factor = height_factor
                    lowest_diff = abs(ideal_aspect_ratio - aspect_ratio)

            m = width_factor - 1
            n = best_height_factor - 1
            #print(f"potential m, n: {m}, {n}")
            assert (self.width % (m + 1) == 0), "width must be divisible by m + 1"
            assert (self.height % (n + 1) == 0), "height must be divisible by n + 1"

            # Compute what the horizontal gap (gx) between the tags should be to satisfy 
            # (m + 1)(tag_size + gx) = width.  Then similarly for the vertical gap (gy).
            gx = self.width // (m + 1) - self.tag_size
            gy = self.height // (n + 1) - self.tag_size

            # Is this pair of m, n suitable?
            if gx >= minimum_gap/2 and gy >= minimum_gap/2:
                suitable_m_n_pairs.append((m, n))
            #    print(f"suitable gx, gy: {gx}, {gy}")
            #else:
            #    print(f"unsuitable gx, gy: {gx}, {gy}")

        # Choose the last (and largest) suitable pair of m and n.
        #print(f"suitable (m, n) pairs: {suitable_m_n_pairs}")
        m, n = suitable_m_n_pairs[-1]
        print(f"m, n: {m}, {n}")
        return m, n

    def pan_tags(self, callback):
        m, n = self.compute_suitable_grid_size()
        gx = self.width // (m + 1) - self.tag_size
        gy = self.height // (n + 1) - self.tag_size

        tags = []
        id = 0
        for j in range(n):
            for i in range(m):
                x = int((self.tag_size + gx)//2 + i * (self.tag_size + gx))
                y = int((self.tag_size + gy)//2 + j * (self.tag_size + gy))
                tags.append(WowTag(id, x, y, 0))
                id += 1

        # Choosing a value at or above 2pi means we are not stepping through angles.
        delta_angle = 10*pi
        delta_x = self.delta
        delta_y = self.delta
        min_x = (self.tag_size + gx)//2
        max_x = self.width - min_x
        max_y = self.height - (self.tag_size + gy)//2
        moving_right = True

        while not self.terminate:
            self.handle_events()
            self.update(tags)
            callback(tags)

            left_tag = tags[0]
            right_tag = tags[m - 1]
            bottom_tag = tags[-1]
            if left_tag.angle + delta_angle < 2*pi:
                tags = [WowTag(tag.id, tag.x, tag.y, tag.angle + delta_angle) for tag in tags]
            elif moving_right and right_tag.x + delta_x <= max_x:
                tags = [WowTag(tag.id, tag.x + delta_x, tag.y, 0) for tag in tags]
            elif not moving_right and left_tag.x - delta_x >= min_x:
                tags = [WowTag(tag.id, tag.x - delta_x, tag.y, 0) for tag in tags]
            elif bottom_tag.y + delta_y <= max_y:
                tags = [WowTag(tag.id, tag.x, tag.y + delta_y, 0) for tag in tags]
                moving_right = not moving_right
            else:
                self.terminate = True


if __name__ == "__main__":
    width = 960
    height = 540
    tag_size = 50
    delta = 12

    # This image is just a debugging tool to show the image positions
    # covered over time by the tags below.
    coverage_image = np.zeros((height, width))
    cv2.imshow("Coverage Image", coverage_image.astype(np.uint8))

    panner = TagGridPanner(width, height, tag_size, delta, False)

    def callback(tags):
        for tag in tags:
            coverage_image[tag.y, tag.x] += 100
        cv2.imshow("Coverage Image", coverage_image.astype(np.uint8))
        cv2.waitKey(1)

    panner.pan_tags(callback)

    cv2.imwrite("coverage.png", coverage_image.astype(np.uint8))
    cv2.waitKey(0)
