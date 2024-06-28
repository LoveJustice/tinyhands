Installation
---

## Windows:

### 1. Install Git

- Go to [Git for Windows](https://gitforwindows.org/) to download the installer.
- Run the installer and follow the on-screen instructions.

### 2. Clone the Repository

- Open the Git Bash or Command Prompt.
- Navigate to the directory where you want to clone the repository.
- Run:
  ```
  git clone git@github.com:ChristoGH/lji_social_media.git
  ```

### 2.1 Create and Checkout a New Branch

- Navigate into the cloned directory:
  ```
  cd lji_social_media
  ```
- Create and checkout a new branch:
  ```
  git checkout -b your_branch_name
  ```

### 3. Create a Virtual Environment

- Ensure you have Python installed. If not, download and install it from the [Python official website](https://www.python.org/downloads/windows/).
- Run:
  ```
  python -m venv venv
  ```

### 4. Activate the Virtual Environment

- Run:
  ```
  .\venv\Scripts\activate
  ```

### 5. Install Dependencies from requirements.txt

- Ensure you're inside the project directory (`lji_social_media`).
- Run:
  ```
  pip install -r requirements.txt
  ```

### 6. Run Streamlit

- Run:
  ```
  streamlit run streamlit_fb_gpt.py
  ```

### 7. Exit Streamlit

- To exit Streamlit, press `CTRL + C` in the command prompt where it's running.

---

## macOS:

### 1. Install Git

- If not already installed, Git can be installed using [Homebrew](https://brew.sh/):
  ```
  brew install git
  ```

### 2. Clone the Repository

- Open the Terminal.
- Navigate to the directory where you want to clone the repository.
- Run:
  ```
  git clone git@github.com:ChristoGH/lji_social_media.git
  ```

### 2.1 Create and Checkout a New Branch

- Navigate into the cloned directory:
  ```
  cd lji_social_media
  ```
- Create and checkout a new branch:
  ```
  git checkout -b your_branch_name
  ```

### 3. Create a Virtual Environment

- Ensure you have Python installed. If not, install it using Homebrew:
  ```
  brew install python3
  ```
- Run:
  ```
  python3 -m venv venv
  ```

### 4. Activate the Virtual Environment

- Run:
  ```
  source venv/bin/activate
  ```

### 5. Install Dependencies from requirements.txt

- Ensure you're inside the project directory (`lji_social_media`).
- Run:
  ```
  pip install -r requirements.txt
  ```

### 6. Run Streamlit

- Run:
  ```
  streamlit run streamlit_fb_gpt.py
  ```

### 7. Exit Streamlit

- To exit Streamlit, press `CTRL + C` in the terminal where it's running.

---

It's always a good practice to test these steps on a clean environment to ensure all the instructions work as intended.
