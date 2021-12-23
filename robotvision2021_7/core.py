"""RobotVision2021-7

  腕立て伏せのフォームが悪かったら本気で怒号を飛ばすアプリ

TODO:
    * 怒号を録音する

"""


import cv2
import numpy as np

from constants import *
from helpers import (
    BodyCoordinates,
    NotEnoughAreasError,
    Sound,
    Timer
)


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


def stand_by(background, body):
    """腕立て伏せの体制になるまでスタンバイする関数

    体の輪郭の縦横比がSTAND_BY_TH_X_Y_RATIO以上かつ
    輪郭の面積の割合がSTAND_BY_AREA_MIN以上STAND_BY_AREA_MAXのときスタンバイ終了とする
    また，スタンバイ終了時にbody.max_body_heightを設定しておく

    Args:
        background(np.ndarray): 背景画像(カラー画像)
        body(BodyCoordinates): BodyCoordinates()

    Returns:
        None

    """
    cap = cv2.VideoCapture(0)

    while cv2.waitKey(1) != ord("q"):
        _, frame = cap.read()
        fgmask = create_fgmask(background, frame, 8)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        try:
            body.get_coordinates(fgmask)

        except NotEnoughAreasError:
            pass

        if body.x_y_ratio > STAND_BY_TH_X_Y_RATIO and \
                frame.size * STAND_BY_AREA_MIN < body.area < frame.size * STAND_BY_AREA_MAX:
            break

        body.draw(src)
        cv2.imshow("Waiting until in the push-up position", src)

    cap.release()
    cv2.destroyAllWindows()
    body.get_max_body_height()


def create_fgmask(background, frame, kernel_size):
    """背景差分をとったフレーム出力を行う関数

    Args:
        background(np.ndarray):     差分をとるための背景画像
        frame(np.ndarray):  背景と比較する毎フレーム
        kernel_size(int):   体のラインを強調するための膨張・収縮を行うカーネルサイズ

    Returns:
        fgmask(np.ndarray): 背景との差分(2値画像)

    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    fgbg.apply(background)
    fgmask = fgbg.apply(frame)
    hsv_mask = cv2.medianBlur(fgmask, ksize=5)
    hsv_mask = cv2.erode(hsv_mask, kernel)
    hsv_mask = cv2.dilate(hsv_mask, kernel)
    return hsv_mask


def pose_judgement(body, timer):
    if body.max_body_height * LOW_FORM_RATIO > body.displacements[-1]:
        timer.lap_timer_start()
        print('低姿勢 ', end='')

    else:
        if timer.current_lap_time < LOW_FORM_TIME and timer.lap_time != 0:
            print('上げるの早い', end='')
        timer.lap_timer_reset()

    if timer.current_time > VELOCITY_MEASURE_TIME:
        if body.length_until_v_measure_time == 0:
            body.length_until_v_measure_time = len(body.displacements)

        v = abs(body.displacements[-1] - body.displacements[-body.length_until_v_measure_time])
        if v > V_TH:
            print('速度:早 ', end='')

    if body.waist.y - (body.head.y + body.foot.y) / 2 > WAIST_TH:
        print('腰:下 ', end='')
    elif body.waist.y - (body.head.y + body.foot.y) / 2 < -WAIST_TH:
        print('腰:上 ', end='')

    print('')


def main():
    bg = get_background()
    body = BodyCoordinates()
    cap = cv2.VideoCapture(0)

    stand_by(background=bg, body=body)

    timer = Timer()
    timer.start()

    while True:
        _, frame = cap.read()
        fgmask = create_fgmask(bg, frame, 8)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        try:
            body.get_coordinates(fgmask)

        except NotEnoughAreasError:
            pass

        body.get_body_height_displacements()
        pose_judgement(body, timer)

        body.draw(image=src)
        body.draw(image=frame)

        cv2.imshow('mask', src)
        cv2.imshow("flow", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # main()

    import simpleaudio

    wav_obj = simpleaudio.WaveObject.from_wave_file("voice/test.wav")
    play_obj = wav_obj.play()
    play_obj.wait_done()
