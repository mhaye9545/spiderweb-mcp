
from fastmcp import FastMCP
from github import GithubException
from spiderweb_mcp.auth.clients import get_github_client


def register_github_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_github_issues(repo_name: str, state: str = "open") -> str:
        """Lists issues for a given repository (e.g. 'owner/repo'). State: 'open', 'closed', 'all'."""
        gh = get_github_client()
        repo = gh.get_repo(repo_name)
        issues = repo.get_issues(state=state)

        result = [
            f"#{issue.number} [{issue.state}]: {issue.title} (Comments: {issue.comments})"
            for issue in issues[:15]
            if not issue.pull_request
        ]
        return "\n".join(result) if result else f"No issues found with state '{state}'."

    @mcp.tool()
    def create_github_issue(repo_name: str, title: str, body: str, labels: list[str] = None) -> str:
        """Creates a new issue in a GitHub repository."""
        gh = get_github_client()
        repo = gh.get_repo(repo_name)
        kwargs = {"title": title, "body": body}
        if labels:
            kwargs["labels"] = labels
        issue = repo.create_issue(**kwargs)
        return f"Issue created: #{issue.number} ({issue.html_url})"

    @mcp.tool()
    def comment_github_issue(repo_name: str, issue_number: int, comment_body: str) -> str:
        """Adds a comment to an existing issue or pull request."""
        gh = get_github_client()
        repo = gh.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        comment = issue.create_comment(comment_body)
        return f"Comment added to #{issue_number}: {comment.html_url}"

    @mcp.tool()
    def list_github_pull_requests(repo_name: str, state: str = "open") -> str:
        """Lists pull requests for a given repository."""
        gh = get_github_client()
        repo = gh.get_repo(repo_name)
        pulls = repo.get_pulls(state=state)

        result = [
            f"PR #{pr.number} [{pr.state}]: {pr.title} ({pr.head.ref} -> {pr.base.ref})"
            for pr in pulls[:10]
        ]
        return "\n".join(result) if result else f"No PRs found with state '{state}'."

    @mcp.tool()
    def create_github_pull_request(repo_name: str, title: str, body: str, head_branch: str, base_branch: str = "main") -> str:
        """Creates a new pull request."""
        gh = get_github_client()
        repo = gh.get_repo(repo_name)
        pr = repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
        return f"Pull Request created: #{pr.number} ({pr.html_url})"

    @mcp.tool()
    def commit_and_push_file(repo_name: str, file_path: str, content: str, commit_message: str, branch: str = "main") -> str:
        """Creates or updates a file directly in a GitHub repository."""
        gh = get_github_client()
        repo = gh.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path, ref=branch)
            repo.update_file(contents.path, commit_message, content, contents.sha, branch=branch)
            return f"File '{file_path}' updated on branch '{branch}' (Commit: '{commit_message}')."
        except GithubException as e:
            if e.status == 404:
                repo.create_file(file_path, commit_message, content, branch=branch)
                return f"File '{file_path}' created on branch '{branch}' (Commit: '{commit_message}')."
            raise e