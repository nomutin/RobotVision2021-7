"""RobotVision2021-7

  腕立て伏せのフォームが悪かったら本気で怒号を飛ばすアプリ

TODO:
    * 怒号を録音する

"""

import statistics

import cv2
import numpy as np

from constants import *
from helpers import BodyCoordinates, NotEnoughAreasError


def get_background():
    """背景を撮影する関数

    画面からはけた状態のスクリーンショットをsキー押下で撮影する

    Returns:
        frame(np.ndarray): スクリーンショットした画面フレーム
    """

    cap = cv2.VideoCapture(0)

    while cv2.waitKey(1) != ord("s"):
        cv2.imshow("press s key to take a background photo", cap.read()[1])
    else:
        _, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        return frame


def create_fgmask(bg, frame, kernel_size):
    """背景差分をとったフレーム出力を行う関数

    Args:
        bg(np.ndarray):     差分をとるための背景画像
        frame(np.ndarray):  背景と比較する毎フレーム
        kernel_size(int):   体のラインを強調するための膨張・収縮を行うカーネルサイズ

    Returns:
        fgmask(np.ndarray): 背景との差分(2値画像)

    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    fgbg.apply(bg)
    fgmask = fgbg.apply(frame)
    fgmask = cv2.dilate(fgmask, kernel)
    fgmask = cv2.erode(fgmask, kernel)
    return fgmask


def get_coordinates(bool_image, body):
    nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(bool_image)

    if nlabels <= 2:
        raise NotEnoughAreasError

    first_idx, second_idx, *_ = stats[:, 4].argsort()[-3:-1]
    x0 = min(stats[first_idx][0], stats[second_idx][0])
    y0 = min(stats[first_idx][1], stats[second_idx][1])
    w = max(stats[first_idx][2], stats[second_idx][2])
    h = max(stats[first_idx][3], stats[second_idx][3])
    x1 = x0 + w
    y1 = y0 + h

    body.head.x = int(statistics.median(np.append(np.nonzero(labels[y0, x0:x1])[0] + x0, body.head.x)))
    body.head.y = y0

    if body.head.x < (x0 + (x1 - x0) * 0.5):
        body.foot.x = x1
    else:
        body.foot.x = x0
    body.foot.y = y1


def main():
    bg = get_background()

    body = BodyCoordinates()
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()

        fgmask = create_fgmask(bg, frame, 8)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        get_coordinates(bool_image=fgmask, body=body)

        body.draw(15, src, waist=False)

        cv2.imshow('mask', src)
        cv2.imshow("flow", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
