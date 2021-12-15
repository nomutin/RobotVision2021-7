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

    def draw(self, image, size):
        cv2.circle(image, (self.x, self.y), size, (234, 145, 152), -1)


class BodyCoordinates:
    def __init__(self):
        self.head = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)
        self.foot = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)
        self.waist = Coordinate(x=0, y=0, th=COORDINATE_MOVEMENT_TH, mom=COORDINATE_MOMENTUM)

        self._x0 = 0
        self._x1 = 0
        self._y0 = 0
        self._y1 = 0

    @property
    def x_y_ratio(self):
        return abs(self.head.x - self.foot.x) / (self.head.y - self.foot.y)

    @property
    def area(self):
        return (self.head.x - self.foot.x) * (self.head.y - self.foot.y)

    def get_coordinates(self, bool_image):
        nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(bool_image)

        if nlabels <= 2:
            pass

        first_idx, second_idx, *_ = stats[:, 4].argsort()[-3:-1]
        x0 = self._x0 = min(stats[first_idx][0], stats[second_idx][0])
        y0 = self._y0 = min(stats[first_idx][1], stats[second_idx][1])
        w = max(stats[first_idx][2], stats[second_idx][2])
        h = max(stats[first_idx][3], stats[second_idx][3])
        x1 = self._x1 = x0 + w
        y1 = self._y1 = y0 + h

        self.head.x = int(statistics.median(np.append(np.nonzero(labels[y0, x0:x1])[0] + x0, self.head.x)))
        self.head.y = y0

        if self.head.x < (x0 + (x1 - x0) * 0.5):
            self.foot.x = x1
        else:
            self.foot.x = x0
        self.foot.y = y1

    def draw(self, image, _head=True, _foot=True, _waist=True, _rect=True):
        if _head:
            cv2.circle(image, (self.head.x, self.head.y), 15, (234, 145, 152), -1)
        if _foot:
            cv2.circle(image, (self.foot.x, self.foot.y), 15, (234, 145, 152), -1)
        if _waist:
            cv2.circle(image, (self.waist.x, self.waist.y), 15, (234, 145, 152), -1)



class NotEnoughAreasError(Exception):
    pass
