import subprocess
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

SCRIPTS_FOLDER = "./cmdscripts/win"

def run_script(script_name):
    subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', f'{SCRIPTS_FOLDER}/{script_name}.ps1'])

def main():
    while True:
        choice = inquirer.select(
            message="Select an action:",
            choices=[
                Choice("config", "Configure Settings"),
                Choice("test", "Test Single Word"),
                Choice("app", "Run Application"),
                Choice("quit", "Quit")
            ],
            default="quit"
        ).execute()

        if choice == "quit":
            if inquirer.confirm(message="Are you sure you want to quit?", default=False).execute():
                break
            else:
                continue
        
        script_map = {
            "config": "runconfig",
            "test": "runtestword",
            "app": "runapp"
        }
        
        run_script(script_map[choice])
        
        print("━"*50)

if __name__ == "__main__":
    main()