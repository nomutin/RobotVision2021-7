"""RobotVision2021-7

  腕立て伏せのフォームが悪かったら本気で怒号を飛ばすアプリ

  TODO:
    * 声の迫力足りない
    * 褒める音声も入れる
    * 『おい！！』も再生するようにする

"""


import sys

import cv2
import numpy as np

from constants import *
from helpers import (
    BodyCoordinates,
    NotEnoughAreasError,
    SoundPlayer,
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

        if cv2.waitKey(1) == ord("q"):
            sys.exit()

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
        body(BodyCoordinates): 体の座標情報

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

    else:
        sys.exit()

    cap.release()
    cv2.destroyAllWindows()
    body.get_max_body_height()


def create_fgmask(background, frame, kernel_size):
    """背景差分をとったフレーム出力を行う関数

    Args:
        background(np.ndarray): 差分をとるための背景画像
        frame(np.ndarray):  背景と比較する毎フレーム
        kernel_size(int): 体のラインを強調するための膨張・収縮を行うカーネルサイズ

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


def pose_judgement(body, timer, player):
    """姿勢の判定を行う関数

    1. 体の高さがスタンバイ時の高さ(body.max_body_height)のLOW_FORM_RATIO倍になったとき，
       低い姿勢になったと判断する
    2. 低い姿勢になった時間がLOW_FORM_TIMEに満たなかった場合，怒号を飛ばす
    3. 速度を測定する
    4. 速度がV_THより早い場合，怒号を飛ばす
    5. 腰の高さがしきい値より高いor低い場合，怒号を飛ばす

    Args:
        body(BodyCoordinates): 体の座標情報
        timer(Timer): タイマー
        player(SoundPlayer): 音声プレーヤー

    Returns:
        None

    """

    # 1.
    if body.max_body_height * LOW_FORM_RATIO > body.displacements[-1]:
        timer.lap_timer_start()

    # 2.
    else:
        if timer.current_lap_time < LOW_FORM_TIME and timer.lap_time != 0:
            player.play('bear')
        timer.lap_timer_reset()

    # 3.
    if timer.current_time > VELOCITY_MEASURE_TIME:
        if body.fps == 0:
            body.fps = len(body.displacements)

        v = abs(body.displacements[-1] - body.displacements[-body.fps])

        # 4.
        if v > V_TH:
            player.play('fast')

    # 5.
    if body.waist.y - (body.head.y + body.foot.y) / 2 > WAIST_TH:
        player.play('low')

    elif body.waist.y - (body.head.y + body.foot.y) / 2 < -WAIST_TH:
        player.play('high')


def main():
    # 背景画像を撮影
    bg = get_background()
    body = BodyCoordinates()

    # 腕立ての体制になるまでスタンバイ
    stand_by(background=bg, body=body)

    timer = Timer()
    timer.start()
    sound_player = SoundPlayer()
    cap = cv2.VideoCapture(0)

    while cv2.waitKey(1) != ord("q"):
        _, frame = cap.read()
        fgmask = create_fgmask(background=bg, frame=frame, kernel_size=8)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        # 体の各座標を取得
        try:
            body.get_coordinates(fgmask)

        except NotEnoughAreasError:
            pass

        body.get_displacements()

        # 姿勢を判定
        pose_judgement(body=body, timer=timer, player=sound_player)

        # 図形の描画
        body.draw(image=src)
        body.draw(image=frame)
        cv2.imshow('mask', src)
        cv2.imshow("flow", frame)

    else:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

