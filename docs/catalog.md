---
type: Catalog
title: Catalog
description: Generated list of every page in this knowledge base with its type, description, tags and trust; read it first to find pages.
tags: [catalog, index]
status: stable
---

# Catalog

<!-- kb:catalog:start -->
## Root

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [Knowledge base conventions](conventions.md) | Guide | How pages in this knowledge base are structured, linked, attributed and reviewed. | knowledge-base, okf, conventions | draft | unverified |

## architecture/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [ADR 0001: Keep project knowledge in an OKF knowledge base under docs/](architecture/decisions/0001-knowledge-base.md) | Decision Record | Curated project knowledge lives in docs/ as an OKF bundle read by people and all agents, maintained with kb-tools; sources stay out of git; verification is optional and tracked. | adr, knowledge-base, okf, agents, tools | stable | unverified |
| [ADR 0002: Ship kb-tools as one Docker image with LibreOffice, used as CLI and MCP server](architecture/decisions/0002-docker-image-with-libreoffice.md) | Decision Record | kb-tools runs in a Docker image bundling LibreOffice and fonts, called through a per-project wrapper or as an MCP sidecar, rather than installed into each environment. | adr, docker, libreoffice, mcp | stable | unverified |
| [ADR 0003: Committed generated files are Markdown; machine output is produced on demand](architecture/decisions/0003-generated-files-markdown-with-on-demand-json.md) | Decision Record | The catalog and roadmap are committed as generated Markdown with drift-free fields; JSON or JSON Lines is printed on demand by commands rather than stored. | adr, catalog, roadmap, formats | stable | unverified |
| [ADR 0004: The repository is the record for work; trackers are synced one way](architecture/decisions/0004-repository-is-the-record-one-way-sync.md) | Decision Record | Epics, plans, items and release notes live in the repository; GitHub, Jira and Paperclip mirror them with one-way sync, each field having one owner. | adr, work-tracking, sync, trackers | stable | unverified |
| [ADR 0005: dev is the integration branch; main is the release branch](architecture/decisions/0005-dev-integration-branch-main-release-branch.md) | Decision Record | Work pull requests target dev and Chief merges them; main changes only through board-approved dev-to-main release pull requests. | adr, branching, pull-requests, releases | stable | unverified |
| [ADR 0006: kb-tools is MIT-licensed; the scaffold template ships no licence](architecture/decisions/0006-mit-license-template-ships-none.md) | Decision Record | kb-tools is released under the MIT licence (Centralus LLC, 2026); projects created with kb scaffold choose their own licence, so the template adds none. | adr, licence, public-release, scaffold | stable | unverified |
| [System overview](architecture/overview.md) | Architecture | How kb-tools is built: a Python package in a Docker image with LibreOffice, used as a CLI or as an MCP server; its components and data flow. | architecture, overview | stable | unverified |
| [Quality attributes](architecture/quality-attributes.md) | Architecture | kb-tools's non-functional requirements (performance, availability, security, privacy, accessibility, compatibility), each with a target and how it is measured. | architecture, requirements, non-functional, quality | draft | unverified |
| [Research data](architecture/research-data.md) | Architecture | Conventions for structured research data in the repository's data/ folder - dataset layout, formats, Frictionless datapackage.json descriptors, provenance, and the path to the application database. | architecture, data, research, datasets | draft | unverified |
| [Third-party licences](architecture/third-party-licences.md) | Reference | Licences of the Python dependencies and Docker image packages kb-tools uses, and why they are compatible with kb-tools' MIT licence. | licence, dependencies, docker, public-release | draft | unverified |

## business/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [Audience](business/audience.md) | Persona | Who uses kb-tools: the project owner, coding agents in a checkout, and agent-platform agents using the MCP server. | business, audience, personas | stable | unverified |
| [Branding](business/branding.md) | Guide | kb-tools's name, voice, tone and visual identity rules for product and marketing text. | business, branding, voice | draft | unverified |
| [Business model and rules](business/business-model.md) | Policy | How kb-tools is distributed and earns or saves money, and the business, legal and policy rules that constrain design. | business, model, rules, compliance | draft | unverified |
| [Vision](business/vision.md) | Overview | Why kb-tools exists, its goals, scope and non-goals. | business, vision, product | stable | unverified |

