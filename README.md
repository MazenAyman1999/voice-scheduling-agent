# To Test the Agent

# Steps to Run Locally (Windows)
1. Clone the git repository.
2. Install **Python 3.13** from this [link](https://www.python.org/downloads/windows/).
3. Open **Windows PowerShell** in the root directory of the project.
4. Execute the following command to create the environment:
```powershell
python -m venv .venv
```
5. Execute the following command to activate the environment:
```powershell
.venv\Scripts\Activate.ps1
```
, if you get an ExecutionPolicy block, re-open **Windows PowerShell** as *admin*, then execute the following commands:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```
6. Execute the following command to install the project dependencies:
```powershell
pip install -r requirements.txt
```
7. Create a *secrets.toml* file in a *.streamlit* directory, then add this line to it:
```
COHERE_API_KEY=<your_cohere's_api_key>
```
8. Execute the following command to run the application:
```powershell
streamlit run app.py
```
# Explanation of the Calendar Integration

# Screenshots

# Loom Video