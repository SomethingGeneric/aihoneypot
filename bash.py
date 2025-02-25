import requests
import argparse
from threading import Lock

class BashShell:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.lock = Lock()

    def execute_command(self, command):
        with self.lock:
            response = self.make_request(command)
            return response

    def make_request(self, command):
        url = f"{self.endpoint}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "llama3.2",
            "stream": False,
            "prompt": f"Pretend to be a Bash shell on an Ubuntu Linux system. Do not respond with anything other than what the user would see in the terminal after running this command: {command}"
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed with status code {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description="Bash Shell")
    parser.add_argument("--endpoint", type=str, help="Endpoint for the LLaMA model API")
    args = parser.parse_args()

    bash_shell = BashShell(args.endpoint)

    while True:
        command = input("bash$: ")
        if not command.strip():
            continue
        response = bash_shell.execute_command(command)
        print(response['response'])

if __name__ == "__main__":
    main()
