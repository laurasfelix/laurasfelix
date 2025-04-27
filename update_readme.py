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
        max_retries = 20  # <-- Allow up to 20 retries (about 5-10 minutes if needed)

        while freq_data == [] and retries < max_retries:
            print(f"Retrying {repo_full_name} (GitHub still calculating stats)... attempt {retries+1}")
            time.sleep(15)  # <-- wait 15 seconds between retries to be polite to GitHub API
            freq_data = fetch_code_frequency(repo_full_name)
            retries += 1

        if not freq_data:
            print(f"⚠️ Skipping {repo_full_name} after {max_retries} retries — GitHub never responded.")
            continue

        for week in freq_data:
            additions = week[1]
            deletions = abs(week[2])
            total += additions + deletions

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
