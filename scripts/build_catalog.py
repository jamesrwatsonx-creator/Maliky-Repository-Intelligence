"""Generate public, browsable catalog views from the canonical registry.

The registry remains authoritative. Every Markdown page, JSON export and static
search page produced here is a disposable view rebuilt by this script.
"""
from __future__ import annotations

import collections
import html
import json
import pathlib
import posixpath
import re
import sys
from urllib.parse import quote

import registry as r

ROOT = r.ROOT
PAGE_SIZE = 150
PUBLISH_BRANCH = "recovery/v1-rebuild"
GITHUB_REPOSITORY = "jamesrwatsonx-creator/Maliky-Repository-Intelligence"
TYPE_SPECS = [
    ("skills", "Skills", {"SKILL"}),
    ("mcps", "MCP Servers", {"MCP_SERVER"}),
    ("plugins", "Plugins", {"PLUGIN"}),
    ("agents", "Agents & Frameworks", {"AGENT", "AGENT_FRAMEWORK"}),
    ("tools", "Tools", {"TOOL", "CLI"}),
    ("apis", "APIs", {"API"}),
    ("sdks", "SDKs", {"SDK"}),
    ("ui-components", "UI Components", {"UI_COMPONENT", "MOBILE_COMPONENT", "COMPONENT"}),
    ("workflows", "Workflows", {"WORKFLOW"}),
    ("templates", "Templates", {"TEMPLATE"}),
    ("models", "Models & Model Adapters", {"MODEL", "MODEL_ADAPTER"}),
    ("libraries", "Libraries & Packages", {"LIBRARY", "PACKAGE"}),
    ("services", "Services & Integrations", {"SERVICE", "INTEGRATION", "CONNECTOR"}),
    ("prompts", "Prompts", {"PROMPT", "PROMPT_LIBRARY"}),
]

