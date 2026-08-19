import requests

username = input("Please enter the username: ")
base_url = f"https://api.github.com/users/{username}/events"

response = requests.get(base_url, timeout=10)
events = response.json()

for event in events:
    event_type = event['type']
    payload = event.get("payload", {})

    match event_type:
        case "PushEvent":
            if "size" in payload:
                commit_count = payload['size']
            elif "commits" in payload:
                commit_count = len(payload['commits'])
            else:
                commit_count = 1

            username_repo = event['repo']['name']
            print(f"Pushed {commit_count} commit(s) to {username_repo}")

        case "IssuesEvent":
            pass
        case "WatchEvent":
            pass
        case "CreateEvent":
            pass
        case "DeleteEvent":
            pass
        case "PullRequestEvent":
            pass
        case "ForkEvent":
            pass
        case _:
            pass