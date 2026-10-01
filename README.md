# Focus pad

Simple GUI application used to keep track of hours spent focusing/studying. Written in Python using PySide6

---

##### This project is in its early stages of development. Installation files are yet to be released.

## To-Do list:

- [ ] Make it possible to edit focused time when goal is undefined

- [ ] Add graph functionality

- [ ] Make the app go to system tray when closed

- [ ] Warn the user when they have not reached their goal yet

- [ ] Add a setting window that includes settings for warnings and more

- [ ] Add To-Do list to the app

- [ ] Add gregorian date system support

- [ ] Release the first version of the app for Linux & Windows

---

## Installation

Release files have not been added yet. If you want to try the app before its first release follow the instructions below.

##### Linux:

1. Download this repo and navigate to the downloaded files, you can use the command below if you have git installed on your machine.

```bash
git clone https://github.com/amirali-davari/focus-pad.git
cd focus-pad
```

2. Create a Python virtual environment to install the app's dependencies inside of it. You can use the command below.

```bash
python3 -m venv venv
```

3. Activate your newly created virtual environment.

```bash
source ./venv/bin/activate
```

4. Install the dependencies by running the command below.

```bash
python3 -m pip install -r requirements.txt
```

5. That's it! You can start the app by running the command below. Make sure you are in the directory where you cloned the repo and have activated the virtual environment before running the command.

```bash
python3 main.py
```

##### Windows:

1. You need to have Python installed on your machine. You can install Python from [Python's official website](https://www.python.org/).

2. Download this repo and navigate to the downloaded files, you can use the command below if you have git installed on your machine.

```powershell
git clone https://github.com/amirali-davari/focus-pad.git
cd focus-pad
```

3. Create a Python virtual environment to install the app's dependencies inside of it. You can use the command below.

```powershell
python -m venv venv
```

4. Activate your newly created virtual environment.

```powershell
.\venv\Scripts\activate
```

5. Install the dependencies by running the command below.

```powershell
python -m pip install -r requirements.txt
```

6. That's it! You can start the app by running the command below. Make sure you are in the directory where you cloned the repo and have activated the virtual environment before running the command.

```powershell
python main.py
```
