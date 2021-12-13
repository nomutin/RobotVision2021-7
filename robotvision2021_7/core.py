"""RobotVision2021-7

* 腕立て伏せ激励アプリ

  腕立て伏せのフォームが悪かったら本気で怒号を飛ばすアプリ

author: 長瀬・野村

TODO:
    get_coordinates:
    * 頭の向きから足を判別する
    * 腰をの位置を前回の方法から判別する
    * docstringを書く
    General:
    * 怒号を録音する

"""

import cv2
import dataclasses
import numpy as np
import statistics as st


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


def get_background():
    """背景を撮影する関数

    画面からはけた状態のスクリーンショットをsキー押下で撮影する

    Returns:
        frame(np.ndarray): スクリーンショットした画面フレーム
    """

    cap = cv2.VideoCapture(0)

    while cv2.waitKey(1) != ord("s"):
        cv2.imshow("camera", cap.read()[1])
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
        kernel_size(int):   体のラインを強調するための膨張・収縮のサイズ

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


def get_coordinates(stats, labels, head, foot):
    first_idx, second_idx, *_ = stats[:, 4].argsort()[-3:-1]
    x0 = min(stats[first_idx][0], stats[second_idx][0])
    y0 = min(stats[first_idx][1], stats[second_idx][1])
    w = max(stats[first_idx][2], stats[second_idx][2])
    h = max(stats[first_idx][3], stats[second_idx][3])
    x1 = x0 + w
    y1 = y0 + h

    head.x = int(st.median(np.append(np.nonzero(labels[y0, x0:x1])[0] + x0, head.x)))
    head.y = y0

    return x0, y0, w, h, x1, y1


def main():
    bg = get_background()
    cap = cv2.VideoCapture(0)

    head = Coordinate()
    waist = Coordinate()
    foot = Coordinate()

    while True:
        _, frame = cap.read()

        fgmask = create_fgmask(bg, frame, 8)
        nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(fgmask)
        src = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        if nlabels <= 2:
            continue

        x0, y0, w, h, x1, y1 = get_coordinates(stats, labels, head, foot)
        cv2.rectangle(src, (x0, y0), (x1, y1), (0, 0, 255), 5)

        head.draw(image=src)
        cv2.imshow('mask', src)
        cv2.imshow("flow", frame)

        if cv2.waitKey(1) == ord("q"):
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    main()
