"""RobotVision2021-7

  腕立て伏せのフォームが悪かったら本気で怒号を飛ばすアプリ

TODO:
    * 怒号を録音する

"""

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


def stand_by(bg, body):
    cap = cv2.VideoCapture(0)

    while cv2.waitKey(1) != ord("q"):
        _, frame = cap.read()
        fgmask = create_fgmask(bg, frame, 8)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        try:
            body.get_coordinates(fgmask)

            if body.x_y_ratio > STAND_BY_TH_X_Y_RATIO and body.area > STAND_BY_TH_AREA:
                break

            body.draw(src)
            cv2.imshow("Waiting until in the push-up position", src)

        except NotEnoughAreasError:
            continue

    cap.release()
    cv2.destroyAllWindows()


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


def main():
    bg = get_background()

    body = BodyCoordinates()
    stand_by(bg, body)
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()

        fgmask = create_fgmask(bg, frame, 8)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        body.get_coordinates(fgmask)

        cv2.imshow('mask', src)
        cv2.imshow("flow", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
