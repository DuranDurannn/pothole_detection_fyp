
# Deep Learning Based Pothole Detecttion for Aerial Drone with Geospatial Analysis

This is my final year project where it uses YOLOv11 model to help with the detection of pothole and road distress. 

*It is recommended to run this project with GPU for faster inference, CPU can be use but will be very slow.*

## Installation
**Clone the project**

```bash
  git clone https://github.com/DuranDurannn/pothole_detection_fyp
```

**Create an environment:**

Go to project directory:
```bash
  cd <my_project>
```

Python enviroment:
```bash
python -m venv <project_name> 
```

Conda enviroment:
```bash
conda create --name <project_name> python
```

**Activating a virtual environment:**

Python enviroment:
```bash
<project_name>\Scripts\activate.ps1
```
Conda enviroment
```bash
conda activate <project_name>
```

**Installing library:**
```bash
pip install -r requirements.txt
```
After installation, use ```pip list``` to view is the library correctly installed.


## Run Locally

Make sure to run the backend, ```app.py``` before running the web app locally

Run locally (Any local hosting is fine, i use ```npm http-server```)

```bash
  http-server . 
```




## Demo
**Map view**
![Map view](https://github.com/DuranDurannn/pothole_detection_fyp/blob/main/images/system.png)

**Video view**
![Video view](https://github.com/DuranDurannn/pothole_detection_fyp/blob/main/images/system2.png)
