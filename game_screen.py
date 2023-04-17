import os
import pygame as pg
from math import cos, pi, sin

POSE_RADIUS = 65

class GameScreen:
    def __init__(self, width, height):

        #os.environ['SDL_VIDEO_WINDOW_POS'] = "1920,0"
        pg.init()
        self.screen = pg.display.set_mode((width, height), flags=pg.SCALED)
        #pg.display.toggle_fullscreen()
        self.terminate = False

        self.debug_level = 1
        self.MAX_DEBUG_LEVEL = 2
        self.font = pg.freetype.SysFont('arial', 18)

    def handle_events(self):
        self.movement = ""

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.terminate = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_d:
                    if self.debug_level < self.MAX_DEBUG_LEVEL:
                        self.debug_level += 1
                    else:
                        self.debug_level = 0

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE] or keys[pg.K_q]:
            self.terminate = True
        if keys[pg.K_UP]:
            self.movement = "forward"
        if keys[pg.K_LEFT]:
            self.movement = "left"
        if keys[pg.K_RIGHT]:
            self.movement = "right"
            
        print(self.movement)

    def get_movement(self):
        return self.movement

    def update(self, tags, guide_positions):
        # Fill the screen to wipe away anything from last frame
        self.screen.fill("black")

        if self.debug_level > 0:
            for tag in tags:
                centre = pg.Vector2(tag['x'], tag['y'])
                unit_vector = pg.Vector2(cos(tag['angle']), sin(tag['angle']))

                pg.draw.circle(self.screen, "purple", centre, POSE_RADIUS, width=2)
                pg.draw.line(self.screen, "purple", centre + 0.7 * POSE_RADIUS * unit_vector, centre + POSE_RADIUS * unit_vector, width=3)

                if self.debug_level == 1:
                    text_surface, rect = self.font.render(str(tag['id']), "purple")
                elif self.debug_level == 2:
                    newline = '\n'
                    text_surface, rect = self.font.render(f"id: {tag['id']}{newline}pos: {tag['x'], tag['y']}{newline}angle: {int(tag['angle']*180/pi)}", "purple")

                text_position = centre + 1.2 * POSE_RADIUS * unit_vector - 0.5 * pg.Vector2(rect.width, rect.height)
                self.screen.blit(text_surface, text_position)

        for pos in guide_positions:
            centre = pg.Vector2(pos[0], pos[1])
            pg.draw.circle(self.screen, "white", centre, 10)

        # flip() the display to put your work on screen
        pg.display.flip()

        # TBD: Update self.delta_time to get framerate- independent physics?

        if self.terminate:
            self.close()

    def close(self):
        pg.display.quit()
        pg.quit()