#!/usr/bin/env python

import cv2, json, pprint, time
import numpy as np
from pupil_apriltags import Detector
from math import atan2, cos, pi, sin
# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

from wow_tag import WowTag, raw_tags_to_wow_tags
from config_loader import ConfigLoader
from game_screen import GameScreen

# Customize the level and controller.
from levels import FirstGameLevel
from control_image_generator import ControlImageGenerator
from controllers import SmoothController1
control_image_generator = ControlImageGenerator(SmoothController1())

if __name__ == "__main__":

    cfg = ConfigLoader.get()

    game_screen = GameScreen(cfg.output_width, cfg.output_height)

    level = FirstGameLevel(cfg.output_width, cfg.output_height)

    apriltag_detector = Detector(
       families="tag36h11",
       nthreads=5,
       quad_decimate=1.0,
       quad_sigma=0.0,
       refine_edges=1,
       decode_sharpening=0.25,
       debug=0
    )

    output_corners = [[0, 0], [cfg.output_width-1, 0], [cfg.output_width-1, cfg.output_height-1], [0, cfg.output_height-1]]
    homography, status = cv2.findHomography(np.array(cfg.screen_corners), np.array(output_corners))

    if cfg.show_input:
        input_window_name = "Input"
        cv2.namedWindow(input_window_name, cv2.WINDOW_NORMAL)
    #pp = pprint.PrettyPrinter(indent=4)

    cap = cv2.VideoCapture(cfg.video_channel)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.input_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.input_height)

    while True:

        start_time = time.time()

        ret, raw_image = cap.read()
        if not ret:
            print('Cannot read video.')
            break

        # Undistort the raw image.  This also has to be done in picker.py so that
        # the picked corners used to build the homography matrix are consistent.
        h, w = raw_image.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cfg.calib_K, cfg.calib_D, (w,h), 1, (w,h))
        undistorted = cv2.undistort(raw_image, cfg.calib_K, cfg.calib_D, None, newcameramtx)

        # Warp the raw image.
        warped_image = cv2.warpPerspective(undistorted, homography, (cfg.output_width, cfg.output_height))
        gray_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

        raw_tags = apriltag_detector.detect(gray_image)

        wow_tags = raw_tags_to_wow_tags(raw_tags)

        game_screen.handle_events()
        manual_movement = game_screen.get_movement()

        # The level is responsibility for determine the application's evolution.
        # This is communicated in a dictionary of journeys for tags (i.e. robots)
        # and a list of sprites which are graphical elements.  They are not
        # robots, but could be drawn adjacent to a robot.
        journey_dict, sprites = level.get_journeys_and_sprites(manual_movement, wow_tags)

        control_curves = control_image_generator.generate(wow_tags, journey_dict)

        game_screen.update(wow_tags, control_curves, sprites)

        if cfg.show_input:
            resize_divisor = 1
            if resize_divisor > 1:
                cv2.resizeWindow(input_window_name, warped_image.shape[1]//resize_divisor, warped_image.shape[0]//resize_divisor)
            cv2.imshow(input_window_name, warped_image)
            cv2.waitKey(10)

        elapsed = time.time() - start_time
        #print(f"loop elapsed time: {elapsed}")

    cap.release()