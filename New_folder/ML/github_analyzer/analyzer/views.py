import requests
from django.shortcuts import render
from .utils import extract_username_from_url, preprocess_code, generate_prompt, run_gpt_model, calculate_complexity_score

def index(request):
    return render(request, 'index.html')

def fetch_user_repositories(github_url):
    username = extract_username_from_url(github_url)
    response = requests.get(f"https://api.github.com/users/{username}/repos")
    repositories = response.json()
    return repositories

import requests

def fetch_repository_code(repo):
    owner = repo['owner']['login']
    repo_name = repo['name']
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"

    response = requests.get(url)
    if response.status_code == 200:
        contents = response.json()
        code = ""
        for item in contents:
            if item['type'] == "file":
                file_content_url = item['download_url']
                file_response = requests.get(file_content_url)
                if file_response.status_code == 200:
                    code += file_response.text + "\n"
        return code

    return ""

def analyze_repositories(request):
    if request.method == 'GET':
        github_url = request.GET.get('github_url')
        repositories = fetch_user_repositories(github_url)

        preprocessed_repositories = []
        for repo in repositories:
            code = fetch_repository_code(repo)  # Fetch the code of the repository
            preprocessed_code = preprocess_code(code)
            preprocessed_repositories.append(preprocessed_code)

        evaluations = []
        for preprocessed_code in preprocessed_repositories:
            prompt = generate_prompt(preprocessed_code)
            evaluation = run_gpt_model(prompt)
            evaluations.append(evaluation)

        highest_complexity_score = float('-inf')
        most_complex_repo = None

        for i, repo in enumerate(repositories):
            complexity_score = calculate_complexity_score(evaluations[i])
            if complexity_score > highest_complexity_score:
                highest_complexity_score = complexity_score
                most_complex_repo = repo

        context = {
            'github_url': github_url,
            'repositories': repositories,
            'most_complex_repo': most_complex_repo,
            'complexity_score': highest_complexity_score,
        }

        return render(request, 'analysis.html', context)

    return render(request, 'index.html')