## design/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [Design system](design/design-system.md) | Design | kb-tools's visual and interaction building blocks: tokens, components and patterns, with accessibility rules. | design, design-system, ui, accessibility | draft | unverified |

## domains/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [Glossary](domains/glossary.md) | Glossary | Definitions of kb-tools's domain terms. Use these terms consistently in code, docs and UI. | domains, glossary, terminology | draft | unverified |

## environments/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [Agent dev environments](environments/agent-dev-environments.md) | Environment | How the devenv manager provides per-project dev containers for Paperclip agents on the Paperclip host: architecture, isolation, ports, MCP tools, the setup flow through Paperclip approvals, and operations. | environments, agents, paperclip, devenv, ssh, operations | draft | unverified |
| [Cloud and hosted environments](environments/cloud.md) | Environment | kb-tools's deployment targets (for example AWS, Cloudflare, an internal server) and what each environment page must record. | environments, cloud, deployment | draft | unverified |
| [Configuration](environments/configuration.md) | Environment | Every setting kb-tools reads (environment variables, config files, command-line flags) for the CLI wrapper, the MCP server and the devenv manager, with its purpose and neutral default; never deployment values or secrets. | environments, configuration, settings | draft | unverified |
| [Dev environment](environments/dev-environment.md) | Environment | kb-tools' development environment: the Dockerfile's dev stage via .devcontainer, with LibreOffice, fonts and test tools; how people and agents run the tests in it. | environments, development, devcontainer, agents | stable | unverified |
| [Local development](environments/local.md) | Environment | How to set up and run kb-tools on a local machine, including the kb-tools prerequisites. | environments, local, setup | stable | unverified |
| [Install kb-tools as an add-on in a Paperclip environment](environments/paperclip-add-on.md) | Environment | How to add kb-tools to any Paperclip environment: the MCP server on the Paperclip machine for the agent that ingests documents and takes source requests and research, the light tools/kb install in project containers, the repos root, and how a project starts using it. | environments, paperclip, mcp, install, add-on | draft | unverified |

## process/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [Agent workflow](process/agent-workflow.md) | Policy | Rules every AI agent (Claude Code, Codex, Copilot, agent-platform agents) follows before, during and after a task in this repository. | agents, policy, workflow | stable | unverified |
| [Development process](process/development.md) | Process | Branching, pull requests, code layout, testing and coding standards for kb-tools. | process, development, git | stable | unverified |
| [Ingestion](process/ingestion.md) | Process | How source documents (PowerPoint, Word, PDF, Excel, images, web pages) become knowledge pages, figures and research data, using kb-tools, with every source tracked in docs/sources/ingest-log.csv. | process, ingestion, sources, data, figures, diagrams, tools | stable | unverified |
| [Knowledge base maintenance](process/knowledge-base.md) | Process | How this knowledge base is updated and verified, and how it relates to agent memory (for example Hindsight in Paperclip). | knowledge-base, okf, agent-memory, process | draft | unverified |
| [Operations](process/operations.md) | Process | Release, deployment, monitoring, incident and access processes for kb-tools. | process, operations, release | draft | unverified |
| [Project management](process/project-management.md) | Process | How kb-tools work is planned and prioritised, who decides, and how agents take part. | process, planning | stable | unverified |
| [Release notes](process/release-notes.md) | Process | How kb-tools release notes are written as work items complete, cut into versioned releases, and updated as each release is deployed to each environment. | process, releases, changelog, deployment | stable | unverified |
| [Security](process/security.md) | Policy | Security rules for kb-tools: secrets, access, dependencies, data handling, rules for AI agents, and how to report a vulnerability. | process, security, policy | draft | unverified |
| [Testing](process/testing.md) | Policy | Testing rules for kb-tools: where tests live, what every change needs, how agents run tests, and what never to do to make tests pass. | process, testing, quality, policy | draft | unverified |
| [Work tracking](process/work-tracking.md) | Process | How kb-tools work is planned and tracked in the repository (epics, implementation plans, work items in docs/work/) and mirrored to outside trackers such as GitHub Issues, Jira or Paperclip. | process, planning, work-tracking, epics | stable | unverified |

