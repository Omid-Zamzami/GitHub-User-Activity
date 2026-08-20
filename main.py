import requests

def github_user_activity():
    username = input("Please enter the username: ").strip()

    if not username:
        print(f"Error: Username cannot be empty.")
        return

    base_url = f"https://api.github.com/users/{username}/events"
    headers = {
            "User-Agent": "GitHub-Activity-CLI",
        }

    try:
        response = requests.get(base_url, headers=headers, timeout=10)

        if response.status_code == 404:
            print(f"Error: User '{username}' was not found.")
            return
        elif response.status_code == 403:
            print("Error: API rate limit exceeded. Please try again later.")
            return

        response.raise_for_status()

        events = response.json()

    except requests.exceptions.Timeout:
        print(f"Error: Request timed out. Please check your network and try again.")
        return
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to GitHub. Please check your internet connection.")
        return
    except requests.exceptions.HTTPError as error:
        print(f"HTTP Error occurred: {error}")
        return
    except requests.exceptions.RequestException as error:
        print(f"An unexpected network error occurred: {error}")
        return
    except ValueError:
        print("Error: Failed to parse JSON response from server.")
        return

    if not isinstance(events, list):
        print("Error: Unexpected data structure received from GitHub.")
        return

    if not events:
        print(f"No recent activity found for user '{username}'.")
        return
    
    for event in events:
        if not isinstance(event, dict):
            continue

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

if __name__ == "__main__":
    github_user_activity()