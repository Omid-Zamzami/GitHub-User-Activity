import requests
import sys
from datetime import datetime

def format_datetime(date_time: str) -> str:
    """Convert an ISO 8601 UTC timestamp string to a readable format (YYYY-MM-DD HH:MM:SS)."""
    if not date_time:
        return ""
    try:
        dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Fallback to the original string if parsing fails
        return date_time

def github_user_activity() -> None:
    """Fetch and display recent public activity for a given GitHub username."""

    # 1. Validate Command-Line Arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <username>")
        sys.exit(1)

    username: str = sys.argv[1].strip()

    if not username:
        print("Error: Username cannot be empty.")
        sys.exit(1)

    # 2. Configure API Endpoint & Headers
    base_url: str = f"https://api.github.com/users/{username}/events"
    headers: dict[str, str] = {
            "User-Agent": "GitHub-Activity-CLI",
        }

    # 3. Fetch Data from GitHub API with Exception Handling
    try:
        response = requests.get(base_url, headers=headers, timeout=10)

        # Handle specific HTTP status codes
        if response.status_code == 404:
            print(f"Error: User '{username}' was not found.")
            return
        elif response.status_code == 403:
            print("Error: API rate limit exceeded. Please try again later.")
            return

        # Raise exception for other HTTP errors (e.g., 500)
        response.raise_for_status()

        # Parse JSON payload
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

    # 4. Validate Response Payload Structure
    if not isinstance(events, list):
        print("Error: Unexpected data structure received from GitHub.")
        return

    if not events:
        print(f"No recent activity found for user '{username}'.")
        return

    # 5. Process and Display Events
    for event in events:
        if not isinstance(event, dict):
            continue

        # Extract event attributes safely
        event_type: str | None = event.get("type")
        payload: dict = event.get("payload", {})
        repo_name: str = event.get("repo", {}).get("name", "Unknown Repo")
        created_at_raw: str = event.get("created_at", "")
        created_at: str = format_datetime(created_at_raw)
        action: str = payload.get("action", "updated")

        # Format output based on event type
        match event_type:
            case "PushEvent":
                commit_count: int
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
                ref_type: str = payload.get("ref_type", "repository")
                print(f"Created {ref_type} in {repo_name} on {created_at}")

            case "DeleteEvent":
                ref_type: str = payload.get("ref_type", "item")
                ref_name: str = payload.get("ref", "")
                if ref_name:
                    print(f"Deleted {ref_type} '{ref_name}' in {repo_name} on {created_at}")
                else:
                    print(f"Deleted {ref_type} in {repo_name} on {created_at}")

            case "PullRequestEvent":
                print(f"{action.capitalize()} a pull request in {repo_name} on {created_at}")

            case "ForkEvent":
                forkee: dict = payload.get("forkee", {})
                fork_name: str | None = forkee.get("full_name")
                if fork_name:
                    print(f"Forked {repo_name} to {fork_name} on {created_at}")
                else:
                    print(f"Forked {repo_name} on {created_at}")

            case _:
                print(f"{event_type} in {repo_name} on {created_at}")

if __name__ == "__main__":
    github_user_activity()