## releases/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [Unreleased](releases/unreleased.md) | Release Notes | Changes completed in kb-tools but not yet released; each merged work item adds its entry here. | releases, changelog | stable | unverified |
| [v0.1.0](releases/v0.1.0.md) | Release Notes | First kb-tools release: ingestion, figures, checks, trust report, catalog, work tracking, scaffold template, and MCP server. | releases | stable | unverified |

## work/

| Page | Type | Description | Tags | Status | Trust |
| --- | --- | --- | --- | --- | --- |
| [0001 Tracker sync](work/epics/0001-tracker-sync/epic.md) | Epic | Mirror repository epics and items to GitHub Issues, Paperclip and Jira one way, and report drift back for triage. | epic | draft, proposed | unverified |
| [0001-01 GitHub Issues sync](work/epics/0001-tracker-sync/items/01-github-issues-sync.md) | Work Item | Mirror epics and items to GitHub Issues one way, with idempotent updates. | work-item | draft, backlog | unverified |
| [0001-02 Paperclip issues sync](work/epics/0001-tracker-sync/items/02-paperclip-issues-sync.md) | Work Item | Mirror epics and items into Paperclip so agents and the board see the same plan. | work-item | draft, backlog | unverified |
| [0001-03 Jira sync](work/epics/0001-tracker-sync/items/03-jira-sync.md) | Work Item | Mirror to Jira for projects that require it. | work-item | draft, backlog | unverified |
| [0001-04 Drift report from trackers](work/epics/0001-tracker-sync/items/04-drift-report-from-trackers.md) | Work Item | Surface drift and externally filed issues as a report to triage. | work-item | draft, backlog | unverified |
| [0001-05 Validate trackers.yaml in kb check](work/epics/0001-tracker-sync/items/05-validate-trackers-yaml-in-kb-check.md) | Work Item | Catch configuration mistakes before sync runs. | work-item | draft, backlog | unverified |
| [Plan: Tracker sync](work/epics/0001-tracker-sync/plan.md) | Implementation Plan | Draft plan for epic 0001: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0002 Image distribution and versioning](work/epics/0002-image-distribution-and-versioning/epic.md) | Epic | Build, test and publish versioned multi-architecture kb-tools images so projects stop building the image locally and pin a known version. | epic | draft, proposed | unverified |
| [0002-01 Build and test the image in CI for arm64 and amd64](work/epics/0002-image-distribution-and-versioning/items/01-build-and-test-the-image-in-ci-for-arm64-and-amd.md) | Work Item | Prove both architectures build and pass tests before release. | work-item | draft, backlog | unverified |
| [0002-02 Publish versioned images to GHCR](work/epics/0002-image-distribution-and-versioning/items/02-publish-versioned-images-to-ghcr.md) | Work Item | Make images available without local builds. | work-item | draft, backlog | unverified |
| [0002-03 Wrapper pins and pulls an image version](work/epics/0002-image-distribution-and-versioning/items/03-wrapper-pins-and-pulls-an-image-version.md) | Work Item | Projects use a known kb-tools version. | work-item | draft, backlog | unverified |
| [0002-04 kb-tools release process](work/epics/0002-image-distribution-and-versioning/items/04-kb-tools-release-process.md) | Work Item | Releases of kb-tools are predictable and documented. | work-item | draft, backlog | unverified |
| [Plan: Image distribution and versioning](work/epics/0002-image-distribution-and-versioning/plan.md) | Implementation Plan | Draft plan for epic 0002: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0003 Paperclip ingestion end to end](work/epics/0003-paperclip-ingestion-end-to-end/epic.md) | Epic | Make document ingestion work end to end for Paperclip agents: MCP connection, repository workspace, review packet, and a real trial. | epic | draft, proposed | unverified |
| [0003-01 Register the kb-tools MCP connection and tool policy](work/epics/0003-paperclip-ingestion-end-to-end/items/01-register-the-kb-tools-mcp-connection-and-tool-po.md) | Work Item | Agents can see and call the kb_* tools. | work-item | draft, backlog | unverified |
| [0003-02 Paperclip project with a repository workspace](work/epics/0003-paperclip-ingestion-end-to-end/items/02-paperclip-project-with-a-repository-workspace.md) | Work Item | Agents work on a real repository checkout the sidecar can reach. | work-item | draft, backlog | unverified |
| [0003-03 Review packet for ingestion](work/epics/0003-paperclip-ingestion-end-to-end/items/03-review-packet-for-ingestion.md) | Work Item | Reviewers can check an ingestion at a glance, optionally. | work-item | draft, backlog | unverified |
| [0003-04 End-to-end ingestion trial](work/epics/0003-paperclip-ingestion-end-to-end/items/04-end-to-end-ingestion-trial.md) | Work Item | Find the gaps before relying on the flow. | work-item | draft, backlog | unverified |
| [Plan: Paperclip ingestion end to end](work/epics/0003-paperclip-ingestion-end-to-end/plan.md) | Implementation Plan | Draft plan for epic 0003: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0004 Continuous integration for project repositories](work/epics/0004-continuous-integration-for-project-repositories/epic.md) | Epic | Run kb check and definition-of-done checks in project repositories' CI so conventions are enforced on every pull request. | epic | draft, proposed | unverified |
| [0004-01 Reusable GitHub Action running kb check](work/epics/0004-continuous-integration-for-project-repositories/items/01-reusable-github-action-running-kb-check.md) | Work Item | Enforce knowledge-base conventions on every pull request. | work-item | draft, backlog | unverified |
| [0004-02 Definition-of-done checks for pull requests](work/epics/0004-continuous-integration-for-project-repositories/items/02-definition-of-done-checks-for-pull-requests.md) | Work Item | Make the definition of done checkable. | work-item | draft, backlog | unverified |
| [Plan: Continuous integration for project repositories](work/epics/0004-continuous-integration-for-project-repositories/plan.md) | Implementation Plan | Draft plan for epic 0004: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0005 Template upgrades for existing repositories](work/epics/0005-template-upgrades-for-existing-repositories/epic.md) | Epic | Let repositories scaffolded from an older template see and adopt template changes without overwriting their own edits. | epic | draft, proposed | unverified |
| [0005-01 Record the template version in scaffolded repositories](work/epics/0005-template-upgrades-for-existing-repositories/items/01-record-the-template-version-in-scaffolded-reposi.md) | Work Item | Know which template a repository started from. | work-item | draft, backlog | unverified |
| [0005-02 kb scaffold --diff to show template changes](work/epics/0005-template-upgrades-for-existing-repositories/items/02-kb-scaffold-diff-to-show-template-changes.md) | Work Item | Adopt template improvements safely. | work-item | draft, backlog | unverified |
| [0005-03 Upgrade guide](work/epics/0005-template-upgrades-for-existing-repositories/items/03-upgrade-guide.md) | Work Item | Make upgrades repeatable for people and agents. | work-item | draft, backlog | unverified |
| [Plan: Template upgrades for existing repositories](work/epics/0005-template-upgrades-for-existing-repositories/plan.md) | Implementation Plan | Draft plan for epic 0005: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0006 Extraction improvements](work/epics/0006-extraction-improvements/epic.md) | Epic | Close the extraction gaps from the earlier extraction guide: OCR for raster pages, duplicate detection, web capture, Word tracked-change views, and better Excel rendering. | epic | draft, proposed | unverified |
| [0006-01 Local OCR for raster-only pages](work/epics/0006-extraction-improvements/items/01-local-ocr-for-raster-only-pages.md) | Work Item | Raster-only pages become searchable without sending documents out. | work-item | draft, backlog | unverified |
| [0006-02 Duplicate source detection](work/epics/0006-extraction-improvements/items/02-duplicate-source-detection.md) | Work Item | Avoid duplicate ingestion of the same deck in different formats. | work-item | draft, backlog | unverified |
| [0006-03 Web page capture](work/epics/0006-extraction-improvements/items/03-web-page-capture.md) | Work Item | Preserve the version of a web page that was actually reviewed. | work-item | draft, backlog | unverified |
| [0006-04 Word tracked changes: markup and accepted views](work/epics/0006-extraction-improvements/items/04-word-tracked-changes-markup-and-accepted-views.md) | Work Item | Ingest the intended document version, with history available. | work-item | draft, backlog | unverified |
| [0006-05 Evaluate ExStruct and Excel-native rendering](work/epics/0006-extraction-improvements/items/05-evaluate-exstruct-and-excel-native-rendering.md) | Work Item | Decide whether better workbook fidelity is worth a Windows or Excel dependency. | work-item | draft, backlog | unverified |
| [Plan: Extraction improvements](work/epics/0006-extraction-improvements/plan.md) | Implementation Plan | Draft plan for epic 0006: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0007 Release notes automation](work/epics/0007-release-notes-automation/epic.md) | Epic | Automate the release-notes process: cut a release from Unreleased and record deployments. | epic | draft, proposed | unverified |
| [0007-01 kb release cut](work/epics/0007-release-notes-automation/items/01-kb-release-cut.md) | Work Item | Releases are cut consistently. | work-item | draft, backlog | unverified |
| [0007-02 kb release deploy](work/epics/0007-release-notes-automation/items/02-kb-release-deploy.md) | Work Item | Anyone can see what is live where. | work-item | draft, backlog | unverified |
| [Plan: Release notes automation](work/epics/0007-release-notes-automation/plan.md) | Implementation Plan | Draft plan for epic 0007: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0008 Structured fact extraction](work/epics/0008-structured-fact-extraction/epic.md) | Epic | Optional schema-driven fact extraction from extraction packages with LangExtract, using the local model by default. | epic | draft, proposed | unverified |
| [0008-01 kb facts with LangExtract profiles](work/epics/0008-structured-fact-extraction/items/01-kb-facts-with-langextract-profiles.md) | Work Item | Repeatable fact extraction without one-off scripts. | work-item | draft, backlog | unverified |
| [0008-02 Default to the local model through the gateway](work/epics/0008-structured-fact-extraction/items/02-default-to-the-local-model-through-the-gateway.md) | Work Item | Keep confidential material local. | work-item | draft, backlog | unverified |
| [Plan: Structured fact extraction](work/epics/0008-structured-fact-extraction/plan.md) | Implementation Plan | Draft plan for epic 0008: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0009 Semantic search through Hindsight](work/epics/0009-semantic-search-through-hindsight/epic.md) | Epic | Deferred: semantic search over knowledge bases through a per-repository Hindsight bank, only when grep and the catalog fall short. | epic | draft, proposed | unverified |
| [0009-01 Measure when grep and the catalog fall short](work/epics/0009-semantic-search-through-hindsight/items/01-measure-when-grep-and-the-catalog-fall-short.md) | Work Item | Build semantic search only when it pays. | work-item | draft, backlog | unverified |
| [0009-02 kb sync-index into a per-repository Hindsight bank](work/epics/0009-semantic-search-through-hindsight/items/02-kb-sync-index-into-a-per-repository-hindsight-ba.md) | Work Item | Semantic search over one repository's knowledge base. | work-item | draft, backlog | unverified |
| [0009-03 Cross-repository search](work/epics/0009-semantic-search-through-hindsight/items/03-cross-repository-search.md) | Work Item | Find knowledge across all projects. | work-item | draft, backlog | unverified |
| [Plan: Semantic search through Hindsight](work/epics/0009-semantic-search-through-hindsight/plan.md) | Implementation Plan | Draft plan for epic 0009: approach, design, sequencing, risks and verification. | plan | draft | unverified |
| [0010 Agent dev environments](work/epics/0010-agent-dev-environments/epic.md) | Epic | TODO: one sentence on the business need behind Agent dev environments. | epic | draft, in_progress | unverified |
| [0010-01 Isolated agentdev account with rootless Docker and egress rules](work/epics/0010-agent-dev-environments/items/01-isolated-agentdev-account-with-rootless-docker-a.md) | Work Item | TODO: one sentence on what 0010-01 delivers. | work-item | draft, done | unverified |
| [0010-02 Dev container overlay that adds sshd, node and the claude CLI to any project image](work/epics/0010-agent-dev-environments/items/02-dev-container-overlay-that-adds-sshd-node-and-th.md) | Work Item | TODO: one sentence on what 0010-02 delivers. | work-item | draft, done | unverified |
| [0010-03 devenv manager MCP service (create, status, rebuild, install, stop)](work/epics/0010-agent-dev-environments/items/03-devenv-manager-mcp-service-create-status-rebuild.md) | Work Item | An MCP service in the agentdev account that creates, rebuilds, installs into, stops and deletes per-project dev containers, with per-project keys and builds from the synced worktree. | work-item | draft, done | unverified |
| [0010-04 kb-tools .devcontainer and the dev target](work/epics/0010-agent-dev-environments/items/04-kb-tools-devcontainer-and-the-dev-target.md) | Work Item | TODO: one sentence on what 0010-04 delivers. | work-item | draft, done | unverified |
| [0010-05 Run the kb-tools test suite through a Paperclip SSH environment](work/epics/0010-agent-dev-environments/items/05-run-the-kb-tools-test-suite-through-a-paperclip.md) | Work Item | Proves a Paperclip agent can run the kb-tools test suite in its remote dev container and push the result back to GitHub. | work-item | draft, done | unverified |
| [0010-06 Approval-gated system package installs](work/epics/0010-agent-dev-environments/items/06-approval-gated-system-package-installs.md) | Work Item | Agents install system packages into their dev container with devenv_install, and Paperclip asks a human first for that and the other lifecycle tools. | work-item | draft, blocked | unverified |
| [0010-07 .devcontainer in the scaffold template](work/epics/0010-agent-dev-environments/items/07-devcontainer-in-the-scaffold-template-and-gamewo.md) | Work Item | kb scaffold gives every new project a generic .devcontainer/ that the devenv manager can build. | work-item | draft, todo | unverified |
| [0010-08 Detect projects without a dev environment and request one](work/epics/0010-agent-dev-environments/items/08-detect-projects-without-a-dev-environment-and-re.md) | Work Item | Agents notice when their project has no working dev environment and get one created through the devenv manager, instead of skipping tests. | work-item | draft, done | unverified |
| [0010-09 Sandbox-provider plugin for Paperclip backed by the devenv manager](work/epics/0010-agent-dev-environments/items/09-sandbox-provider-plugin-for-paperclip-backed-by.md) | Work Item | Not ready for development: a Paperclip sandbox-provider plugin (environment driver) that uses the devenv manager as its backend, so projects just pick an environment. | work-item | draft, backlog | unverified |
| [0010-10 Purge client-project references from the repository, including history](work/epics/0010-agent-dev-environments/items/10-purge-client-project-references-including-history.md) | Work Item | Remove every reference to an earlier client project from the working tree and from git history with one filter-repo rewrite, approved by the owner before the force-push. | work-item | draft, in_progress | unverified |
| [0010-11 Audit for Centralus secrets and internal references](work/epics/0010-agent-dev-environments/items/11-audit-for-centralus-secrets-and-internal-referen.md) | Work Item | Find Centralus secrets and internal references (local LLM endpoints, hostnames, private IPs, internal URLs, IDs, names, tokens) in the tree and full history, fix each one, and add a repeatable scan. | work-item | draft, done | unverified |
| [0010-12 Add an MIT license](work/epics/0010-agent-dev-environments/items/12-add-an-mit-license.md) | Work Item | License kb-tools under MIT: a root LICENSE, pyproject metadata, a README section and the image label. | work-item | draft, in_review | unverified |
| [0010-13 Make deployment-specific settings configurable](work/epics/0010-agent-dev-environments/items/13-make-deployment-specific-settings-configurable.md) | Work Item | Keep the devenv manager and the Paperclip host deployment, but supply every deployment-specific host, IP, port and URL through environment variables with neutral defaults, so the public repository carries no Centralus values. | work-item | draft, in_review | unverified |
| [0010-14 kb CLI available inside project dev containers](work/epics/0010-agent-dev-environments/items/14-kb-cli-available-inside-project-dev-containers.md) | Work Item | Make the kb CLI (check, catalog, work, report) runnable inside a project's dev container against its own repository, through the scaffold template, without Docker in the container. | work-item | draft, done | unverified |
| [0010-15 Upgrade path for projects set up before tools/kb.conf](work/epics/0010-agent-dev-environments/items/15-upgrade-path-for-projects-set-up-before-tools-kb.md) | Work Item | Fix the issues found by gameworld's reinstall check of 0010-13 and 0010-11 on dev: upgrading a project set up by an older kb-tools, the ref scaffold records, the scan's scope, and updating tools/kb from a project container. | work-item | draft, done | unverified |
| [0010-16 Librarian process in the scaffold template for every project](work/epics/0010-agent-dev-environments/items/16-librarian-process-in-the-scaffold-template-for-e.md) | Work Item | Every scaffolded project routes ingestion, source requests and research to the ingesting agent (for example a Librarian): a template process page, an AGENTS.md section, and add-on guide steps. | work-item | draft, done | unverified |
| [Plan: Agent dev environments](work/epics/0010-agent-dev-environments/plan.md) | Implementation Plan | How agents get complete dev environments in Paperclip: an isolated account, a devenv manager building per-project dev containers from .devcontainer, Paperclip SSH environments, and approval-gated installs. | plan | draft | unverified |
| [0011 MCP tool parity with the CLI](work/epics/0011-mcp-tool-parity-with-the-cli/epic.md) | Epic | Agents that use kb-tools through MCP can do what the kb CLI does, so they stop hand-editing generated files. | epic | draft, done | unverified |
| [0011-01 kb_catalog MCP tool can write docs/catalog.md](work/epics/0011-mcp-tool-parity-with-the-cli/items/01-kb-catalog-mcp-tool-can-write-docs-catalog-md.md) | Work Item | The kb_catalog MCP tool gains a write option that regenerates docs/catalog.md, matching kb catalog --write. | work-item | draft, done | unverified |
| [Plan: MCP tool parity with the CLI](work/epics/0011-mcp-tool-parity-with-the-cli/plan.md) | Implementation Plan | How epic 0011 will be delivered: approach, design, risks and sequencing of its items. | plan | draft | unverified |
| [0012 Development workflow](work/epics/0012-development-workflow/epic.md) | Epic | How changes reach kb-tools: branches, pull requests, who merges, and how releases reach main. | epic | draft, done | unverified |
| [0012-01 Document the dev-branch workflow](work/epics/0012-development-workflow/items/01-document-the-dev-branch-workflow.md) | Work Item | AGENTS.md and the process pages describe the dev-branch workflow: branch from and PR into dev, Chief merges, dev to main releases need board approval. | work-item | draft, done | unverified |
| [0012-02 Reconcile work-item statuses with delivered work](work/epics/0012-development-workflow/items/02-reconcile-work-item-statuses-with-delivered-work.md) | Work Item | Make every epic and item status in docs/work match what is actually done, checked against code, merged pull requests and Paperclip tasks. | work-item | draft, done | unverified |
| [Plan: Development workflow](work/epics/0012-development-workflow/plan.md) | Implementation Plan | How epic 0012 will be delivered: approach, design, risks and sequencing of its items. | plan | draft | unverified |
<!-- kb:catalog:end -->
