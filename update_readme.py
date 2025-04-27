import requests
import time

USERNAME = "laurasfelix"

GITHUB_TOKEN = ""

GITHUB_API = "https://api.github.com"
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def fetch_repos(username):
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API}/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching repos: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def fetch_code_frequency(repo_full_name):
    url = f"{GITHUB_API}/repos/{repo_full_name}/stats/code_frequency"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching code frequency for {repo_full_name}")
        return []
    return response.json()


def calculate_lines_of_code(repos):
    total = 0
    for repo in repos:
        repo_full_name = repo['full_name']
        print(f"Fetching {repo_full_name}...")
        freq_data = fetch_code_frequency(repo_full_name)

        retries = 0
        while freq_data == [] and retries < 5:
            print(f"Retrying {repo_full_name} (GitHub is calculating stats)...")
            time.sleep(2)
            freq_data = fetch_code_frequency(repo_full_name)
            retries += 1

        for week in freq_data:
            total += week[1] + week[2]
    return total

def update_readme(net_lines):
    with open("README.md", "r") as file:
        readme = file.read()

    updated_readme = readme.replace("{{ lines_of_code }}", f"{net_lines:,}")

    with open("README.md", "w") as file:
        file.write(updated_readme)

if __name__ == "__main__":
    print(f"Fetching repositories for {USERNAME}...")
    repos = fetch_repos(USERNAME)
    print(f"Found {len(repos)} repositories.")
    
    total = calculate_lines_of_code(repos)

    update_readme(total)
    print("README.md updated successfully.")
