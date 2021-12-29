# 補助クラス

import dataclasses
import time
import typing

import cv2
import numpy as np
import simpleaudio

from constants import *


@dataclasses.dataclass
class Coordinate:
    """座標を管理するクラス

    x・yが代入されたとき，変化量がthを上回る場合，変化量を(1-mom)倍に抑えるようにする
        -> 座標がピョンピョン跳ぶのを防ぐ

    """

    x: int
    y: int
    th: int
    mom: float

    def __setattr__(self, key, value):
        try:
            if abs(self.__getattribute__(key) - value) >= self.th:
                super().__setattr__(key, int(self.__getattribute__(key) * self.mom + value * (1 - self.mom)))
            else:
                super().__setattr__(key, value)

        except AttributeError:
            super().__setattr__(key, value)


class BodyCoordinates:
    # 体の座標を管理するクラス

    def __init__(self):
        self.head = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)
        self.foot = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)
        self.waist = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)

        # スタンバイ時の体の高さを格納する
        self.max_body_height: int = 0

        # 速度判定のためにフレームごとの体の高さを保存する
        self.displacements: typing.List[int] = []

        # fps
        self.fps: int = 0

    @property
    def x_y_ratio(self):
        # 体の高さと幅の比

        if self.head.y - self.foot.y == 0:
            return 0
        else:
            return abs(self.head.x - self.foot.x) / abs(self.head.y - self.foot.y)

    @property
    def area(self):
        return (self.head.x - self.foot.x) * (self.head.y - self.foot.y)

    def get_coordinates(self, bool_image):
        """
            頭・腰・足の座標を取得するメソッド

        Args:
            bool_image(np.ndarray): 座標を取得する画像

        Returns:
            None

        Raises:
            NotEnoughError: 画像にラベルを付けられる領域が無い場合にRaiseされる

        """
        nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(bool_image)

        if nlabels <= 1:
            raise NotEnoughAreasError

        idx = stats[:, 4].argsort()[-2]
        self.head.x, self.head.y, w, h, *_ = stats[idx]
        self.foot.x = self.head.x + w
        self.foot.y = self.head.y + h

        self.waist.x = (self.head.x + self.foot.x) // 2
        waist_min = np.append(np.nonzero(labels[self.head.y: self.foot.y, self.waist.x])[0] + self.head.y, self.waist.y).min()
        waist_max = np.append(self.head.y + np.nonzero(labels[self.head.y: self.foot.y, self.waist.x])[0], self.waist.y).max()
        self.waist.y = (waist_max + waist_min) // 2

    def draw(self, image, _head=True, _foot=True, _waist=True, _rect=True):
        """画像に図形を描写するメソッド

        Args:
            image(np.ndarray): 図形を書き込む画像
            _head(bool): headを描画するか
            _foot(bool): footを描画するか
            _waist(bool): waistを描画するか
            _rect(bool): 長方形を描画するか

        Returns:
            None

        """
        if _head:
            cv2.circle(image, (self.head.x, self.head.y), 15, (234, 145, 152), -1)
        if _foot:
            cv2.circle(image, (self.foot.x, self.foot.y), 15, (234, 145, 152), -1)
        if _waist:
            cv2.circle(image, (self.waist.x, self.waist.y), 15, (234, 145, 152), -1)
        if _rect:
            cv2.rectangle(image, (self.head.x, self.head.y), (self.foot.x, self.foot.y), (0, 0, 255), 5)

    def get_max_body_height(self):
        self.max_body_height = self.foot.y - self.head.y

    def get_displacements(self):
        self.displacements.append(self.foot.y - self.head.y)
        if len(self.displacements) >= 1500:
            self.displacements.pop(0)


class NotEnoughAreasError(Exception):
    # ラベリングできる領域が無いエラー
    pass


class SoundPlayer:
    # 音声再生に関するクラス

    def __init__(self):
        self.voices: typing.Dict = {
            'high': './voice/高い.wav',
            'low': './voice/低い.wav',
            'bear': './voice/耐えろ.wav',
            'fast': './voice/早い.wav',
            'oi': './voice/おい.wav',
            'beep': './voice/beep.wav'
        }
        self.play_obj = simpleaudio.WaveObject.from_wave_file(self.voices['beep']).play()

    def play(self, key):
        """
        Args:
            key(str): 再生するボイスの内容

        """

        if self.play_obj.is_playing():
            return

        self.play_obj = simpleaudio.WaveObject.from_wave_file(self.voices[key]).play()


class Timer:
    # 時間とラップタイム計測ができる普通のタイマークラス

    def __init__(self):
        self.time = 0
        self.lap_time = 0

    @property
    def current_time(self):
        return time.time() - self.time

    def start(self):
        self.time = time.time()

    def reset(self):
        self.time = 0

    def lap_timer_start(self):
        if self.lap_time != 0:
            return
        else:
            self.lap_time = time.time()

    def lap_timer_reset(self):
        self.lap_time = 0

    @property
    def current_lap_time(self):
        return time.time() - self.lap_time
