"""Reconcile packaging variants in the active V1 intake batch.

The reviewed repositories deliberately publish the same logical skill for
multiple agent harnesses.  Those copies are distribution variants, not
independent capabilities.  Evidence comes only from the pinned source cache;
source code is never imported or executed.
"""
from __future__ import annotations

import json

from lean_review_lib import LeanReview
import registry as r


def complete(review: LeanReview, result: dict) -> dict:
    repo = review.repo
    repo.update({"state": "COMPLETE", "next_phase": "COMPLETE"})
    repo.setdefault("phases", {}).update(
        {
            "structure": True,
            "entity_extraction": True,
            "capability_analysis": True,
            "validation": True,
        }
    )
    r.write(r.repo_file(repo), repo)
    return {**result, "state": "COMPLETE"}


def one(review: LeanReview, kind: str, *, path: str):
    found = review.find(kind, path=path)
    if len(found) != 1:
        raise ValueError(f"Expected one {kind} at {path}, found {len(found)}")
    return found[0]


def review_youtube_skills() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/youtube-skills",
        "5c168578ec8424dbd1bd144d1cb53e8e6db276ee",
    )
    categories = [
        "category:skills",
        "category:plugins-extensions",
        "category:media-publishing",
    ]
    studios: list[str] = []

    definitions = {
        "captions": (
            "Fetch timestamped YouTube captions for accessibility, translation, quotation and content review through TranscriptAPI.",
            "youtube-caption-retrieval",
            "YouTube caption retrieval",
        ),
        "subtitles": (
            "Fetch timestamped YouTube subtitles for reading, translation, language learning and accessibility through TranscriptAPI.",
            "youtube-subtitle-retrieval",
            "YouTube subtitle retrieval",
        ),
        "transcript": (
            "Retrieve the spoken content of a YouTube video for summarization, quotation, translation, fact checking and research.",
            "youtube-transcript-retrieval",
            "YouTube transcript retrieval",
        ),
        "transcriptapi": (
            "Broad TranscriptAPI skill covering YouTube transcripts, search, channels, playlists and within-channel research.",
            "transcriptapi-youtube-research",
            "TranscriptAPI YouTube research",
        ),
        "video-transcript": (
            "Extract YouTube video content as text for transcription, summarization, translation and information extraction.",
            "video-to-transcript-workflow",
            "Video-to-transcript workflow",
        ),
        "youtube-api": (
            "Query transcripts, video metadata, channels, search results and playlists without Google OAuth or Google API quotas.",
            "youtube-data-api-without-oauth",
            "YouTube data API without OAuth",
        ),
        "youtube-channels": (
            "Resolve and browse YouTube channels, recent uploads and within-channel search results.",
            "youtube-channel-browsing",
            "YouTube channel browsing",
        ),
        "youtube-data": (
            "Retrieve structured YouTube transcript, video, channel, playlist and search data through TranscriptAPI.",
            "structured-youtube-data-retrieval",
            "Structured YouTube data retrieval",
        ),
        "youtube-full": (
            "Full YouTube research workflow spanning transcripts, video and channel search, channel browsing and playlists.",
            "full-youtube-research-workflow",
            "Full YouTube research workflow",
        ),
        "youtube-playlist": (
            "List and browse YouTube playlist contents for series, course and collection research.",
            "youtube-playlist-browsing",
            "YouTube playlist browsing",
        ),
        "youtube-search": (
            "Search YouTube videos and channels for creators, tutorials, talks and topic research.",
            "youtube-video-channel-search",
            "YouTube video and channel search",
        ),
        "yt": (
            "Compact YouTube utility skill covering quick transcripts, search and latest channel uploads.",
            "compact-youtube-agent-utility",
            "Compact YouTube agent utility",
        ),
    }

    for entity in list(review.existing):
        path = entity["source"]["source_path"]
        if entity["entity_type"] == "SKILL" and path.startswith("clawhub/"):
            review.drop(entity)
        elif entity["entity_type"] == "SKILL" and path.startswith("skills/"):
            description, slug, name = definitions[entity["name"]]
            review.finish(
                entity,
                description,
                [(slug, name, [entity["name"], name.lower()])],
                "USE DIRECTLY",
                "operational:01",
                "SKILL",
                "FULL",
                ["TranscriptAPI internet service", "TRANSCRIPT_API_KEY"],
                "The clawhub copy is a distribution variant of this canonical skill; related skills intentionally expose narrower or broader trigger surfaces.",
                categories,
                studios,
                extra={
                    "distribution_variants": [f"clawhub/{entity['name']}/SKILL.md"],
                    "network_service": "https://transcriptapi.com",
                    "credential_requirement": "TRANSCRIPT_API_KEY",
                    "version": "1.5.1" if entity["name"] == "yt" else "1.5.0",
                },
            )
        elif entity["entity_type"] == "PLUGIN":
            review.finish(
                entity,
                "Codex plugin manifest packaging the canonical YouTube skill collection for agent installation.",
                [
                    (
                        "youtube-agent-skill-plugin",
                        "YouTube agent skill plugin",
                        ["youtube-skills plugin", "YouTube skills bundle"],
                    )
                ],
                "USE DIRECTLY",
                "operational:01",
                "CORE",
                "FULL",
                ["Compatible Codex plugin loader", "bundled skills"],
                "Provides the installation surface for the twelve canonical skills.",
                categories,
                studios,
            )
        else:
            # The scanner workflow is project CI, not an independently reusable
            # capability in this inventory.
            review.drop(entity)

    result = review.finalize(
        categories,
        studios,
        "USE DIRECTLY",
        "operational:01",
        {
            "SKILL": "Twelve named skills retained once under skills/; clawhub copies are packaging variants.",
            "PLUGIN": "Plugin installation manifest retained.",
            "WORKFLOW": "Repository-specific scanner CI is not catalogued as a reusable capability.",
        },
        deep_review="Credential scope reviewed: every skill declares only the external TRANSCRIPT_API_KEY and performs network reads through TranscriptAPI; no upload or account-management behavior is claimed.",
        details=["clawhub distribution copies", "repository-specific scanner CI"],
    )
    return complete(review, result)


