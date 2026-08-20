import requests

username = input("Please enter the username: ").strip()
base_url = f"https://api.github.com/users/{username}/events"

response = requests.get(base_url, timeout=10)
events = response.json()

for event in events:
    event_type = event.get("type")
    payload = event.get("payload", {})
    repo_name = event.get("repo", {}).get("name", "Unknown Repo")
    created_at = event.get("created_at", "")
    action = payload.get("action", "updated")

    match event_type:
        case "PushEvent":
            if "size" in payload:
                commit_count = payload['size']
            elif "commits" in payload:
                commit_count = len(payload['commits'])
            else:
                commit_count = 1
            print(f"Pushed {commit_count} commit(s) to {repo_name} on {created_at}")

        case "IssuesEvent":
            print(f"{action.capitalize()} an issue in {repo_name} on {created_at}")

        case "WatchEvent":
            print(f"Starred {repo_name} on {created_at}")

        case "CreateEvent":
            ref_type = payload.get("ref_type", "repository")
            print(f"Created {ref_type} in {repo_name} on {created_at}")
            
        case "DeleteEvent":
            ref_type = payload.get("ref_type", "item")
            ref_name = payload.get("ref", "")
            if ref_name:
                print(f"Deleted {ref_type} '{ref_name}' in {repo_name} on {created_at}")
            else:
                print(f"Deleted {ref_type} in {repo_name} on {created_at}")

        case "PullRequestEvent":
           print(f"{action.capitalize()} a pull request in {repo_name} on {created_at}")

        case "ForkEvent":
            forkee = payload.get("forkee", {})
            fork_name = forkee.get("full_name")
            if fork_name:
                print(f"Forked {repo_name} to {fork_name} on {created_at}")
            else:
                print(f"Forked {repo_name} on {created_at}")

        case _:
            print(f"{event_type} in {repo_name} on {created_at}")