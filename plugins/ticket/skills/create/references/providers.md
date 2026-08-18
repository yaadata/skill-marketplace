# Provider Routing

Read only the selected provider section. Provider schemas and commands can change, so inspect the available connector schema or CLI `--help` before calling it. Use non-interactive flags and body files where supported.

## Common Rules

- Prefer the exact saved MCP server or CLI when it is available and capable.
- MCP choices must expose issue creation plus the required metadata operations for this run.
- CLI choices must be installed, authenticated, and target the confirmed host/project.
- Use read-only commands for discovery. Do not create during capability checks.
- Do not install tools, start authentication flows, or change saved routing without a select-based user choice.
- Fetch the authenticated identity before offering assignment to self.
- Treat inaccessible templates or iterations as unknown, not proof that none exist. Explain the limitation and use the default template or no iteration only after the user selects that path.

## Jira

Supported routes:

- An available Jira or Atlassian MCP connector.
- Atlassian CLI (`acli`) with Jira work-item support.
- A compatible `jira` CLI whose help confirms project, issue-type, assignee, sprint, and create operations needed by the run.

Discover accessible projects, required create metadata, issue types, current user, templates when exposed, and active Jira sprints. Ask only the project plus fields required by that project's create schema.

## Linear

Supported routes:

- An available Linear MCP connector.
- An installed Linear CLI whose help confirms the required issue operations.

Discover teams/projects, required create metadata, current user, issue templates, and active cycles. Always ask about the project; include `No project` only if Linear permits it for the selected team.

## GitHub

Supported routes:

- An available GitHub MCP connector.
- GitHub CLI (`gh`), using repository-qualified issue commands.

Discover repositories from the current remote and authenticated account. Inspect repository issue forms and templates through the connector/API or `.github/ISSUE_TEMPLATE/`. A GitHub Projects iteration counts only when the selected tool exposes it as a native active iteration applicable to the issue; labels, milestones, and due dates do not.

## Codeberg and Forgejo

Supported routes:

- An available Codeberg or Forgejo MCP connector.
- Forgejo CLI (`fj`) when its help confirms the required issue operations.

Confirm the host and `owner/repository`; never infer Codeberg from an unrelated Forgejo remote. Discover repository issue templates through the provider or checked-out repository. Use only provider-native iterations exposed by the selected tool.

## GitLab

Supported routes:

- An available GitLab MCP connector.
- GitLab CLI (`glab`) with repository-qualified issue operations.

Confirm the GitLab host and project path. Discover project issue templates and native iterations only when exposed by the chosen tool.

## Gitea

Supported routes:

- An available Gitea MCP connector.
- Gitea CLI (`tea`) with an explicitly selected login/host and repository.

Confirm the configured host and `owner/repository`. Discover repository templates and provider-native iterations only when exposed by the chosen tool.
