# 前提
- pythonが実行できること
- pipがinstallされていること

# 実行環境(pythonのバージョンが3.2以降なら問題ないと思います。)
```
python 3.8.1
```

# プログラム実行手順
1. 仮想環境を作成
```
python -m venv google_scraping
```

2. 仮想環境を切り替え
```
source google_scraping/bin/activate
```

3. 必要なモジュールを追加
```
pip install -r requirements.txt
```

4. プログラム実行
```
python google_scraping_main.py
```