# Topic sections are navigation facets, not a second taxonomy. Matching uses
# existing entity/repository metadata and evidence-backed registry labels.
TOPICS = [
    ("android", "Android", "Android apps, libraries, skills and platform tooling.", ["android", "jetpack compose", "androidx", "gradle", "adb", "kotlin android", "wear os"], ["operational:19"], {"MOBILE_COMPONENT"}),
    ("ios", "iOS", "iOS apps, Swift components and Apple platform tooling.", ["ios", "swiftui", "swift package", "xcode", "iphone", "ipad", "watchos"], ["operational:19"], set()),
    ("react-native", "React Native", "React Native applications, components and tooling.", ["react native", "react-native", "nativewind"], ["operational:19"], set()),
    ("expo", "Expo", "Expo applications, modules, templates and workflows.", ["expo", "expo router", "expo go"], ["operational:19"], set()),
    ("flutter", "Flutter", "Flutter and Dart applications, packages and UI components.", ["flutter", "dart", "pubspec"], ["operational:19"], set()),
    ("wearables", "Wearables", "Wear OS, watchOS and wearable device projects.", ["wearable", "wear os", "watchos", "smartwatch", "apple watch"], ["operational:06"], set()),
    ("websites", "Websites", "Website projects, templates, components and references.", ["website", "web site", "homepage", "web design"], ["operational:16"], {"WEBSITE"}),
    ("web-apps", "Web Apps", "Browser-based applications, frontend and full-stack projects.", ["web app", "web application", "next.js", "nextjs", "single page app", "frontend application"], ["operational:16"], {"APP"}),
    ("website-inspiration", "Website Inspiration", "Visual website references and inspiration collections.", ["website inspiration", "web inspiration", "website reference", "site gallery", "web design reference"], [], {"WEBSITE_REFERENCE", "DESIGN_REFERENCE"}),
    ("landing-page-inspiration", "Landing Page Inspiration", "Landing pages, hero sections and marketing-site references.", ["landing page", "landing-page", "hero section", "homepage inspiration", "marketing site"], [], {"WEBSITE_REFERENCE", "DESIGN_REFERENCE"}),
    ("ui-ux", "UI/UX", "Reusable interface components, patterns, screens and UX resources.", ["ui/ux", "ui ux", "user interface", "user experience", "design system", "component library", "ui component"], ["operational:16"], {"UI_COMPONENT", "MOBILE_COMPONENT", "COMPONENT", "UI_PATTERN", "SCREEN_REFERENCE", "DESIGN_SYSTEM"}),
    ("design-systems", "Design Systems", "Design tokens, component systems and brand-specific design references.", ["design system", "design tokens", "design language", "component system"], ["operational:17"], {"DESIGN_SYSTEM", "DESIGN_REFERENCE"}),
    ("fonts-icons-branding", "Fonts, Icons & Branding", "Typography, icon sets, illustrations and identity resources.", ["font", "typeface", "icon", "icon pack", "branding", "brand identity", "illustration"], [], set()),
    ("animation-motion", "Animation & Motion", "Animation libraries, motion systems and interaction effects.", ["animation", "motion design", "gsap", "framer motion", "lottie", "transition", "scroll animation"], ["operational:17"], set()),
    ("3d-xr", "3D & XR", "Three-dimensional graphics, rendering, augmented and virtual reality.", ["3d", "three.js", "threejs", "webgl", "webgpu", "xr", "ar/vr", "rendering"], ["operational:18"], set()),
    ("mobile-references", "Mobile References", "Mobile screen references, app patterns and device interface examples.", ["mobile reference", "mobile screen", "app screen", "mobile ui", "android ui", "ios ui"], ["operational:19"], {"SCREEN_REFERENCE", "MOBILE_COMPONENT"}),
    ("ai-agents", "AI Agents", "Agents, agent tools and reusable agent capabilities.", ["ai agent", "agentic", "multi-agent", "autonomous agent"], ["operational:03"], {"AGENT"}),
    ("agent-frameworks", "Agent Frameworks", "Frameworks and orchestration systems for building agents.", ["agent framework", "agent orchestration", "orchestration framework", "agent runtime"], ["operational:03"], {"AGENT_FRAMEWORK"}),
    ("memory", "Memory & Context", "Memory, context management, knowledge and retrieval systems.", ["memory", "context management", "knowledge graph", "conversation history", "long-term memory"], ["operational:04"], set()),
    ("models-local-llms", "Models & Local LLMs", "Models, local inference, adapters and model routing.", ["local llm", "language model", "model adapter", "inference", "ollama", "llama.cpp", "vllm", "model routing"], ["operational:15"], {"MODEL", "MODEL_ADAPTER"}),
    ("search-indexing", "Search & Indexing", "Search, retrieval, indexing and discovery capabilities.", ["search", "indexing", "retrieval", "full-text", "semantic search", "search engine"], ["operational:10", "operational:13"], set()),
    ("browser-automation", "Browser Automation", "Browser control, computer use, testing and web interaction.", ["browser automation", "computer use", "playwright", "puppeteer", "browser agent", "chrome devtools"], ["operational:05"], set()),
    ("research-scraping", "Research & Scraping", "Research tools, web scraping, crawlers and data collection.", ["web scraping", "scraping", "crawler", "web research", "research agent", "web extraction"], ["operational:10"], set()),
    ("prompts-workflows", "Prompts & Workflows", "Prompt libraries, agent workflows and reusable procedures.", ["prompt", "workflow", "slash command", "playbook", "automation recipe"], ["operational:20"], {"PROMPT", "PROMPT_LIBRARY", "WORKFLOW"}),
    ("voice-stt-tts", "Voice, STT & TTS", "Speech interfaces, transcription, speech generation and voice agents.", ["voice", "speech to text", "text to speech", "stt", "tts", "transcription", "voice agent", "speech recognition"], ["operational:07"], set()),
    ("audio-music", "Audio & Music", "Audio processing, music generation, playback and sound tools.", ["audio", "music generation", "music", "sound effect", "audio processing", "podcast"], ["operational:07"], set()),
    ("vision-ocr", "Vision & OCR", "Image understanding, computer vision, document vision and OCR.", ["computer vision", "vision", "ocr", "optical character", "image understanding", "object detection"], ["operational:08"], set()),
    ("images", "Images", "Image generation, editing, processing and asset libraries.", ["image generation", "image editing", "image processing", "image assets", "image library"], ["operational:08"], set()),
    ("video", "Video", "Video creation, editing, generation, playback and media processing.", ["video", "video generation", "video editing", "video player", "media processing"], ["operational:09"], set()),
    ("realtime", "Realtime", "Realtime messaging, streaming, collaboration and low-latency systems.", ["realtime", "real-time", "websocket", "live streaming", "low latency", "webrtc"], ["operational:12"], set()),
    ("backend", "Backend", "Backend applications, services, APIs and server-side components.", ["backend", "server-side", "microservice", "api server", "http service"], ["operational:12"], {"SERVICE"}),
    ("apis-sdks", "APIs & SDKs", "API surfaces, client SDKs and service integrations.", ["api", "sdk", "integration", "rest api", "graphql", "client library"], ["operational:12"], {"API", "SDK", "CONNECTOR", "INTEGRATION"}),
    ("databases-etl", "Databases & ETL", "Databases, storage, data pipelines and ETL/ELT tooling.", ["database", "postgres", "sqlite", "mongodb", "etl", "elt", "data pipeline", "data ingestion"], ["operational:13"], set()),
    ("security-identity", "Security & Identity", "Authentication, authorization, identity and security tooling.", ["security", "authentication", "authorization", "identity", "oauth", "passkey", "encryption"], ["operational:21"], set()),
    ("infrastructure", "Infrastructure", "Cloud, infrastructure, containers, CI and platform operations.", ["infrastructure", "docker", "kubernetes", "cloud", "terraform", "ci/cd", "continuous integration"], ["operational:14"], {"INFRASTRUCTURE_MODULE"}),
    ("deployment", "Deployment", "Deployment workflows, hosting, packaging and release automation.", ["deployment", "deploy", "hosting", "release automation", "container", "helm chart"], ["operational:14"], set()),
    ("testing-developer-tools", "Testing & Developer Tools", "Testing, evaluation, QA and tools that improve software development.", ["testing", "test framework", "developer tool", "codegen", "lint", "debugging", "evaluation", "qa"], ["operational:23", "operational:24"], {"TOOL", "CLI"}),
    ("business-crm-marketing", "Business, CRM & Marketing", "Business systems, CRM, sales, marketing and commerce tools.", ["business", "crm", "marketing", "sales", "commerce", "lead generation", "customer relationship"], ["operational:11"], set()),
    ("finance-blockchain-crypto", "Finance, Blockchain & Crypto", "Finance, trading, blockchain, crypto and wallet capabilities.", ["finance", "trading", "blockchain", "crypto", "cryptocurrency", "wallet", "defi"], ["operational:22"], set()),
    ("productivity-automation", "Productivity & Automation", "Productivity tools, office workflows and task automation.", ["productivity", "automation", "office", "task management", "workflow automation", "spreadsheet"], ["operational:20"], set()),
    ("documentation", "Documentation & References", "Technical documentation, guides and reference material.", ["documentation", "technical guide", "reference implementation", "tutorial", "developer docs"], [], {"DOCUMENTATION_ASSET", "DESIGN_REFERENCE", "REFERENCE_IMPLEMENTATION"}),
    ("experimental", "Experimental", "Experimental projects and emerging technology explorations.", ["experimental", "experiment", "prototype", "proof of concept", "research prototype"], [], set()),
]


