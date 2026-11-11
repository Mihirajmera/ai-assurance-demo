# AI Agent Access Review: 2026-10-12

**2 agents**, **2 tool grants**, **9 findings** (5 high, 2 medium, 2 low).

## Agents

| Agent | Source | Owner | Approved | Tools | High | Medium | Low |
|---|---|---|---|---:|---:|---:|---:|
| [Release Agent](#release-bot) | `agents.yaml` | dana@example.com | 2026-06-30 by platform-security | 1 | 0 | 1 | 0 |
| [MCP host (.mcp.json)](#mcp) | `.mcp.json` | **none** | **none** | 1 | 5 | 1 | 2 |

## Control results

| Check | Control | Agents failing | Frameworks |
|---|---|---:|---|
| AAR-01 | Every agent has an accountable human owner | 1 / 2 | NIST 800-53 AC-2; SOC 2 CC6.2; NIST AI RMF GOVERN 2.1 |
| AAR-02 | Agent access is approved and recertified within 90 days | 2 / 2 | NIST 800-53 AC-2; SOC 2 CC6.2, CC6.3 |
| AAR-03 | Privileged agent actions require human approval | 1 / 2 | NIST 800-53 AC-6; SOC 2 CC6.3; NIST AI RMF MAP 3.5; OWASP LLM LLM06 |
| AAR-04 | Tool scopes follow least privilege | 0 / 2 | NIST 800-53 AC-6; SOC 2 CC6.3; OWASP LLM LLM06 |
| AAR-05 | Code and shell execution is sandboxed | 0 / 2 | NIST 800-53 CM-7, AC-6; OWASP LLM LLM05, LLM06 |
| AAR-06 | No credentials are hardcoded in agent configuration | 0 / 2 | NIST 800-53 IA-5; SOC 2 CC6.1 |
| AAR-07 | Agent credentials are rotated within 90 days | 1 / 2 | NIST 800-53 IA-5; SOC 2 CC6.1 |
| AAR-08 | Dormant agent access is removed after 90 days | 1 / 2 | NIST 800-53 AC-2(3); SOC 2 CC6.2 |
| AAR-09 | No unmitigated data exfiltration path | 1 / 2 | NIST 800-53 AC-4; NIST AI RMF MEASURE 2.7; OWASP LLM LLM01, LLM02 |
| AAR-10 | Tool packages are pinned to a version | 1 / 2 | NIST 800-53 SR-3; OWASP LLM LLM03 |
| AAR-11 | Remote tools use encrypted transport | 0 / 2 | NIST 800-53 SC-8; SOC 2 CC6.7 |
| AAR-12 | Every tool's capabilities are inventoried | 0 / 2 | NIST 800-53 CM-8; NIST AI RMF GOVERN 1.6 |
| AAR-13 | Tool servers are still maintained upstream | 1 / 2 | NIST 800-53 SA-22, SI-2; SOC 2 CC7.1; OWASP LLM LLM03 |
| AAR-14 | Tool servers have no known vulnerabilities | 0 / 2 | NIST 800-53 RA-5, SI-2; SOC 2 CC7.1; OWASP LLM LLM03 |

---

<a id="release-bot"></a>
## Release Agent

- **ID:** `release-bot` (agent-manifest)
- **Source:** `scenario/agents.yaml`
- **Owner:** dana@example.com
- **Approval:** platform-security on 2026-06-30
- **Evidence:** `evidence/release-bot.json` (sha256 `7d32b59d462ec6cf…`)

### Access inventory

| Tool | Type | Resource | Actions | Data | Untrusted input | Egress | Recommended | Reviewer decision |
|---|---|---|---|---|:---:|:---:|---|---|
| github | source-control | `github:acme/payments-api` | delete, merge, read, write | confidential | yes |  | **Keep** | ☐ Keep ☐ Modify ☐ Revoke |

### Findings

| Check | Severity | Tool | Finding | Recommendation |
|---|---|---|---|---|
| AAR-02 | medium | (agent) | Access was last approved 104 days ago by platform-security (limit 90). | Recertify: the owner confirms each tool below is still needed. |

### Sign-off

I have reviewed each tool grant above and confirm the decisions recorded.

| Role | Name | Date |
|---|---|---|
| Agent owner | | |
| Reviewer | | |

---

<a id="mcp"></a>
## MCP host (.mcp.json)

- **ID:** `mcp` (mcp-config)
- **Source:** `scenario/.mcp.json`
- **Owner:** none recorded
- **Approval:** none recorded
- **Evidence:** `evidence/mcp.json` (sha256 `f6eeff8b8a01954f…`)

### Access inventory

| Tool | Type | Resource | Actions | Data | Untrusted input | Egress | Recommended | Reviewer decision |
|---|---|---|---|---|:---:|:---:|---|---|
| github | github | `@modelcontextprotocol/server-github` | read, write | confidential | yes | yes | **Modify** | ☐ Keep ☐ Modify ☐ Revoke |

### Findings

| Check | Severity | Tool | Finding | Recommendation |
|---|---|---|---|---|
| AAR-01 | high | (agent) | No accountable human owner is recorded for this agent. | Assign an owner who answers for what the agent does, or decommission it. |
| AAR-02 | high | (agent) | Agent access has no recorded approval. | Route the agent through access approval before its next use. |
| AAR-03 | high | github | github can write confidential data without a human approving each action. | Require human confirmation for these actions, or reduce the tool to read-only. |
| AAR-09 | high | (agent) | Exfiltration path: reads sensitive data (github), ingests untrusted content (github) and can send data out (github) with no human approval. A prompt injection in the untrusted content could leak the data. | Break the chain: split the agent, remove one leg, or require approval on every egress action. |
| AAR-13 | high | github | github runs @modelcontextprotocol/server-github, which is deprecated or archived upstream and no longer receives security fixes. | Move to ghcr.io/github/github-mcp-server, then remove this server. |
| AAR-10 | medium | github | github runs @modelcontextprotocol/server-github without a pinned version, so a new upstream release runs automatically. | Pin an exact version (npm/PyPI) or image digest and update it through change control. |
| AAR-07 | low | github | No rotation date is recorded for github.GITHUB_PERSONAL_ACCESS_TOKEN. | Record when the credential was issued so rotation can be evidenced. |
| AAR-08 | low | (agent) | No tool usage is logged, so dormant access cannot be identified. | Log tool calls per agent so unused access can be found and removed. |

### Sign-off

I have reviewed each tool grant above and confirm the decisions recorded.

| Role | Name | Date |
|---|---|---|
| Agent owner | | |
| Reviewer | | |
