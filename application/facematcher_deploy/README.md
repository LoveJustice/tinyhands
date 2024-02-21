# Facematcher_deploy

The project folder is found at tinyhands/applications/facematcher_deploy

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them:

- Python 3.x (where x is the subversion)
- pip (Python package installer, comes with Python 3.4+)

### Installing


#### Setting Up a Virtual Environment

1. **Create a Virtual Environment**

    Navigate to yourtinyhands/applications/facematcher_deploy/ in the terminal and run:

    ```sh
    python3 -m venv venv
    ```

    This command creates a virtual environment named `venv` within your project directory.

2. **Activate the Virtual Environment**

    - On macOS and Linux:

    ```sh
    source venv/bin/activate
    ```

    - On Windows:

    ```cmd
    .\venv\Scripts\activate
    ```

    You should now see `(venv)` at the beginning of your terminal line, indicating that the virtual environment is activated.

#### Installing Dependencies

With the virtual environment activated, install the project dependencies by running:

```sh
pip install -r requirements.txt

```
#### Authentication
The secrets.toml file is required to run the application. This file is not included in the repository. 
Please contact the project owner for the secrets.toml file.   
This file is placed in the .streamlit directory of the project directory

#### Running the Application

With the virtual environment activated, run the application by running:
The streamlit app is activated with:
```sh
streamlit run facematcher_deploy.py
```