def read(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def records(kind: str):
    folder = ROOT / "registry" / kind
    return [json.loads(p.read_text(encoding="utf-8")) for p in folder.glob("*.json")]


def slug(value: str) -> str:
    value = value.lower().replace("&", " and ").replace("/", " ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def clean(value, limit=260):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    value = value.replace("|", "\\|")
    if len(value) > limit:
        value = value[: limit - 1].rsplit(" ", 1)[0] + "…"
    return value


def words(value):
    return set(re.findall(r"[a-z0-9]+", str(value).lower()))


def has_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.lower().strip()
    if not phrase:
        return False
    # Short keyword matching is token based to avoid e.g. "ios" matching "repositories".
    if " " not in phrase and len(phrase) <= 4:
        return phrase in words(text)
    return phrase in text.lower()


def canonical_entity_url(entity):
    return canonical_record_url("registry/entities/" + entity["id"] + ".json")


def canonical_record_url(path):
    return f"https://github.com/{GITHUB_REPOSITORY}/blob/{PUBLISH_BRANCH}/{quote(path, safe='/') }"


def source_url(source):
    path = quote(source.get("source_path", ""), safe="/!$&'()*+,;=:@-._~")
    url = source.get("repository_url", "") + "/blob/" + source.get("inspected_commit", "") + "/" + path
    if source.get("line"):
        url += "#L" + str(source["line"])
    return url


def topic_matches(item, topic):
    _, _, _, keywords, op_ids, entity_types = topic
    haystack = item["search_text"].lower()
    return (
        any(has_phrase(haystack, k) for k in keywords)
        or item.get("operational_category") in op_ids
        or item.get("entity_type") in entity_types
    )


def repo_descriptions(repos, entities_by_repo):
    descs = {}
    for repo in repos:
        value = clean(repo.get("description"), 360)
        status = "METADATA"
        if value:
            status = "GITHUB_DESCRIPTION"
        else:
            group = entities_by_repo.get(repo["id"], [])
            meaningful = [e for e in group if e.get("description")]
            if meaningful:
                kinds = sorted({e["entity_type"].replace("_", " ").lower() for e in meaningful})
                examples = ", ".join(clean(e["name"], 60) for e in meaningful[:3])
                value = f"Catalog evidence identifies {len(group)} reusable assets across {', '.join(kinds[:5])}; examples include {examples}."
                status = "DERIVED_FROM_CATALOGED_ASSETS"
            else:
                value = "Purpose not established from the available public metadata. NEEDS DESCRIPTION."
                status = "NEEDS_DESCRIPTION"
        descs[repo["id"]] = (value, status)
    return descs


def make_catalog():
    repos = sorted((x for x in records("repositories") if x.get("visibility") == "public"), key=lambda x: x["full_name"].lower())
    repo_by_id = {x["id"]: x for x in repos}
    cap_map = {x["id"]: x for x in records("capabilities")}
    operational = {x["id"]: x["name"] for x in read("registry/taxonomy/operational.json", [])}
    categories = {x["id"]: x["name"] for x in read("registry/taxonomy/categories.json", [])}
    all_entities = records("entities")
    active = [e for e in all_entities if e.get("source", {}).get("repository_id") in repo_by_id and e.get("source", {}).get("inspected_commit") == repo_by_id[e["source"]["repository_id"]].get("inspected_commit")]
    by_repo = collections.defaultdict(list)
    for entity in active:
        by_repo[entity["source"]["repository_id"]].append(entity)
    descriptions = repo_descriptions(repos, by_repo)
    repo_items = []
    for repo in repos:
        desc, desc_status = descriptions[repo["id"]]
        cat_names = [categories.get(x, x) for x in repo.get("categories", [])]
        caps = [cap_map[x]["name"] for x in repo.get("capabilities", []) if x in cap_map]
        repo_items.append({
            "id": repo["id"], "kind": "repository", "asset_type": "Repository", "entity_type": "REPOSITORY",
            "name": repo["full_name"], "description": desc, "description_status": desc_status,
            "repository": repo["full_name"], "repository_url": repo["url"], "repository_record": canonical_record_url("registry/repositories/" + str(repo["github_id"]) + ".json"),
            "source_path": "", "source_url": repo["url"], "upstream_url": repo.get("upstream_url"),
            "language": repo.get("metadata", {}).get("language"), "technology": repo.get("metadata", {}).get("language"),
            "review_status": repo.get("state", "DISCOVERED"), "repository_state": repo.get("state", "DISCOVERED"),
            "evidence_status": "PINNED_SOURCE" if repo.get("inspected_commit") else "PUBLIC_METADATA_ONLY",
            "inspected_commit": repo.get("inspected_commit"), "inspection_date": repo.get("inspection_date"),
            "pushed_at": repo.get("metadata", {}).get("pushed_at"),
            "categories": cat_names, "operational_category": repo.get("operational_category"),
            "operational_category_name": operational.get(repo.get("operational_category")),
            "asset_types": sorted({e["entity_type"] for e in by_repo.get(repo["id"], [])}),
            "capabilities": caps, "recommendation": repo.get("recommendation"),
        })
    entity_items = []
    for entity in active:
        src = entity["source"]
        repo = repo_by_id[src["repository_id"]]
        cat_names = [categories.get(x, x) for x in entity.get("categories", [])]
        cap_names = [cap_map[x]["name"] for x in entity.get("capabilities", []) if x in cap_map]
        description = clean(entity.get("description"), 360) or (cap_names[0] if cap_names else "Description not available in current evidence.")
        entity_items.append({
            "id": entity["id"], "kind": "asset", "asset_type": entity["entity_type"].replace("_", " ").title(),
            "entity_type": entity["entity_type"], "name": entity["name"], "description": description,
            "description_status": "REGISTRY_DESCRIPTION" if entity.get("description") else "NEEDS_DESCRIPTION",
            "record_url": canonical_entity_url(entity), "canonical_record": "registry/entities/" + entity["id"] + ".json", "repository": src["repository_name"],
            "repository_url": src["repository_url"], "repository_record": canonical_record_url("registry/repositories/" + str(repo["github_id"]) + ".json"),
            "source_path": src["source_path"], "source_url": source_url(src), "upstream_url": src.get("upstream_url") or repo.get("upstream_url"),
            "language": repo.get("metadata", {}).get("language"), "technology": ", ".join(entity.get("metadata", {}).get("technologies", []) or [repo.get("metadata", {}).get("language") or ""]),
            "review_status": entity.get("review_status", "NEEDS_REVIEW"), "evidence_status": "PINNED_SOURCE" if src.get("blob_sha") and src.get("inspected_commit") else "INCOMPLETE_PROVENANCE",
            "inspected_commit": src.get("inspected_commit"), "inspection_date": src.get("inspection_date"), "blob_sha": src.get("blob_sha"),
            "categories": cat_names, "operational_category": entity.get("operational_category"),
            "operational_category_name": operational.get(entity.get("operational_category")),
            "capabilities": cap_names, "capability_ids": entity.get("capabilities", []),
            "recommendation": entity.get("recommendation"), "metadata": entity.get("metadata", {}),
        })
    # Attach generated facets/search text after the semantic fields are complete.
    items = repo_items + entity_items
    topics_by_id = collections.defaultdict(list)
    for item in items:
        item["search_text"] = " ".join(filter(None, [item["name"], item.get("asset_type", ""), item.get("entity_type", ""), item["description"], item["repository"], item.get("source_path", ""), item.get("technology", ""), item.get("language", ""), " ".join(item.get("categories", [])), item.get("operational_category_name", ""), " ".join(item.get("capabilities", [])), " ".join(item.get("asset_types", []))]))
        item["topics"] = []
        for topic in TOPICS:
            if topic_matches(item, topic):
                item["topics"].append(topic[0])
                topics_by_id[topic[0]].append(item)
        topic_names = [name for slug_, name, *_ in TOPICS if slug_ in item["topics"]]
        item["search_text"] += " " + " ".join(topic_names)
    capability_export = [{"id": c["id"], "name": c["name"], "description": c.get("description", ""), "aliases": c.get("aliases", []), "status": c.get("status"), "providers": [x for x in c.get("providers", []) if x in repo_by_id or any(e["id"] == x for e in active)]} for c in cap_map.values()]
    return {
        "schema_version": 1, "generated_at": r.now(),
        "source_of_truth": "registry/repositories, registry/entities, registry/capabilities and registry/taxonomy",
        "privacy": "Public repository records and active entities only; private identities and evidence excluded.",
        "counts": {"repositories": len(repo_items), "assets": len(entity_items), "all_items": len(items), "capabilities": len(capability_export), "needs_description_repositories": sum(x["description_status"] == "NEEDS_DESCRIPTION" for x in repo_items)},
        "asset_types": [{"slug": s, "name": n, "count": sum(e.get("entity_type") in kinds for e in active)} for s, n, kinds in TYPE_SPECS if any(e.get("entity_type") in kinds for e in active)],
        "canonical_categories": [{"id": c["id"], "name": c["name"], "count": sum(x.get("operational_category") == c["id"] or c["id"] in x.get("categories", []) for x in items)} for c in read("registry/taxonomy/operational.json", []) if any(x.get("operational_category") == c["id"] or c["id"] in x.get("categories", []) for x in items)],
        "topics": [{"slug": s, "name": n, "description": d, "count": len(topics_by_id[s])} for s, n, d, *_ in TOPICS if topics_by_id[s]],
        "repositories": repo_items, "assets": entity_items, "items": items, "capabilities": capability_export,
    }


def md_link(label, target):
    label = str(label).replace("[", "\\[").replace("]", "\\]").replace("|", "\\|").replace("\n", " ")
    target = quote(str(target), safe="/:#?=&%+-._~")
    return f"[{label}]({target})"


def item_line(item, current_dir="."):
    canonical = item.get("canonical_record")
    link = canonical_record_url(canonical) if canonical else item.get("repository_record") or item["repository_url"]
    badges = [item.get("entity_type", "Repository"), item.get("review_status", "UNKNOWN"), item.get("evidence_status", ""), "DESCRIPTION NEEDS REVIEW" if item.get("description_status") == "NEEDS_DESCRIPTION" else "", ", ".join(item.get("categories", [])[:3])]
    desc = clean(item.get("description"), 220)
    return f"- {md_link(item['name'], link)} — {desc}<br>\n  Source: {md_link(item['repository'], item['repository_url'])}" + (f" · {md_link(item['source_path'], item['source_url'])}" if item.get("source_path") else "") + f" · {' · '.join(x for x in badges if x)}"


def page_content(title, items, base_link, page=1, nested=None, nav="../../README.md"):
    total = len(items)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    selected = items[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]
    repositories_link = posixpath.relpath("browse/repositories/README.md", base_link)
    lines = [f"# {title}", "", f"{total:,} catalog entries · Sorted alphabetically by name · Page {page} of {pages}.", "", f"[Category home](README.md) · [All browse sections]({nav}) · [All repositories]({repositories_link})", ""]
    if nested:
        lines += ["## Browse within this topic", ""]
        lines += [f"- {md_link(name, href)} ({count:,})" for name, href, count in nested]
        lines += [""]
    lines += [item_line(x, base_link) for x in selected]
    if pages > 1:
        lines += ["", "## Pages", ""]
        lines += [f"- {'**' if n == page else ''}{md_link('Page ' + str(n), 'README.md' if n == 1 else f'page-{n}.md')}{'**' if n == page else ''}" for n in range(1, pages + 1)]
    return "\n".join(lines).rstrip() + "\n"


def write_text(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


def write_section(folder: str, title: str, desc: str, items: list, nav: str):
    if not items:
        return 0
    items = sorted(items, key=lambda x: (x["name"].lower(), x["id"]))
    pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
    path = pathlib.PurePosixPath(folder)
    nested = None
    # index is the first readable page; pagination links remain in the same directory.
    repo_link = posixpath.relpath("browse/repositories/README.md", folder)
    topic_parent = ""
    parts = pathlib.PurePosixPath(folder).parts
    if len(parts) >= 5 and parts[:2] == ("browse", "topics") and "by-type" in parts:
        topic_slug = parts[2]
        parent = posixpath.relpath(f"browse/topics/{topic_slug}/README.md", folder)
        topic_parent = f"[Back to {topic_slug.replace('-', ' ').title()}]({parent}) · "
    intro = [f"# {title}", "", desc, "", f"**{len(items):,} entries** · Alphabetical · {pages} page{'s' if pages != 1 else ''}.", "", topic_parent + f"[Browse homepage]({nav}) · [All repositories]({repo_link})", ""]
    first = items[:PAGE_SIZE]
    intro += [item_line(x, folder) for x in first]
    if pages > 1:
        intro += ["", "## Pages", ""]
        intro += [f"- {'**' if n == 1 else ''}{md_link('Page ' + str(n), 'README.md' if n == 1 else f'page-{n}.md')}{'**' if n == 1 else ''}" for n in range(1, pages + 1)]
    write_text((path / "README.md").as_posix(), "\n".join(intro).rstrip() + "\n")
    for n in range(2, pages + 1):
        write_text((path / f"page-{n}.md").as_posix(), page_content(title + f" — page {n}", items, folder, n, nav=nav))
    return pages


def generate(catalog):
    items = catalog["items"]
    assets = catalog["assets"]
    repos = catalog["repositories"]
    mapped = set().union(*(x[2] for x in TYPE_SPECS))
    other = [x for x in assets if x["entity_type"] not in mapped]
    if other:
        catalog["asset_types"].append({"slug": "other-assets", "name": "Other Assets", "count": len(other)})
    catalog["asset_types"].append({"slug": "repositories", "name": "Repositories", "count": len(repos)})
    pages = 0
    # Agent/site export. Keep one canonical record per item; views only contain links.
    export = {k: v for k, v in catalog.items() if k not in ("items", "repositories", "assets")}
    export["items"] = [{k: x.get(k) for k in ("id", "kind", "asset_type", "entity_type", "name", "description", "description_status", "record_url", "repository", "repository_url", "source_path", "source_url", "upstream_url", "language", "technology", "review_status", "evidence_status", "inspected_commit", "inspection_date", "blob_sha", "categories", "operational_category", "operational_category_name", "asset_types", "capabilities", "capability_ids", "recommendation", "topics")} for x in items]
    write_text("docs/catalog/catalog.json", json.dumps(export, ensure_ascii=False, separators=(",", ":")) + "\n")

    # Public source links are from the stable branch expected after publication.
    write_text("docs/catalog/index.html", STATIC_HTML)
    write_text("docs/catalog/app.js", STATIC_JS)
    write_text("docs/catalog/styles.css", STATIC_CSS)

    type_links = []
    for slug_, title, types in TYPE_SPECS:
        group = [x for x in assets if x["entity_type"] in types]
        if not group:
            continue
        pages += write_section(f"browse/types/{slug_}", title, f"Individually searchable {title.lower()} from the public owned catalog.", group, "../../README.md")
        type_links.append((slug_, title, len(group)))
    # All otherwise-unmapped entity kinds remain discoverable under Other Assets.
    if other:
        pages += write_section("browse/types/other-assets", "Other Assets", "Meaningful reusable assets not covered by a named asset type.", other, "../../README.md")
        type_links.append(("other-assets", "Other Assets", len(other)))
    # Repositories are a first-class browse type as well as their own index.
    type_links.append(("repositories", "Repositories", len(repos)))
    pages += write_section("browse/types/repositories", "Repositories", "All public repositories, alphabetically listed and paginated.", repos, "../../README.md")
    pages += write_section("browse/repositories", "Repositories", "Public repositories owned or forked under the catalog owner account. Repository entries describe indexed ownership; they do not imply software is installed or running.", repos, "../README.md")

    topic_map = {s: (n, d) for s, n, d, *_ in TOPICS}
    type_map = {x[0]: x[1] for x in TYPE_SPECS}
    topic_links = []
    for topic in catalog["topics"]:
        topic_slug = topic["slug"]
        group = [x for x in items if topic_slug in x.get("topics", [])]
        nested = []
        by_type = collections.defaultdict(list)
        for x in group:
            if x["kind"] == "repository":
                by_type["repositories"].append(x)
            else:
                by_type[next((s for s, _, kinds in TYPE_SPECS if x["entity_type"] in kinds), "other-assets")].append(x)
        if topic_slug in {"android", "websites", "ui-ux", "animation-motion", "voice-stt-tts", "video"}:
            for type_slug, typed_items in sorted(by_type.items(), key=lambda pair: (type_map.get(pair[0], "Repositories").lower(), pair[0])):
                if not typed_items:
                    continue
                type_title = type_map.get(type_slug, "Repositories" if type_slug == "repositories" else "Other Assets")
                nested_path = f"browse/topics/{topic_slug}/by-type/{type_slug}"
                pages += write_section(nested_path, f"{topic['name']} · {type_title}", f"{type_title} tagged under {topic['name']}.", typed_items, "../../../../README.md")
                nested.append((type_title, f"by-type/{type_slug}/README.md", len(typed_items)))
        pages += write_section(f"browse/topics/{topic_slug}", topic["name"], topic["description"], group, "../../README.md")
        # Append nested links to category homepage after its generated item list.
        if nested:
            p = ROOT / "browse" / "topics" / topic_slug / "README.md"
            current = p.read_text(encoding="utf-8")
            marker = f"**{len(group):,} entries**"
            current = current.replace(marker, marker + "\n\n## Browse within this topic\n\n" + "\n".join(f"- {md_link(name, href)} ({count:,})" for name, href, count in nested), 1)
            p.write_text(current, encoding="utf-8", newline="\n")
        topic_links.append((topic_slug, topic["name"], len(group)))

    # Established 25-area operational taxonomy: only create browsable pages with records.
    op_categories = read("registry/taxonomy/operational.json", [])
    category_links = []
    for cat in op_categories:
        group = [x for x in items if x.get("operational_category") == cat["id"]]
        if not group:
            continue
        cat_slug = slug(cat["name"])
        pages += write_section(f"browse/categories/{cat_slug}", cat["name"], "Canonical operational taxonomy view generated from registry assignments.", group, "../../README.md")
        category_links.append((cat_slug, cat["name"], len(group)))

    # Repository index page includes metadata-only/unclassified records without hiding them.
    missing = [x for x in repos if x["description_status"] == "NEEDS_DESCRIPTION"]
    links = lambda rows, base: " · ".join(md_link(name, f"{base}/{s}/README.md") + f" ({count:,})" for s, name, count in rows)
    home = [
        "# MALIKY REPOSITORY INTELLIGENCE", "", "My personal library of owned software capabilities.", "",
        "This catalog describes software I own or forked on GitHub. A catalog entry does not mean that software is installed, running, compatible, secure, or production-ready.", "",
        "## Browse by Asset Type", "", links(type_links, "browse/types"), "",
        "## Browse by Purpose", "", links(topic_links, "browse/topics"), "",
        "## Browse the Canonical 25-Area Taxonomy", "", links(category_links, "browse/categories"), "",
        "## Browse All Repositories", "", md_link(f"{len(repos):,} public repositories", "browse/repositories/README.md") + f" · {catalog['counts']['needs_description_repositories']} need a clearer description.", "",
        "## Search the Catalog", "", md_link("Open the lightweight searchable catalog", "docs/catalog/index.html") + " · [Machine-readable JSON export](docs/catalog/catalog.json) · [Agent access and CLI](docs/AGENT-ACCESS.md)", "",
        "## How Agents Can Use This Library", "", "Use `python scripts/search_catalog.py` for deterministic local search, then use `python scripts/compose_idea.py idea:...` to map established capabilities to owned assets. Every result carries a repository and source link when available. See [agent instructions](docs/AGENT-ACCESS.md).", "",
        "## Recently Added Repositories", "", "The newest public inventory entries are shown first by GitHub update timestamp.", "",
    ]
    newest = sorted(repos, key=lambda x: x.get("pushed_at") or "", reverse=True)[:10]
    if not newest:
        newest = repos[:10]
    home.extend(item_line(x, ".") for x in newest)
    home += ["", "## About the Catalog", "", f"{len(repos):,} public repositories · {len(assets):,} active searchable assets · {len(catalog['capabilities']):,} registered capabilities · {len(topic_links):,} populated purpose sections.", "", "Evidence status and historical semantic-review states remain visible. Generated pages are navigation views; the canonical source records are in `registry/`.", ""]
    # Keep the root README human-maintained. It carries the project mission and
    # permanent navigation links; the generated, count-bearing browse homepage
    # below is the canonical automatically refreshed directory.

    browse = ["# Browse the Maliky Catalog", "", f"{len(assets):,} individually searchable assets across {len(type_links)} populated asset types, {len(topic_links)} populated topics and {len(category_links)} active canonical taxonomy areas.", "", "## By Asset Type", ""]
    browse += [f"- {md_link(name, f'types/{s}/README.md')} ({count:,})" for s, name, count in type_links]
    browse += ["", "## By Purpose", ""]
    browse += [f"- {md_link(name, f'topics/{s}/README.md')} ({count:,})" for s, name, count in topic_links]
    browse += ["", "## Canonical 25-Area Taxonomy", ""]
    browse += [f"- {md_link(name, f'categories/{s}/README.md')} ({count:,})" for s, name, count in category_links]
    browse += ["", f"[All {len(repos):,} repositories](repositories/README.md) · [Search](../docs/catalog/index.html) · [Machine-readable export](../docs/catalog/catalog.json)", ""]
    write_text("browse/README.md", "\n".join(browse))

    browse_pages = sum(1 for p in (ROOT / "browse").rglob("*.md"))
    return {"browse_pages": browse_pages, "asset_types": type_links, "topics": topic_links, "canonical_categories": category_links, "repositories_needing_description": [x["name"] for x in missing]}


STATIC_HTML = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Maliky Capability Catalog</title><link rel="stylesheet" href="styles.css"></head>
<body><main><header><p class="eyebrow">MALIKY REPOSITORY INTELLIGENCE</p><h1>My GitHub capability library</h1><p>Search owned repositories and individually indexed assets. Catalog presence does not mean software is installed or production-ready.</p></header>
<section class="controls"><label for="query">Search by name, capability, description, technology, repository or source path</label><input id="query" type="search" placeholder="Try “Android voice interface” or “MCP server”" autocomplete="off"><div class="filters"><label>Asset type <select id="type"><option value="">All types</option></select></label><label>Topic <select id="topic"><option value="">All topics</option></select></label><label>Status <select id="status"><option value="">All evidence states</option><option>VERIFIED</option><option>NEEDS_REVIEW</option><option>COMPLETE</option><option>PARTIAL</option><option>STRUCTURE_COMPLETE</option><option>DISCOVERED</option></select></label></div><p id="count" aria-live="polite"></p></section><section id="results" aria-live="polite"></section></main><script src="app.js"></script></body></html>'''

STATIC_JS = '''const $=s=>document.querySelector(s);let catalog=[];const esc=s=>String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\\"":"&quot;","'":"&#39;"}[c]));const text=x=>[x.name,x.asset_type,x.entity_type,x.description,x.repository,x.source_path,x.technology,x.language,(x.categories||[]).join(" "),(x.capabilities||[]).join(" "),(x.topics||[]).join(" ")].join(" ").toLowerCase();
fetch("catalog.json").then(r=>r.json()).then(data=>{catalog=data.items||[];const types=[...new Set(catalog.map(x=>x.asset_type))].sort();for(const x of types)$("#type").add(new Option(x,x));for(const x of data.topics||[])$("#topic").add(new Option(x.name,x.slug));render();}).catch(()=>{$("#count").textContent="Catalog data could not be loaded. Use the JSON export or local CLI."});
function render(){const q=$("#query").value.toLowerCase().trim().split(/\\s+/).filter(Boolean),type=$("#type").value,topic=$("#topic").value,status=$("#status").value;let rows=catalog.map(x=>{const hay=text(x);const score=q.reduce((n,t)=>n+(hay.includes(t)?1:0),0);return{x,score}}).filter(y=>(!q.length||y.score>0)&&(!type||y.x.asset_type===type)&&(!topic||y.x.topics.includes(topic))&&(!status||y.x.review_status===status)).sort((a,b)=>b.score-a.score||a.x.name.localeCompare(b.x.name)).slice(0,250);$("#count").textContent=`Showing ${rows.length} of ${catalog.filter(x=>(!type||x.asset_type===type)&&(!topic||x.topics.includes(topic))&&(!status||x.review_status===status)).length} matches (maximum 250 per view).`;$("#results").innerHTML=rows.map(({x})=>`<article><h2><a href="${esc(x.record_url||x.repository_url)}">${esc(x.name)}</a></h2><p>${esc(x.description)}</p><p class="meta">${esc(x.asset_type)} · ${esc(x.review_status)} · from <a href="${esc(x.repository_url)}">${esc(x.repository)}</a></p>${x.source_path?`<p><a href="${esc(x.source_url)}">Source: ${esc(x.source_path)}</a></p>`:""}<p class="tags">${(x.topics||[]).map(t=>`<span>${esc(t)}</span>`).join("")}</p></article>`).join("")||"<p>No matching entries.</p>"}
["#query","#type","#topic","#status"].forEach(s=>$(s).addEventListener(s==="#query"?"input":"change",render));'''

STATIC_CSS = '''*{box-sizing:border-box}body{margin:0;background:#f5f7fb;color:#19202a;font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}main{max-width:1080px;margin:0 auto;padding:28px 20px 64px}header{padding:28px 32px;border-radius:18px;background:#15233b;color:white}h1{font-size:clamp(2rem,5vw,3.3rem);line-height:1.1;margin:.2em 0}.eyebrow{letter-spacing:.12em;font-size:.78rem;font-weight:700;color:#a9c7ff}.controls{position:sticky;top:0;background:#f5f7fb;padding:20px 0;z-index:2}input,select{font:inherit;padding:12px;border:1px solid #bcc7d8;border-radius:9px;background:white}input{display:block;width:100%;margin:8px 0 12px}.filters{display:flex;gap:14px;flex-wrap:wrap}.filters label{display:grid;gap:4px}article{background:white;border:1px solid #e0e5ed;border-radius:12px;padding:18px 20px;margin:12px 0;box-shadow:0 2px 8px #17233b0a}article h2{font-size:1.15rem;margin:0 0 6px}a{color:#1456a0}.meta,.tags{font-size:.9rem;color:#4d596b}.tags span{display:inline-block;background:#edf2fa;border-radius:99px;padding:2px 9px;margin:2px}#count{font-weight:600}@media(max-width:600px){main{padding:14px}.filters>*{width:100%}.filters select{width:100%}}'''


def main():
    catalog = make_catalog()
    result = generate(catalog)
    result["counts"] = catalog["counts"]
    result["generated_at"] = catalog["generated_at"]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
