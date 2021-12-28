# ロボットビジョン2021-team7

![python](https://img.shields.io/badge/python-3.6|3.7|3.8|3.9-blue)
    
    
## USAGE

長瀬・野村はパッケージマネージャとして[Poetry](https://github.com/python-poetry/poetry)
を使用しました．

これは無くても大丈夫ですが，環境の状態に合わせて``RobotVision2021-7`` ディレクトリで以下のコマンドを実行する必要があります．

<details>
<summary>Poetryがインストール済の場合 </summary>


- 環境構築

    ``poetry install``


- 実行

    ``poetry run python robotvision2021_7 -m``
</details>

<details>
<summary>OpenCVのみインストール済の場合</summary>

音声再生のためのライブラリ[simpleaudio](https://github.com/hamiltron/py-simple-audio)
を追加でインストールする必要があります．

- 環境構築

    ``pip install simpleaudio``


- 実行

    ``python robotvision2021_7 -m``



</details>


<details>
<summary>OpenCV・simpleaudioがインストール済の場合</summary>

追加インストールや仮想環境構築をする必要はありません．

- 実行

    ``python robotvision2021_7 -m``


</details>

## CONFIG
- ``robotvision2021_7/core.py``

    main()など全体の流れが書いてあります．

- ``robotvision2021_7/helpers.py``

    core.pyに載せると冗長になる部分をこのファイルに書いています．

- ``robotvision2021_7/constants.py``

    しきい値などのパラメータがまとめて記述してあります．

- ``pyproject.toml`` ・ ``poetry.lock``

    Poetry関連のファイルです．requirements.txtみたいなものです