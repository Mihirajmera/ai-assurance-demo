# AI Gateway Audit: 2026-10-12

**1 gateway deployment**, **3 open findings** (0 high, 2 medium, 1 low).

| Deployment | Sources | High | Medium | Low | Not assessed |
|---|---|---:|---:|---:|---:|
| [gateway](#gateway) | `config.yaml`, `docker-compose.yml` | 0 | 2 | 1 | 0 |

## Control results

| Check | Control | gateway | Frameworks |
|---|---|---|---|
| GWA-01 | Provider credentials are not stored in plain text | PASS | NIST 800-53 IA-5(7), SC-28; SOC 2 CC6.1; OWASP LLM LLM02 |
| GWA-02 | The proxy requires a master key that is not stored in plain text | PASS | NIST 800-53 AC-3, IA-2, IA-5(7); SOC 2 CC6.1; OWASP LLM LLM10 |
| GWA-03 | Prompts and responses are kept out of logs | PASS | NIST 800-53 AU-3(3), SI-12; SOC 2 C1.1; OWASP LLM LLM02 |
| GWA-04 | Provider keys are not held in the gateway database | PASS | NIST 800-53 SC-12, SC-28; SOC 2 CC6.1; OWASP LLM LLM02 |
| GWA-05 | The admin UI does not accept a shared environment login | PASS | NIST 800-53 AC-2, IA-2; SOC 2 CC6.1, CC6.2 |
| GWA-06 | Spend is capped globally and per key | FAIL | NIST 800-53 SC-6; SOC 2 A1.1; OWASP LLM LLM10 |
| GWA-07 | The gateway image is pinned by digest | FAIL | NIST 800-53 CM-2, SI-7; SOC 2 CC8.1; OWASP LLM LLM03 |
| GWA-08 | TLS certificates are verified on calls to providers | PASS | NIST 800-53 SC-8, SC-23; SOC 2 CC6.7 |
| GWA-09 | Interactive API documentation is disabled | PASS | NIST 800-53 CM-7 |
| GWA-10 | Request and upload sizes are limited | PASS | NIST 800-53 SC-5, CM-7; OWASP LLM LLM10 |
| GWA-11 | The gateway runs a LiteLLM release with no known high or critical advisory | PASS | NIST 800-53 SI-2, RA-5; SOC 2 CC7.1; OWASP LLM LLM03 |

---

<a id="gateway"></a>
## gateway

- **Folder:** `.`
- **Evidence:** `evidence/gateway.json` (sha256 `64a51e5a869fa5e0…`)
- **Sources read:**
  - `config.yaml` (litellm-config, sha256 `5ee86ccf6c511fc2…`)
  - `docker-compose.yml` (compose, sha256 `16f63581d29b1592…`)

### Findings

| Check | Severity | Finding | Recommendation | Status |
|---|---|---|---|---|
| GWA-06 | medium | There is no global spend cap. A leaked virtual key or a runaway agent can spend without limit, and stolen gateway access is used to run attackers' workloads. | Set litellm_settings.max_budget (and budget_duration) to a limit someone has approved. | **open** |
| GWA-07 | medium | Service `litellm` runs `ghcr.io/berriai/litellm:v1.106.2`, pinned by tag but not by digest. Tags can be moved to different content. | Add the digest of the reviewed image: image: …litellm:<tag>@sha256:<digest>. | **open** |
| GWA-06 | low | Virtual keys can be created with no budget limit. | Set litellm_settings.upperbound_key_generate_params.max_budget so no key can exceed it. | **open** |

## Needs evidence from outside the configuration

A configuration file can't prove these. Collect evidence for them separately:

- **M-01:** Outbound traffic from the gateway is limited to approved model providers (NIST 800-53 SC-7(5))
- **M-02:** The admin UI and management routes are not reachable from the internet (NIST 800-53 AC-17, SC-7)
- **M-03:** Provider keys are rotated and their use is monitored (NIST 800-53 IA-5(1), AU-6)
- **M-04:** The gateway database is encrypted and access to it is restricted (NIST 800-53 SC-28, AC-6)

## Sign-off

I have reviewed the findings above and the decisions recorded for each.

| Role | Name | Date |
|---|---|---|
| Gateway owner | | |
| Reviewer | | |
