# GitHub User Activity CLI

A lightweight command-line utility written in Python for retrieving and displaying a GitHub user's recent public activity. The application communicates directly with the GitHub Events API, formats common event types into human-readable messages, and provides clear handling for invalid input, API errors, network failures, and unexpected responses.

---

## 🌟 Key Features

* **GitHub Events API Integration:** Fetches recent public activity for a specified GitHub username using the GitHub REST API.
* **Command-Line Interface:** Accepts the GitHub username directly as a command-line argument.
* **Human-Readable Activity Output:** Converts GitHub event data into concise messages showing the action, repository, and timestamp.
* **Multiple Event Types:** Provides dedicated formatting for `PushEvent`, `IssuesEvent`, `WatchEvent`, `CreateEvent`, `DeleteEvent`, `PullRequestEvent`, and `ForkEvent`.
* **Push Commit Handling:** Determines the number of pushed commits using the event `size`, the `commits` list, or a safe default of one commit.
* **Timestamp Formatting:** Converts GitHub's ISO 8601 UTC timestamps into `YYYY-MM-DD HH:MM:SS` format, with a fallback to the original value when parsing fails.
* **Robust Error Handling:** Handles missing usernames, empty usernames, unknown users, API rate limits, HTTP errors, timeouts, connection failures, JSON parsing errors, and unexpected response structures.
* **Safe Payload Processing:** Uses defensive access to event and payload fields and falls back to sensible values when optional data is missing.
* **Automated Testing:** Includes a comprehensive `pytest` test suite covering CLI validation, API requests, network failures, response validation, event formatting, and edge cases.

---

## 🛠️ Prerequisites

* **Python 3.10 or higher** (required for the `match-case` syntax used by the application).
* An active internet connection is required when running the application because it retrieves activity directly from GitHub's API.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Omid-Zamzami/GitHub-User-Activity.git
cd GitHub-User-Activity
```

### 2. Install Dependencies

Install the required packages with:

```bash
pip install -r requirements.txt
```

The project uses `requests` for GitHub API communication and `pytest` for automated testing.

### 3. Run the Application

Provide a GitHub username as the command-line argument:

```bash
python main.py <username>
```

For example:

```bash
python main.py octocat
```

If no username is supplied, the program displays:

```text
Usage: python main.py <username>
```

---

## 📋 Example Output

For a user with recent public activity, the CLI can produce output such as:

```text
Pushed 3 commit(s) to octocat/example-repository on 2026-08-19 02:54:48
Opened an issue in octocat/example-repository on 2026-08-19 03:10:21
Starred octocat/another-repository on 2026-08-19 04:05:12
Created repository in octocat/example-repository on 2026-08-19 05:20:00
Deleted branch 'feature-x' in octocat/example-repository on 2026-08-19 06:15:30
Closed a pull request in octocat/example-repository on 2026-08-19 07:40:10
Forked original/repository to octocat/forked-repository on 2026-08-19 08:00:00
```

The exact output depends on the activity returned by GitHub.

---

## 🔎 Supported Activity Types

The application provides specific output formatting for the following GitHub event types:

| Event Type | Displayed Information |
|---|---|
| `PushEvent` | Number of commits, repository, and timestamp |
| `IssuesEvent` | Issue action, repository, and timestamp |
| `WatchEvent` | Repository starred and timestamp |
| `CreateEvent` | Created reference type, repository, and timestamp |
| `DeleteEvent` | Deleted reference type/name, repository, and timestamp |
| `PullRequestEvent` | Pull request action, repository, and timestamp |
| `ForkEvent` | Original and forked repository names, plus timestamp |
| Other events | Event type, repository, and timestamp |

Events that are not explicitly handled are still displayed using a generic fallback format rather than being silently discarded.

---

## ⚠️ Error Handling

The application is designed to fail gracefully in common error scenarios.

It handles:

1. **Missing username argument** — displays the command usage and exits.
2. **Empty username** — rejects whitespace-only input.
3. **User not found (`404`)** — reports that the requested GitHub user was not found.
4. **API rate limit (`403`)** — informs the user that the GitHub API rate limit has been exceeded.
5. **Other HTTP errors** — reports the HTTP error returned by the API.
6. **Request timeout** — reports that the request timed out.
7. **Connection failure** — reports that GitHub could not be reached.
8. **Other request errors** — reports unexpected network-related failures.
9. **Invalid JSON** — reports that the server response could not be parsed.
10. **Unexpected response structure** — verifies that the decoded GitHub response is a list.
11. **No recent activity** — clearly reports when the returned event list is empty.

The API request also uses a **10-second timeout** and identifies the client with the `GitHub-Activity-CLI` User-Agent.

---

## 🧪 Running Tests

This project includes automated unit tests written with `pytest`.

The test suite covers:

* ISO 8601 timestamp conversion.
* Empty and invalid timestamps.
* Missing and empty CLI arguments.
* Correct GitHub API URL, headers, and timeout.
* `404` user-not-found responses.
* `403` API rate-limit responses.
* HTTP server errors.
* Network timeout and connection errors.
* Invalid JSON responses.
* Unexpected JSON structures.
* Empty activity lists.
* Different `PushEvent` commit-count scenarios.
* Formatting of all explicitly supported event types.
* Fallback handling for unsupported event types.

Run the complete test suite with:

```bash
pytest -v
```

---

## 📁 Repository Structure

```text
GitHub-User-Activity/
├── .gitignore          # Git ignore rules
├── LICENSE             # Project license
├── README.md           # Project documentation
├── requirements.txt    # Runtime and testing dependencies
├── main.py             # Main CLI application
└── test_main.py        # Automated pytest test suite
```

---

## 📦 Dependencies

The project keeps its dependency list intentionally small:

```text
requests>=2.31.0
pytest>=8.0.0
```

`requests` is used by the application to communicate with the GitHub API, while `pytest` is used to run the automated test suite.

---

## 🔐 API & Authentication

The application accesses the public GitHub Events API endpoint for the supplied username:

```text
https://api.github.com/users/<username>/events
```

The current implementation does **not** require a GitHub personal access token. It requests publicly available activity and sends a custom `User-Agent` header.

Because the application relies on GitHub's public API, requests remain subject to GitHub API availability and rate limits.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
