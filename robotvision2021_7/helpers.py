"""補助クラス

* Coordinate
    座標がピョンピョン跳ばないようにする座標管理クラス

* NotEnoughAreasError(仮)
    ラベリング時に領域数が少ない場合(今回であれば<3)にraiseされる
"""


import dataclasses

import cv2

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

    @property
    def x_y_ratio(self):
        return abs(self.head.x - self.foot.x) / (self.head.y - self.foot.y)

    @property
    def area(self):
        return (self.head.x - self.foot.x) * (self.head.y - self.foot.y)

    def draw(self, size, image, head=True, foot=True, waist=True):
        if head:
            self.head.draw(image, size)
        if foot:
            self.foot.draw(image, size)
        if waist:
            self.waist.draw(image, size)


class NotEnoughAreasError(Exception):
    pass
