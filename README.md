# python-optics-lab

## Установка

### Windows

Устнавливем [Anaconda](https://www.anaconda.com/) для Python3.
В директории с файлом `setup.py` открываем терминал и вводи команду:
```
pip install -e .
```
Затем запускаем программу:
```
python3 main.py
```

### Ubuntu

#### Системный питон

```
sudo apt-get install python3-pip
```
В директории с файлом `setup.py` открываем терминал и вводи команду:
```
pip3 install -e .
```
Затем запускаем программу:
```
python3 main.py
```
### Установка зависимостей вручную
```
conda install pyqt numpy scipy matplotlib appdirs
```
или
```
pip3 install pyqt5 numpy scipy matplotlib appdirs
```