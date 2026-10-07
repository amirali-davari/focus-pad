# Focus pad

Simple GUI application used to keep track of hours spent focusing/studying. Written in Python using PySide6

---

## Installation

Linux & Windows:

1. Download the binary release file from the [release page](https://github.com/amirali-davari/focus-pad/releases).

2. Extract the file.

3. Start the app by opening the file named "Focus Pad". (Or "Focus Pad.exe" on Windows)

--- 

## To-Do list:

- [ ] Make it possible to edit focused time when goal is undefined

- [ ] Make the matplotlib graph part of my own window to allow real time graph customization with my own tool bar + matplotlib toolbar

- [ ] Make the app go to system tray when closed

- [ ] Warn the user when they have not reached their goal yet

- [ ] Add a setting window that includes settings for warnings and more

- [ ] Add To-Do list to the app

- [ ] Add a feature to make app block other apps for some amount of time

- [ ] Add gregorian date system support

## Completed items:

- [x] ~~Add graph functionality~~
- [x] ~~Release the first version of the app for Linux & Windows~~

---

## Running using code

Release files are availible for an easy installation. Use this method of installation only if you want to modify or study the code.

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
