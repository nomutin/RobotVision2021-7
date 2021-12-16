"""補助クラス

* Coordinate
    座標がピョンピョン跳ばないようにする座標管理クラス

* NotEnoughAreasError(仮)
    ラベリング時に領域数が少ない場合(今回であれば<3)にraiseされる
"""


import dataclasses
import statistics

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

    def draw(self, image):
        cv2.circle(image, (self.x, self.y), 15, (234, 145, 152), -1)


class BodyCoordinates:
    def __init__(self):
        self.head = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)
        self.foot = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)
        self.waist = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)

    @property
    def x_y_ratio(self):
        if self.head.y - self.foot.y == 0:
            return 0
        else:
            return abs(self.head.x - self.foot.x) / abs(self.head.y - self.foot.y)

    @property
    def area(self):
        return (self.head.x - self.foot.x) * (self.head.y - self.foot.y)

    def get_coordinates(self, bool_image):
        nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(bool_image)

        if nlabels <= 1:
            raise NotEnoughAreasError

        first_idx, *_ = stats[:, 4].argsort()[-2:-1]
        self.head.x = stats[first_idx][0]
        self.head.y = stats[first_idx][1]
        w = stats[first_idx][2]
        h = stats[first_idx][3]
        self.foot.x = self.head.x + w
        self.foot.y = self.head.y + h

        self.waist.x = (self.head.x + self.foot.x) // 2
        waist_min = np.append(np.nonzero(labels[self.head.y: self.foot.y, self.waist.x])[0] + self.head.y, self.waist.y).min()
        waist_max = np.append(self.head.y + np.nonzero(labels[self.head.y: self.foot.y, self.waist.x])[0], self.waist.y).max()
        self.waist.y = (waist_max + waist_min) // 2

        # self.waist.y = int(
        #     statistics.median(
        #         np.append(self.head.y + np.nonzero(labels[self.head.y: self.foot.y, self.waist.x])[0], self.waist.y)
        #     )
        # )

    def draw(self, image, _head=True, _foot=True, _waist=True, _rect=True):
        if _head:
            cv2.circle(image, (self.head.x, self.head.y), 15, (234, 145, 152), -1)
        if _foot:
            cv2.circle(image, (self.foot.x, self.foot.y), 15, (234, 145, 152), -1)
        if _waist:
            cv2.circle(image, (self.waist.x, self.waist.y), 15, (234, 145, 152), -1)
        if _rect:
            cv2.rectangle(image, (self.head.x, self.head.y), (self.foot.x, self.foot.y), (0, 0, 255), 5)


class NotEnoughAreasError(Exception):
    pass


class Sound:
    def __init__(self):
        self.play_obj = None

    def play(self, file):
        if self.play_obj.is_playing():
            return

        wav_obj = simpleaudio.WaveObject.from_wave_file(file)
        self.play_obj = wav_obj.play()
