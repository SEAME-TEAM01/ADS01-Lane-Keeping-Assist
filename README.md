# Lane Keeping Assist
> ## Introduction
> In this project, you will be exposed to the intersection of virtual simulations and real-world applications. You will delve deep into the mechanisms of the Lane Keeping Assist System (LKA), a pivotal Level 1 autonomous driving feature. Using advanced simulation platforms and actual hardware, you will design, test, and implement an LKAS that can operate both virtually and in the real world.
> 
> *You can find full descriptions in [subject.en.md](subject.en.md)*.


## 🏛️ Repository Structure
```bash
├── README.md       
├── subject.en.pdf  # subject of the project
│
├── data-recorder/  # data recorder with auto-pilot for carla simulator
│   ├── main.py
│ 
├── cnn-trainer/    # creates CNN model
│   ├── main.py
│ 
├── auto-pilot/     # Auto-Pilot with generated model file
│   ├── main.py
│ 
│── docs/           # .md files documentations for the project
│   ├── CNN.md 
│   ├── Carla.md
│   ├── Control_car.md
│   ├── Data_processing.md
```

## 🗃️ Table of Contents
- [Repository Structure](#classical_building-repository-structure)
- [Table of Contents](#card_file_box-table-of-contents)
- [Installation](#arrow_down-Installation)
- [How to Use](#question_How-to-use)
- [Tech Stacks](#computer-tech-stacks)
- [Project Goal](#goal_net-project-goal)
- [Contributor](#office_worker-contributor)

## ⬇️ Installation
Please check the document below.
> [docs/installation.md](docs/installation.md)

## ❓ How to use

### 1. Run the Carla Server Application.
- Linux
```Shell
./CarlaUE4.sh
```
- Windows
```Shell
./CarlaUE4.exe
```

After launch, you might can check applications look like this. You can look around the world with WASD and the mouse.

<img src="docs/imgs/carla-screenshot.png">

If your computer's graphic power is not enough so the application is too slow, check the command line options [here](https://carla.readthedocs.io/en/0.9.14/start_quickstart/#command-line-options). You can lower the quality by `--quality-level=Low` option.

### 2. Launch the auto-pilot.

- Move to `auto-pilot/` directory.

```Shell
# Linux / Windows
cd auto-pilot
```

- Launch the main.py application.

If you have changed some port of Carla, please let our application find that port with `--port 2004` options.

```Shell
# Linux / Windows
py -3.7 main.py
```

- ***NOW YOU SEE ME!***

## 💻 Tech Stacks

## 🧑‍💼 Contributor
- [@KKWANH](github.com/KKWANH)
- [@Shuta-Syd](github.com/Shuta-Syd)
- [@welida42](github.com/welida42)