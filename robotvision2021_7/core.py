"""RobotVision2021-7

  腕立て伏せのフォームが悪かったら本気で怒号を飛ばすアプリ

TODO:
    * 怒号を録音する

"""

import time

import cv2
import numpy as np

from constants import *
from helpers import BodyCoordinates, NotEnoughAreasError, Sound


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

        except NotEnoughAreasError:
            pass

        if body.x_y_ratio > STAND_BY_TH_X_Y_RATIO and frame.size * 0.05 < body.area < frame.size * 0.5:
            break

        body.draw(src)
        cv2.imshow("Waiting until in the push-up position", src)

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
    hsv_mask = cv2.medianBlur(fgmask, ksize=5)
    hsv_mask = cv2.erode(hsv_mask, kernel)
    hsv_mask = cv2.dilate(hsv_mask, kernel)
    return hsv_mask


def main():
    bg = get_background()
    body = BodyCoordinates()
    cap = cv2.VideoCapture(0)

    stand_by(bg, body)

    start_time = time.time()
    displacements = []
    sound = Sound()
    length = 0
    low_timer = 0
    max_h = body.foot.y - body.head.y

    while True:
        _, frame = cap.read()
        fgmask = create_fgmask(bg, frame, 8)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
        try:
            body.get_coordinates(fgmask)

        except NotEnoughAreasError:
            pass

        # if body.waist.y - (body.head.y + body.foot.y) / 2 > WAIST_TH:
        #     print('下')
        # elif body.waist.y - (body.head.y + body.foot.y) / 2 < -WAIST_TH:
        #     print('上')
        # else:
        #     print('ok')

        displacements.append(body.foot.y - body.head.y)
        if len(displacements) >= 1500:
            displacements.pop(0)

        if time.time() - start_time > VELOCITY_MEASURE_TIME:
            if length == 0:
                length = len(displacements)

            v = abs(displacements[-1] - displacements[-length])

            # if v > v_th:
            #     sound.play('voice/test.wav')

        if max_h * 0.4 > displacements[-1]:
            if low_timer == 0:
                low_timer = time.time()
                print('スタート')

        else:
            # low_timer.stop
            if (time.time() - low_timer) < 3 and low_timer != 0:
                print('早い')
            low_timer = 0

        print(low_timer)
        body.draw(image=src)
        body.draw(image=frame)

        cv2.imshow('mask', src)
        cv2.imshow("flow", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
