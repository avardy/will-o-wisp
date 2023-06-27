#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":

    tg_calib_count = np.load("tg_calib_count.npy")
    tg_calib_x = np.load("tg_calib_x.npy")
    tg_calib_y = np.load("tg_calib_y.npy")
    tg_calib_count_interp = np.load("tg_calib_count_interp.npy")
    tg_calib_x_interp = np.load("tg_calib_x_interp.npy")
    tg_calib_y_interp = np.load("tg_calib_y_interp.npy")
    tg_calib_x_filtered = np.load("tg_calib_x_filtered.npy")
    tg_calib_y_filtered = np.load("tg_calib_y_filtered.npy")

    #fig, axs = plt.subplots(1, 1)
    #axs.imshow(tg_calib_count)
    fig, axs = plt.subplots(3, 3)
    axs[0, 0].imshow(tg_calib_count)
    axs[1, 0].imshow(tg_calib_x)
    axs[2, 0].imshow(tg_calib_y)
    axs[0, 1].imshow(tg_calib_count_interp)
    axs[1, 1].imshow(tg_calib_x_interp)
    axs[2, 1].imshow(tg_calib_y_interp)
    axs[1, 2].imshow(tg_calib_x_filtered)
    axs[2, 2].imshow(tg_calib_y_filtered)
    plt.show()