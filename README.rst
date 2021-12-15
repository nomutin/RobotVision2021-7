======
ロボットビジョン2021-team7
======

腕立て伏せのフォームが悪いと本気でブチギレてくるプログラム
=====

CONFIG
-----
- ``RobotVision2021-7/core.py``
    main()など全体の流れが書いてある

- ``RobotVision2021-7/helpers.py``
    BodyCoordinates()などcore.pyに載せると冗長になる部分をこっちに書いてる
    ある意味ここが一番大事

- ``RobotVision2021-7/constants.py``
    しきい値などのパラメータはここにまとめてある

- ``pyproject.toml`` ・ ``poetry.lock``
    おまじない


USAGE
-----
事前にpip等で Poetry_ を入れること

``RobotVision2021-7`` ディレクトリで以下のコマンドを実行

- 環境構築

    ``poetry install``


- 実行

    ``poetry run python robotvision2021_7 -m``


poetryが無くてもopencv-pythonが実行できる環境なら

    ``python robotvision2021_7 -m``

で動きます

VERIFY
-----
白背景に全身黒でトレーニングだ

.. _Poetry: https://github.com/python-poetry/poetry