def review_website_cloner() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/ai-website-cloner-template",
        "92872bc40ced2c5edb4d5dc9fd3970d40c77f4ca",
    )
    categories = [
        "category:skills",
        "category:templates-boilerplates",
        "category:developer-tools",
        "category:frontend-applications",
    ]
    studios: list[str] = []

    canonical = one(
        review,
        "SKILL",
        path=".codex/skills/clone-website/SKILL.md",
    )
    for entity in list(review.existing):
        if entity["id"] == canonical["id"]:
            continue
        path = entity["source"]["source_path"]
        if entity["entity_type"] == "PACKAGE":
            review.finish(
                entity,
                "Private Next.js 16, React 19, Tailwind CSS and shadcn-based application scaffold used as the target for agent-built website clones.",
                [
                    (
                        "website-cloning-nextjs-scaffold",
                        "Website-cloning Next.js scaffold",
                        ["AI website clone template", "Next.js clone starter"],
                    )
                ],
                "USE DIRECTLY",
                "operational:16",
                "CORE",
                "PARTIAL",
                ["Node.js 24+", "Next.js 16", "React 19", "Tailwind CSS 4"],
                "Complements the clone-website skill; the generic starter page and layout are implementation scaffolding.",
                categories,
                studios,
            )
        elif entity["entity_type"] == "SKILL":
            review.drop(entity)
        else:
            # Generic starter UI and repository CI do not pass the independent
            # reuse test once the skill and scaffold are represented.
            review.drop(entity)

    review.finish(
        canonical,
        "Foreman-style website reverse-engineering skill that captures source evidence section by section, writes auditable build specifications and coordinates isolated builders for faithful Next.js reconstruction.",
        [
            (
                "agent-directed-website-reconstruction",
                "Agent-directed website reconstruction",
                ["clone website skill", "pixel-perfect website clone workflow"],
            )
        ],
        "USE DIRECTLY",
        "operational:01",
        "SKILL",
        "FULL",
        ["browser automation", "prepared Next.js application root", "compatible coding-agent harness"],
        "The five other harness-specific SKILL.md files are synchronized distribution variants of the same logical skill.",
        categories,
        studios,
        extra={
            "distribution_variants": [
                ".claude/skills/clone-website/SKILL.md",
                ".cline/skills/clone-website/SKILL.md",
                ".github/skills/clone-website/SKILL.md",
                ".kiro/skills/clone-website/SKILL.md",
                ".roo/skills/clone-website/SKILL.md",
            ],
            "required_interface": "browser automation plus coding-agent file access",
        },
    )

    template = review.make("TEMPLATE", "AI Website Cloner Template", "README.md", 1)
    review.finish(
        template,
        "MIT-licensed, multi-agent website-cloning template combining the clone-website skill with a prepared Next.js application scaffold and synchronized instructions for several agent harnesses.",
        [
            (
                "multi-agent-website-cloner-template",
                "Multi-agent website cloner template",
                ["AI Website Cloner Template", "website reconstruction starter"],
            )
        ],
        "USE DIRECTLY",
        "operational:24",
        "REFERENCE",
        "FULL",
        ["GitHub template workflow", "Node.js 24+", "browser-capable coding agent"],
        "Contains the canonical skill and Next.js scaffold rather than representing another copy of either.",
        categories,
        studios,
        extra={"license": "MIT", "template_version": "0.4.0"},
    )

    result = review.finalize(
        categories,
        studios,
        "USE DIRECTLY",
        "operational:24",
        {
            "SKILL": "One canonical Codex skill retained; five synchronized harness variants recorded as metadata.",
            "PACKAGE": "The prepared Next.js scaffold retained.",
            "TEMPLATE": "Repository-level reusable template retained.",
            "UI_COMPONENT": "Generic starter layout and page do not pass the independent reuse test.",
            "WORKFLOW": "Repository-specific consistency/build CI is implementation support, not a standalone capability.",
        },
        details=["generic starter UI", "synchronized harness copies", "repository CI"],
    )
    return complete(review, result)


def main() -> None:
    results = [review_youtube_skills(), review_website_cloner()]
    r.build()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
