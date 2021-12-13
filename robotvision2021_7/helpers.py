"""補助クラス

* Coordinate
    座標がピョンピョン跳ばないようにする座標管理クラス

* NotEnoughAreasError(仮)
    ラベリング時に領域数が少ない場合(今回であれば<3)にraiseされる
"""


import dataclasses

import cv2


@dataclasses.dataclass
class Coordinate:
    """座標を管理するクラス

    x・yが代入されたとき，変化量がthを上回る場合，変化量を(1-mom)倍に抑えるようにする
        -> 座標がピョンピョン跳ぶのを防ぐ

    """

    x: int = 0
    y: int = 0
    th: int = 25
    mom: float = 0.9

    def __setattr__(self, key, value):
        try:
            if abs(self.__getattribute__(key) - value) >= self.th:
                super().__setattr__(key, int(self.__getattribute__(key) * self.mom + value * (1 - self.mom)))
            else:
                super().__setattr__(key, value)

        except AttributeError:
            super().__setattr__(key, value)

    def draw(self, image, size=15):
        """(self.x, self.y)に点をプロットするメソッド

        Args:
            image(np.ndarray): 点をプロットする対象の画像
            size(int):         点の半径

        Returns:
            None
        """

        cv2.circle(image, (self.x, self.y), size, (234, 145, 152), -1)


class NotEnoughAreasError(Exception):
    pass
