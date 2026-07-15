#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from config_loader import ConfigLoader

if __name__ == "__main__":

    cfg = ConfigLoader.get()

    directory = f"tg_calib"

    tg_calib_count = np.load(f"{directory}/tg_calib_count.npy")
    tg_calib_x = np.load(f"{directory}/tg_calib_x.npy")
    tg_calib_y = np.load(f"{directory}/tg_calib_y.npy")
    tg_calib_count_interp = np.load(f"{directory}/tg_calib_count_interp.npy")
    tg_calib_x_interp = np.load(f"{directory}/tg_calib_x_interp.npy")
    tg_calib_y_interp = np.load(f"{directory}/tg_calib_y_interp.npy")
    tg_calib_x_filtered = np.load(f"{directory}/tg_calib_x_filtered.npy")
    tg_calib_y_filtered = np.load(f"{directory}/tg_calib_y_filtered.npy")

    '''
    tg_calib_x_filtered = signal.medfilt2d(tg_calib_x_interp, kernel_size=(5,21))
    tg_calib_y_filtered = signal.medfilt2d(tg_calib_y_interp, kernel_size=9)
    np.save("tg_calib_x_filtered", tg_calib_x_filtered)
    np.save("tg_calib_y_filtered", tg_calib_y_filtered)
    '''

    #fig, axs = plt.subplots(1, 1)
    #axs.imshow(tg_calib_count)
    fig, axs = plt.subplots(3, 3)
    axs[0, 0].imshow(tg_calib_count)
    axs[0, 0].set_title('tg_calib_count')
    axs[1, 0].imshow(tg_calib_x)
    axs[1, 0].set_title('tg_calib_x')
    axs[2, 0].imshow(tg_calib_y)
    axs[2, 0].set_title('tg_calib_y')
    axs[0, 1].imshow(tg_calib_count_interp)
    axs[0, 1].set_title('tg_calib_count_interp')
    axs[1, 1].imshow(tg_calib_x_interp)
    axs[1, 1].set_title('tg_calib_x_interp')
    axs[2, 1].imshow(tg_calib_y_interp)
    axs[2, 1].set_title('tg_calib_y_interp')
    axs[1, 2].imshow(tg_calib_x_filtered)
    axs[1, 2].set_title('tg_calib_x_filtered')
    axs[2, 2].imshow(tg_calib_y_filtered)
    axs[2, 2].set_title('tg_calib_y_filtered')
    plt.show()
