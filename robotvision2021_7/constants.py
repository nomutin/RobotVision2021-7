# 定数を管理するファイル

from typing import Final

# --- Coordinates()関連 ---
COORDINATE_MOVEMENT_TH: Final = 30   # 座標がワープした，と判断する移動量のしきい値
COORDINATE_MOMENTUM: Final = 0.8     # 座標がワープした時の変化を抑える割合

# --- stand_by()関連 ---
STAND_BY_TH_X_Y_RATIO: Final = 2.6   # 腕立て伏せの姿勢になった，と判断する体の輪郭の縦横比
STAND_BY_AREA_MIN: Final = 0.05      # 腕立て伏せの姿勢になった，と判断する体の面積の最小値
STAND_BY_AREA_MAX: Final = 0.5       # q腕立て伏せの姿勢になった，と判断する体の面積の最大値

WAIST_TH: Final = 50

LOW_FORM_TIME: Final = 2
LOW_FORM_RATIO: Final = 0.4
VELOCITY_MEASURE_TIME: Final = 0.5


V_TH = 50
