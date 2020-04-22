# python-optics-lab
Виртуальные лабораторные работы:

* 405: Эффект Поккельса
* 407: Проебразование Фурье в оптике 

## Установка

Устнавливем [Anaconda](https://www.anaconda.com/) для Python3 
или устанавливаем Python с [официального сайта](https://www.python.org/)

Устанавливаем пакет с помощью `pip`, для этого в терминале (например, программа Anaconda Power Shell) введите:
```
pip install mipt-npm-optics
```
Теперь можно запускать программу:
```
mipt-optics
```
или
```
mipt-optics.exe
```

также Вы можете запустить программу из исходного кода. Скачайте код из этого репозитория, откройте в терминале директорию с кодом и введите:
```
pip3 install -e .
# или
pip install -e .
```
для установки зависимостей. Затем для запуска программы введите:
```
python3 main.py 
```

### Ubuntu

#### Системный питон

```
sudo apt-get install python3-pip
```

### Установка зависимостей вручную
```
conda install pyqt numpy scipy matplotlib appdirs diffractio hickle pandas pillow
```
или
```
pip3 install pyqt5  numpy scipy matplotlib appdirs diffractio hickle pandas pillow
```
