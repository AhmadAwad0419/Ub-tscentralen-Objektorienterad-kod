# Ub-tscentralen - Objektorienterad kod

## Project Overview

This project, named "Ub-tscentralen" (Submarine Central), is a Python-based application designed to simulate and manage the operations of multiple submarine drones. It utilizes an object-oriented approach to handle various aspects of submarine behavior, including movement, collision detection, torpedo systems, and sensor data processing. The application aims to provide a centralized system for monitoring and controlling these autonomous underwater vehicles.

## Features

The Ub-tscentralen project includes the following key features:

*   **Submarine Management**: Creation and tracking of individual submarine drones with unique IDs and position data.
*   **Movement Simulation**: Simulates submarine movement based on directional commands (up, down, forward) and distances.
*   **Collision Detection**: Real-time detection of collisions between submarines based on their current positions.
*   **Torpedo System**: Manages torpedo launches and includes a friendly-fire checking mechanism to prevent accidental targeting of allied submarines.
*   **Sensor Data Processing**: Functionality to load, analyze, and save sensor data, identifying errors and patterns.
*   **Modular Design**: Organized into distinct modules for configuration, core logic, data handling, graphical user interface (GUI - though not fully implemented in the provided `main.py`), and utilities.

## Project Structure

The project is structured into several directories, each serving a specific purpose:

```
Ub-tscentralen-Objektorienterad-kod/
├── files/
│   ├── README.md
│   ├── report.pdf
│   └── requirements.txt
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── paths.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── collision_checker.py
│   │   ├── movement_manager.py
│   │   ├── nuke_activation.py
│   │   ├── sensor_manager.py
│   │   └── submarine.py
│   │   └── torpedo_system.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── file_reader.py
│   │   └── secrets_loader.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── log_view.py
│   │   ├── main_window.py
│   │   └── map_view.py
│   ├── logs/
│   │   └── system_2025-09-05.log
│   │   └── system_2025-09-15.log
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── validators.py
│   └── main.py
```

### Directory Breakdown:

*   `files/`: Contains miscellaneous project files, including documentation (`README.md`, `report.pdf`) and project dependencies (`requirements.txt`).
*   `src/`: The main source code directory.
    *   `config/`: Configuration files, such as `paths.py` for defining important directory paths.
    *   `core/`: Contains the core logic and main classes of the submarine simulation.
    *   `data/`: Modules for data handling, including `file_reader.py` for reading movement data and `secrets_loader.py` for managing sensitive information.
    *   `gui/`: Modules related to the graphical user interface, though `main.py` primarily focuses on the core simulation logic.
    *   `logs/`: Stores system log files.
    *   `utils/`: Utility functions and helper modules, such as `logger.py` and `validators.py`.
    *   `main.py`: The entry point of the application.


## Core Components and Functionality

### `src/core/submarine.py`

This module defines the `Submarine` class, which represents an individual submarine drone. Each submarine has a unique ID, tracks its vertical and horizontal positions, and records its movements. It includes methods for loading movement data from files, updating its position based on commands, and retrieving its current coordinates.

### `src/core/movement_manager.py`

The `MovementManager` class is responsible for orchestrating the movements of multiple submarines. It loads submarine objects and their respective movement generators, then iteratively processes movement commands. This manager also integrates with the `CollisionChecker` and `TorpedoSystem` to perform checks after each batch of movements.

### `src/core/collision_checker.py`

The `CollisionChecker` class is designed to detect collisions between submarines. It maintains a log of detected collisions and identifies new collisions based on the current positions of all active submarines. When a collision is detected, it logs the event and the involved submarines.

### `src/core/torpedo_system.py`

This module implements the `TorpedoSystem` class, which handles torpedo launch simulations and friendly-fire checks. It can analyze potential torpedo trajectories to determine if an allied submarine is in the line of fire, generating a report for each launch attempt.

### `src/core/sensor_manager.py`

The `SensorManager` class provides functionality for loading, analyzing, and saving sensor data. It can process sensor logs line by line, count errors (represented by '0's), and identify patterns within the data. This is crucial for monitoring the operational health and behavior of the submarines.

### `src/data/file_reader.py`

This utility class is responsible for reading movement commands from external files, typically `.txt` files, and yielding them as a generator. This allows for efficient processing of potentially large movement logs without loading the entire file into memory.

### `src/data/secrets_loader.py`

Handles the loading of sensitive information or 

secrets from a designated source. The `main.py` uses this to ensure necessary credentials or configurations are loaded before proceeding with the simulation.

## Getting Started

### Prerequisites

This project requires Python 3.x. The specific dependencies are listed in `files/requirements.txt`.
“If the module is not found, you can install it manually using pip install in the terminal.”

### Installation

1.  **Clone the repository:**

    ```bash
    Ask for it! 
    It is private repository. 
    ```


2.  **Create a virtual environment:**
    🖥 Windows (PowerShell or CMD)
    ```bash
    python -m venv venv 
    ```
    
    🍎 macOS / 🐧 Linux
    ```bash
    python3 -m venv venv 
    ```
    

3.  **Activate the virtual environment:**
    🖥 Windows (PowerShell)
    venv\Scripts\Activate.ps1

    If using CMD:
    venv\Scripts\activate.bat

    🍎 macOS / 🐧 Linux
    source venv/bin/activate


4.  **Install dependencies:**

    ```bash
    pip install -r files/requirements.txt 
    ```
    “If the module is not found, you can install it manually using pip install in the terminal.”

### Running the Application

To run the main simulation, execute `main.py` from the `src` directory:

```bash
python src/main.py
```



