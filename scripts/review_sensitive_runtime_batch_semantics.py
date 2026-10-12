"""Lean semantic review for sensitive runtimes in the active V1 batch.

This script records the reusable implementation cores that declaration scanning
missed, removes packaging and test false positives, and performs the narrow
security/identity review required by the repository policy.  All evidence is
read from pinned, blob-verified source.  Inspected source is never executed.
"""
from __future__ import annotations

import json

from lean_review_lib import LeanReview
import registry as r


def complete_scoped(
    review: LeanReview,
    result: dict,
    evidence: list[tuple[str, int]],
    conclusion: str,
) -> dict:
    """Mark inventory work complete while preserving a deployment warning."""
    repo = review.repo
    repo.update({"state": "COMPLETE", "next_phase": "COMPLETE"})
    repo.setdefault("phases", {}).update(
        {
            "structure": True,
            "entity_extraction": True,
            "capability_analysis": True,
            "deep_review": True,
            "validation": True,
        }
    )
    repo["deep_review"] = {
        "completed": True,
        "reviewer": "Automated scoped static review",
        "evidence": [
            {"type": "source_review", "value": review.url(path, line)}
            for path, line in evidence
        ],
        "conclusion": conclusion,
        "runtime_tested": False,
    }
    repo.pop("review_reason", None)
    r.write(r.repo_file(repo), repo)
    return {**result, "state": "COMPLETE", "scoped_review": "COMPLETE"}


def one(review: LeanReview, kind: str, *, path: str):
    found = review.find(kind, path=path)
    if len(found) != 1:
        raise ValueError(f"Expected one {kind} at {path}, found {len(found)}")
    return found[0]


def review_deep_live_cam() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/Deep-Live-Cam",
        "aa6f2cbade35a0a55502b87b18697b020c49b5f3",
    )
    categories = [
        "category:generative-ai",
        "category:ai-applications",
        "category:creative-tools",
        "category:privacy",
    ]

    app = review.make("APP", "Deep-Live-Cam", "modules/core.py", 205)
    review.finish(
        app,
        "Desktop application and live-camera pipeline for applying a source identity to detected faces in images, prerecorded video and real-time camera streams.",
        [
            (
                "real-time-face-swap-application",
                "Real-time face-swap application",
                ["live deepfake application", "camera face replacement"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:09",
        "CORE",
        "PARTIAL",
        ["Python 3.11", "ONNX Runtime", "ffmpeg", "InsightFace model weights"],
        "Orchestrates the reusable face analysis, replacement and enhancement components represented separately.",
        categories,
        [],
        extra={"content_sensitivity": "biometric identity synthesis"},
    )

    swapper = review.make(
        "MODEL_ADAPTER",
        "InsightFace Face Swapper",
        "modules/processors/frame/face_swapper.py",
        501,
    )
    review.finish(
        swapper,
        "ONNX/InsightFace adapter that maps a source face embedding onto one or more target faces, with masking, blending, multi-face mapping and optional CUDA-graph inference.",
        [
            (
                "identity-conditioned-face-replacement",
                "Identity-conditioned face replacement",
                ["face swap processor", "inswapper adapter"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:09",
        "MODULE",
        "PARTIAL",
        ["inswapper_128_fp16.onnx", "InsightFace", "ONNX Runtime", "NumPy/OpenCV"],
        "Primary synthesis module used by the application; the external model weights are not contained in the repository.",
        categories,
        [],
        extra={"external_model": "inswapper_128_fp16.onnx"},
    )

    enhancer = review.make(
        "MODEL_ADAPTER",
        "GFPGAN Face Enhancer",
        "modules/processors/frame/face_enhancer.py",
        66,
    )
    review.finish(
        enhancer,
        "ONNX GFPGAN adapter that aligns, restores and blends generated faces back into image and video frames.",
        [
            (
                "generated-face-restoration",
                "Generated-face restoration",
                ["GFPGAN face enhancement", "face restoration adapter"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:09",
        "MODULE",
        "PARTIAL",
        ["GFPGANv1.4.onnx", "ONNX Runtime", "OpenCV"],
        "Optional post-processing complement to the face swapper.",
        categories,
        [],
        extra={"external_model": "GFPGANv1.4.onnx"},
    )

    analyser = review.make(
        "COMPONENT", "Face Analysis and Mapping", "modules/face_analyser.py", 22
    )
    review.finish(
        analyser,
        "Face detection, landmark completion, cached analysis and source-to-target face mapping used by still-image and streaming replacement paths.",
        [
            (
                "face-detection-landmark-mapping",
                "Face detection and landmark mapping",
                ["multi-face mapping", "face analysis cache"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:08",
        "MODULE",
        "PARTIAL",
        ["InsightFace FaceAnalysis", "OpenCV", "configured execution provider"],
        "Complements the face swapper and exposes independently useful analysis and mapping logic.",
        categories,
        [],
    )

    cli = review.make("CLI", "Deep-Live-Cam launcher", "run.py", 72)
    review.finish(
        cli,
        "Cross-platform launcher that prepares local runtime library paths and delegates to the application's command-line/UI orchestration.",
        [
            (
                "cross-platform-face-swap-launcher",
                "Cross-platform face-swap launcher",
                ["Deep-Live-Cam CLI", "deepfake launcher"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:09",
        "COMPONENT",
        "PARTIAL",
        ["Deep-Live-Cam Python environment", "platform GPU libraries"],
        "Thin operational surface over the application.",
        categories,
        [],
    )

    review.relate("PROVIDES", app["id"], swapper["id"], "modules/core.py", 205)
    review.relate("PROVIDES", app["id"], enhancer["id"], "modules/core.py", 205)
    review.relate("DEPENDS_ON", swapper["id"], analyser["id"], "modules/processors/frame/face_swapper.py", 501)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:09",
        {
            "APP": "Application orchestration retained.",
            "MODEL_ADAPTER": "Face replacement and restoration adapters retained; external weights are dependencies.",
            "COMPONENT": "Face analysis and mapping retained.",
            "CLI": "Cross-platform launcher retained.",
        },
        deep_review="Biometric/deepfake trigger reviewed narrowly. README requires consent and deepfake labeling and describes content checks, but those statements are policy controls rather than proof against impersonation or misuse. Deployment remains security/identity-review gated.",
        details=["UI widgets", "low-level CUDA graph helper", "external model weights"],
    )
    return complete_scoped(
        review,
        result,
        [("README.md", 11), ("modules/processors/frame/face_swapper.py", 501)],
        "Inventory is complete. Reuse must remain gated on consent, identity-abuse controls, output disclosure and applicable biometric/deepfake law; runtime safeguards were not tested.",
    )


def review_mobile_agent() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/MobileAgent-Android",
        "31e3662d4bec9d8101997a2bd6f63a2c6d04e153",
    )
    categories = [
        "category:mobile-applications",
        "category:ai-agents",
        "category:agent-frameworks",
        "category:accessibility",
        "category:privacy",
    ]
    for entity in list(review.existing):
        review.drop(entity)  # Release-only CI is not an independent capability.

    root = "app/src/main/java/com/mobileagent/app/"
    framework = review.make("AGENT_FRAMEWORK", "MobileAgent Android AgentLoop", root + "agent/AgentLoop.kt", 24)
    review.finish(
        framework,
        "Native Android vision-language agent loop that repeatedly captures the screen, plans, executes device actions, reflects on results and updates working notes with bounded retries.",
        [
            (
                "autonomous-android-device-agent-loop",
                "Autonomous Android device agent loop",
                ["mobile VLM agent", "screenshot-plan-act-reflect loop"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        "CORE",
        "PARTIAL",
        ["Android API 26+", "Kotlin coroutines", "vision-language model client", "Accessibility Service", "MediaProjection"],
        "Native alternative to desktop/ADB mobile-agent implementations.",
        categories,
        [],
        extra={"default_max_steps": 25, "privileged_interfaces": ["AccessibilityService", "MediaProjection", "SYSTEM_ALERT_WINDOW"]},
    )

    phase_specs = [
        ("Manager Agent", "Manager.kt", 3, "Plans and revises numbered task subgoals from screenshots, UI elements and execution history.", "android-agent-task-planning", "Android agent task planning"),
        ("Executor Agent", "Executor.kt", 3, "Selects and parses one atomic Android action for the current subgoal.", "android-agent-action-selection", "Android agent action selection"),
        ("Action Reflector Agent", "ActionReflector.kt", 3, "Compares before/after state and classifies an action as successful, failed or ineffective.", "android-agent-action-reflection", "Android agent action reflection"),
        ("Notetaker Agent", "Notetaker.kt", 3, "Extracts durable on-screen facts into the agent's running task notes after successful actions.", "android-agent-screen-notetaking", "Android agent screen notetaking"),
    ]
    phase_entities = []
    for name, filename, line, description, slug, cap_name in phase_specs:
        entity = review.make("AGENT", name, root + "agent/" + filename, line)
        review.finish(
            entity,
            description,
            [(slug, cap_name, [name.lower()])],
            "EXTRACT",
            "operational:03",
            "MODULE",
            "PARTIAL",
            ["MobileAgent InfoPool state", "vision-language model response"],
            "A coordinated phase inside the four-stage Android agent loop.",
            categories,
            [],
        )
        phase_entities.append(entity)
        review.relate("CONTAINS_AGENT", framework["id"], entity["id"], root + "agent/AgentLoop.kt", 24)

    component_specs = [
        ("Android Accessibility Controller", "controller/AccessibilityController.kt", 10, "MOBILE_COMPONENT", "Executes taps, long presses, swipes, typing and Back/Home/Enter actions through the Android accessibility service.", "android-accessibility-device-control", "Android accessibility device control"),
        ("Android Screen Capture Manager", "controller/ScreenCaptureManager.kt", 18, "MOBILE_COMPONENT", "Captures Android display frames from an authorized MediaProjection session for agent perception.", "android-mediaprojection-screen-capture", "Android MediaProjection screen capture"),
        ("Android UI Element Detector", "controller/UiElementDetector.kt", 17, "MOBILE_COMPONENT", "Traverses the accessibility tree, indexes interactive elements and annotates screenshots with target boxes.", "android-accessibility-ui-element-detection", "Android accessibility UI-element detection"),
        ("MobileAgent Accessibility Service", "service/AgentAccessibilityService.kt", 20, "SERVICE", "Privileged Android AccessibilityService implementing gesture dispatch and focused-field text input for the agent controller.", "android-agent-accessibility-service", "Android agent accessibility service"),
    ]
    for name, path, line, kind, description, slug, cap_name in component_specs:
        entity = review.make(kind, name, root + path, line)
        review.finish(
            entity,
            description,
            [(slug, cap_name, [name.lower()])],
            "SECURITY REVIEW REQUIRED",
            "operational:06",
            "MODULE",
            "PARTIAL",
            ["Android privileged user grant", "foreground application/service context"],
            "Privileged perception or action surface used by the agent loop.",
            categories,
            [],
            extra={"privilege_sensitive": True},
        )
        review.relate("DEPENDS_ON", framework["id"], entity["id"], root + "agent/AgentLoop.kt", 24)

    adapters = [
        ("Local Android VLM Adapter", "LocalVlmClient.kt", 29, "On-device adapter for a local llama.cpp-backed multimodal model with JPEG screenshot encoding.", "on-device-android-vlm-inference", "On-device Android VLM inference", ["local model files", "LlamaVlmEngine"]),
        ("OpenAI-Compatible Mobile VLM Adapter", "OpenAiCompatibleClient.kt", 14, "Android client for OpenAI-compatible multimodal chat endpoints used to reason over screenshots.", "openai-compatible-mobile-vlm-client", "OpenAI-compatible mobile VLM client", ["configured HTTPS endpoint", "API key", "vision-capable model"]),
        ("Anthropic Mobile VLM Adapter", "AnthropicClient.kt", 15, "Android client for Anthropic multimodal messages used to reason over screenshots.", "anthropic-mobile-vlm-client", "Anthropic mobile VLM client", ["Anthropic API endpoint", "API key", "vision-capable Claude model"]),
    ]
    for name, filename, line, description, slug, cap_name, deps in adapters:
        entity = review.make("MODEL_ADAPTER", name, root + "api/" + filename, line)
        review.finish(
            entity,
            description,
            [(slug, cap_name, [name.lower()])],
            "EXTRACT" if "Local" in name else "SECURITY REVIEW REQUIRED",
            "operational:15",
            "COMPONENT",
            "PARTIAL",
            deps,
            "Alternative VLM backends implementing the same mobile prediction interface.",
            categories,
            [],
            extra={"sensitive_input": "device screenshots"},
        )
        review.relate("DEPENDS_ON", framework["id"], entity["id"], root + "agent/AgentLoop.kt", 52)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        {
            "AGENT_FRAMEWORK": "Native screenshot-plan-act-reflect loop retained.",
            "AGENT": "Four functionally distinct agent phases retained.",
            "MOBILE_COMPONENT": "Screen capture, UI detection and device control retained.",
            "SERVICE": "Privileged accessibility service retained.",
            "MODEL_ADAPTER": "Local, OpenAI-compatible and Anthropic VLM clients retained.",
            "WORKFLOW": "Release-only CI is not catalogued as a reusable capability.",
        },
        deep_review="Privileged-device trigger reviewed narrowly. The app requires AccessibilityService, MediaProjection, overlay, foreground-service and battery-optimization permissions; remote VLM modes transmit device screenshots and receive actions capable of taps, typing and system navigation. User grants are necessary but not sufficient deployment policy.",
        details=["Jetpack Compose screens", "floating status UI", "release workflow", "data-store plumbing"],
    )
    return complete_scoped(
        review,
        result,
        [("README.md", 85), (root + "service/AgentAccessibilityService.kt", 20), (root + "controller/ScreenCaptureManager.kt", 18)],
        "Inventory is complete. Deployment requires explicit permission UX, endpoint trust, screenshot/data-handling controls, action confirmation and revocation policy; no privileged Android behavior was executed.",
    )


def review_agent_sdk_mobile() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/agent-sdk-mobile-app",
        "dc414f05172c62af1bc993a556ffa33f6033bb7d",
    )
    categories = [
        "category:mobile-applications",
        "category:ai-applications",
        "category:sdks-client-libraries",
        "category:frontend-applications",
        "category:reference-implementations",
    ]

    ui_specs = {
        "AgentsScreen": ("Mobile agent directory with search, creation, pagination and agent selection.", "mobile-agent-directory-ui", "Mobile agent directory UI"),
        "ChatScreen": ("Mobile streaming-agent chat screen integrating transcript, composer, queue, approval and connection state.", "mobile-agent-chat-ui", "Mobile agent chat UI"),
        "ConversationsScreen": ("Mobile conversation browser with pagination, rename, deletion and resume flows.", "mobile-agent-conversation-ui", "Mobile agent conversation UI"),
        "ConnectScreen": ("Connection onboarding for Letta Cloud OAuth/API keys and authenticated self-hosted app servers.", "mobile-agent-server-connection-ui", "Mobile agent-server connection UI"),
        "ProfileEditorScreen": ("Editor for cloud and self-hosted connection profiles stored in the device credential store.", "mobile-agent-profile-editor-ui", "Mobile agent profile editor UI"),
        "ApprovalCard": ("Tool approval card displaying command context and allow/deny decisions with reasons and persistent suggestions.", "mobile-tool-approval-ui", "Mobile tool-approval UI"),
        "ConnectionBanner": ("Reconnect and connection-state banner for remote agent sessions.", "mobile-agent-connection-state-ui", "Mobile agent connection-state UI"),
        "DiffBlock": ("React Native unified-diff renderer for agent tool output.", "react-native-unified-diff-ui", "React Native unified-diff UI"),
        "Markdown": ("React Native markdown renderer with fenced code and tappable links for agent transcript content.", "react-native-agent-markdown-ui", "React Native agent markdown UI"),
        "ModelSheet": ("Bottom sheet for selecting the model used by a remote agent.", "mobile-agent-model-selector-ui", "Mobile agent model-selector UI"),
        "QueueCapsule": ("Compact queued-follow-up status component for an active agent turn.", "mobile-agent-queue-status-ui", "Mobile agent queue-status UI"),
        "QueueSheet": ("Detailed mobile queue management sheet for follow-up messages.", "mobile-agent-queue-management-ui", "Mobile agent queue-management UI"),
        "ToolDetailSheet": ("Detailed agent tool-call sheet exposing full input, output, duration and status.", "mobile-agent-tool-detail-ui", "Mobile agent tool-detail UI"),
        "UserBubble": ("User-message transcript row with attachment and queued-state rendering.", "mobile-agent-user-message-ui", "Mobile agent user-message UI"),
        "ToolGroupRow": ("Collapsible row summarizing consecutive agent tool calls.", "mobile-agent-tool-group-ui", "Mobile agent tool-group UI"),
        "ErrorRow": ("Agent transcript row for surfaced session and tool errors.", "mobile-agent-error-row-ui", "Mobile agent error-row UI"),
        "ToolCard": ("Agent transcript card for one running or settled tool invocation.", "mobile-agent-tool-card-ui", "Mobile agent tool-card UI"),
        "ReasoningRow": ("Collapsible reasoning transcript row with live think duration.", "mobile-agent-reasoning-row-ui", "Mobile agent reasoning-row UI"),
        "AssistantBlock": ("Streaming assistant-message block for projected agent transcripts.", "mobile-agent-assistant-message-ui", "Mobile agent assistant-message UI"),
        "ThinkingRow": ("Live thinking indicator used while an agent turn is reasoning.", "mobile-agent-thinking-state-ui", "Mobile agent thinking-state UI"),
    }

    for entity in list(review.existing):
        if entity["entity_type"] == "PACKAGE":
            review.finish(
                entity,
                "Expo/React Native reference application package for the Letta Agent SDK, targeting iOS, Android and Expo Go.",
                [("letta-agent-sdk-mobile-reference-app", "Letta Agent SDK mobile reference app", ["Bloop", "letta-mobile"])],
                "REFERENCE",
                "operational:19",
                "CORE",
                "FULL",
                ["Expo", "React Native", "TypeScript", "@letta-ai/letta-agent-sdk 0.7.x"],
                "Repository application shell containing the reusable SDK and UI components represented separately.",
                categories,
                [],
                extra={"license": "Apache-2.0"},
            )
        elif entity["entity_type"] == "UI_COMPONENT" and entity["name"] in ui_specs:
            description, slug, cap_name = ui_specs[entity["name"]]
            review.finish(
                entity,
                description,
                [(slug, cap_name, [entity["name"]])],
                "EXTRACT",
                "operational:16",
                "COMPONENT",
                "PARTIAL",
                ["React Native", "Expo Router", "Bloop design tokens and agent domain model"],
                "Domain-specific reference component; generic layout and primitive components are not separately catalogued.",
                categories,
                [],
            )
        else:
            review.drop(entity)

    core_specs = [
        ("COMPONENT", "Letta ChatSession Adapter", "src/lib/letta/ChatSession.ts", 85, "Portable session adapter covering resume, streaming reduction, approvals, abort, queued follow-ups and server-authoritative reconciliation.", "letta-mobile-chat-session-adapter", "Letta mobile ChatSession adapter", ["@letta-ai/letta-agent-sdk", "authenticated Letta app-server"]),
        ("INTEGRATION", "Letta Mobile Data Layer", "src/lib/letta/api.ts", 1, "Portable Letta client integration for agent, conversation, model and message-history operations.", "letta-mobile-data-layer", "Letta mobile data layer", ["Letta portable client", "Cloud OAuth token or app-server capability token"]),
        ("COMPONENT", "Letta Cloud PKCE OAuth", "src/lib/auth/oauth.ts", 1, "Mobile Authorization Code with PKCE flow for Letta Cloud, including browser handoff and token refresh.", "mobile-pkce-oauth-for-letta", "Mobile PKCE OAuth for Letta", ["Expo AuthSession/WebBrowser", "public OAuth client id", "Expo SecureStore"]),
        ("COMPONENT", "Letta Transcript Projection", "src/lib/letta/transcriptProjection.ts", 1, "Projects Agent SDK transcript accumulator rows into stable React Native render state while preserving live and approval-owned state.", "agent-sdk-transcript-projection", "Agent SDK transcript projection", ["Letta transcript accumulator", "mobile agent domain model"]),
        ("COMPONENT", "Mobile Agent Attachment Pipeline", "src/lib/letta/attachments.ts", 1, "On-device screenshot/photo selection, downscaling and attachment preparation for agent messages.", "mobile-agent-image-attachment-pipeline", "Mobile agent image-attachment pipeline", ["Expo image picker/manipulator", "Letta message attachment contract"]),
        ("COMPONENT", "Secure Connection Profile Store", "src/lib/profiles/profiles.ts", 1, "Cloud and self-hosted server profile persistence that keeps access, refresh, API and capability tokens in Expo SecureStore.", "secure-mobile-agent-profile-store", "Secure mobile agent profile store", ["Expo SecureStore", "React Native profile context"]),
        ("DESIGN_SYSTEM", "Bloop Mobile Design Tokens", "src/theme/tokens.ts", 1, "Tokenized light/dark color, typography, spacing and motion foundation for the mobile agent client.", "mobile-agent-client-design-system", "Mobile agent-client design system", ["React Native", "Bloop ThemeProvider"]),
        ("REFERENCE_IMPLEMENTATION", "Mock Letta Agent Session", "src/lib/letta/mockSession.ts", 1, "Fixture-driven fake agent session that makes streaming, approval, tool, queue and error UI states reachable without a server or credentials.", "mock-mobile-agent-session", "Mock mobile agent session", ["Letta session-shaped domain contract", "fixture data"]),
    ]
    added = []
    for kind, name, path, line, description, slug, cap_name, deps in core_specs:
        entity = review.make(kind, name, path, line)
        review.finish(
            entity,
            description,
            [(slug, cap_name, [name.lower()])],
            "EXTRACT" if kind not in {"INTEGRATION"} else "INTEGRATE VIA API",
            "operational:19" if kind != "DESIGN_SYSTEM" else "operational:17",
            "MODULE" if kind != "REFERENCE_IMPLEMENTATION" else "REFERENCE",
            "PARTIAL",
            deps,
            "Worked mobile reference implementation over the portable Letta Agent SDK.",
            categories,
            [],
        )
        added.append(entity)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:19",
        {
            "PACKAGE": "Reference mobile application retained.",
            "UI_COMPONENT": "Agent-domain screens and transcript/approval components retained; generic primitives and dev-only routes removed.",
            "COMPONENT": "Session, OAuth, transcript, attachment and secure-profile components retained.",
            "INTEGRATION": "Letta data layer retained.",
            "DESIGN_SYSTEM": "Token system retained instead of its provider wrapper.",
            "REFERENCE_IMPLEMENTATION": "Credential-free mock session retained.",
        },
        deep_review="Authentication and remote-execution trigger reviewed narrowly. OAuth uses Authorization Code with PKCE; secrets are stored in Expo SecureStore; self-hosted sessions require a capability token. The remote agent can read files and run commands, the UI offers an unrestricted permission mode, and the README requires TLS/private networking beyond a trusted LAN.",
        details=["generic UI primitives", "root layout", "gallery and press-still routes", "provider wrappers"],
    )
    return complete_scoped(
        review,
        result,
        [("README.md", 33), ("README.md", 48), ("src/lib/auth/oauth.ts", 1), ("src/lib/profiles/profiles.ts", 1)],
        "Inventory is complete. Production reuse must preserve PKCE and secure storage, authenticate every remote socket, default to bounded approval modes, and require TLS or a private network for command-capable servers.",
    )


def review_voice_cloning() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/Real-Time-Voice-Cloning",
        "890f3a03187195b9829db2079b75c2ba2ab0405c",
    )
    categories = [
        "category:machine-learning-models",
        "category:generative-ai",
        "category:creative-tools",
        "category:research-projects",
        "category:privacy",
    ]
    for entity in list(review.existing):
        if entity["entity_type"] == "PACKAGE":
            review.finish(
                entity,
                "Python package for the three-stage SV2TTS voice-cloning research implementation and its inference interfaces.",
                [("sv2tts-python-package", "SV2TTS Python package", ["Real-Time Voice Cloning package"])],
                "REFERENCE",
                "operational:07",
                "CORE",
                "PARTIAL",
                ["Python", "PyTorch", "librosa", "ffmpeg", "pretrained checkpoints"],
                "Packages the three model stages and CLI represented separately.",
                categories,
                [],
            )
        else:
            review.drop(entity)

    model_specs = [
        ("Speaker Encoder", "encoder/model.py", 12, "GE2E-style recurrent speaker encoder that converts a short reference utterance into a normalized voice embedding.", "speaker-voice-embedding", "Speaker voice embedding", ["PyTorch", "speaker encoder checkpoint", "preprocessed reference audio"]),
        ("Tacotron Voice Synthesizer", "synthesizer/models/tacotron.py", 328, "Tacotron sequence-to-sequence synthesizer that generates mel spectrograms conditioned on text and a speaker embedding.", "speaker-conditioned-tacotron-synthesis", "Speaker-conditioned Tacotron synthesis", ["PyTorch", "Tacotron checkpoint", "speaker embedding"]),
        ("WaveRNN Vocoder", "vocoder/models/fatchord_version.py", 88, "WaveRNN neural vocoder that converts generated mel spectrograms into audio waveforms.", "wavernn-neural-vocoding", "WaveRNN neural vocoding", ["PyTorch", "WaveRNN checkpoint", "mel spectrogram"]),
    ]
    models = []
    for name, path, line, description, slug, cap_name, deps in model_specs:
        entity = review.make("MODEL", name, path, line)
        review.finish(
            entity,
            description,
            [(slug, cap_name, [name.lower()])],
            "SECURITY REVIEW REQUIRED",
            "operational:07",
            "CORE" if name == "Speaker Encoder" else "MODULE",
            "PARTIAL",
            deps,
            "One stage of the SV2TTS voice-cloning pipeline.",
            categories,
            [],
            extra={"identity_sensitivity": "voice biometric and synthesized identity"},
        )
        models.append(entity)

    pipeline = review.make("COMPONENT", "SV2TTS Voice Cloning Pipeline", "demo_cli.py", 1)
    review.finish(
        pipeline,
        "Three-stage inference composition that embeds a reference speaker, synthesizes text-conditioned spectrograms and vocodes them into speech.",
        [("three-stage-sv2tts-voice-cloning", "Three-stage SV2TTS voice cloning", ["real-time voice cloning pipeline", "speaker encoder synthesizer vocoder"])],
        "SECURITY REVIEW REQUIRED",
        "operational:07",
        "CORE",
        "PARTIAL",
        ["Speaker Encoder", "Tacotron Voice Synthesizer", "WaveRNN Vocoder", "pretrained checkpoints"],
        "Composes the three separately reusable models.",
        categories,
        [],
    )
    cli = review.make("CLI", "SV2TTS demo_cli.py", "demo_cli.py", 14)
    review.finish(
        cli,
        "Command-line configuration and inference demonstration for loading SV2TTS checkpoints, cloning a reference voice and synthesizing arbitrary text.",
        [("command-line-voice-cloning", "Command-line voice cloning", ["SV2TTS CLI", "voice cloning demo CLI"])],
        "SECURITY REVIEW REQUIRED",
        "operational:07",
        "COMPONENT",
        "PARTIAL",
        ["SV2TTS pipeline", "ffmpeg", "input reference audio"],
        "Operational surface over the model pipeline.",
        categories,
        [],
    )
    for model in models:
        review.relate("DEPENDS_ON", pipeline["id"], model["id"], "demo_cli.py", 14)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:07",
        {
            "PACKAGE": "SV2TTS package retained.",
            "MODEL": "Speaker encoder, Tacotron synthesizer and WaveRNN vocoder retained as distinct stages.",
            "COMPONENT": "Composed inference pipeline retained.",
            "CLI": "Command-line inference surface retained.",
            "WORKFLOW": "Generic CI is not an independent capability.",
        },
        deep_review="Voice-identity trigger reviewed narrowly. The implementation creates a voice representation from a few seconds of audio and generates arbitrary speech; the source does not establish speaker consent, provenance marking or misuse controls. It is also explicitly described as an aging research implementation.",
        details=["training data loaders", "GUI toolbox", "low-level neural layers", "generic CI"],
    )
    return complete_scoped(
        review,
        result,
        [("README.md", 1), ("encoder/model.py", 12), ("demo_cli.py", 14)],
        "Inventory is complete. Any reuse requires affirmative speaker consent, provenance/disclosure and anti-impersonation policy; model quality and runtime safeguards were not tested.",
    )


def review_slack_mcp() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/slack-mcp-server",
        "b88c0de3f706f4f07337c9eda7133c736d1c9524",
    )
    categories = [
        "category:mcp-servers",
        "category:developer-tools",
        "category:business-applications",
        "category:productivity",
        "category:iam",
    ]

    server_entity = one(review, "MCP_SERVER", path="pkg/server/server.go")
    cli_entity = one(review, "CLI", path="npm/slack-mcp-server/package.json")
    package_entity = one(review, "PACKAGE", path="npm/slack-mcp-server/package.json")
    retained = {server_entity["id"], cli_entity["id"], package_entity["id"]}
    for entity in list(review.existing):
        if entity["id"] not in retained:
            review.drop(entity)

    review.finish(
        server_entity,
        "Go Model Context Protocol server exposing Slack conversations, search, channels, users, user groups, reactions, attachments and saved-item operations over stdio, SSE or streamable HTTP transports.",
        [("slack-model-context-protocol-server", "Slack Model Context Protocol server", ["Slack MCP", "slack-mcp-server"])],
        "SECURITY REVIEW REQUIRED",
        "operational:02",
        "CORE",
        "FULL",
        ["Slack bot/OAuth token or browser xoxc/xoxd session", "mcp-go", "network access to Slack"],
        "Primary server providing the twenty-two tools represented below and Slack channel/user resources.",
        categories,
        [],
        extra={"transports": ["stdio", "SSE", "streamable HTTP"], "credential_modes": ["bot token", "OAuth token", "browser session tokens"]},
    )
    review.finish(
        cli_entity,
        "npm-distributed command-line launcher that selects and executes the matching prebuilt Slack MCP server binary.",
        [("slack-mcp-command-line-launcher", "Slack MCP command-line launcher", ["slack-mcp-server CLI"])],
        "INTEGRATE VIA MCP",
        "operational:02",
        "COMPONENT",
        "FULL",
        ["supported platform binary npm package", "Node.js/npm"],
        "Distribution surface for the Go MCP server.",
        categories,
        [],
    )
    review.finish(
        package_entity,
        "Cross-platform npm wrapper package for installing and launching the prebuilt Slack MCP server.",
        [("cross-platform-slack-mcp-package", "Cross-platform Slack MCP package", ["Slack MCP npm package"])],
        "INTEGRATE VIA MCP",
        "operational:02",
        "COMPONENT",
        "FULL",
        ["one architecture-specific optional dependency"],
        "Architecture-specific packages are delivery variants rather than independent capabilities.",
        categories,
        [],
        extra={"platform_variants": ["darwin-amd64", "darwin-arm64", "linux-amd64", "linux-arm64", "windows-amd64", "windows-arm64"]},
    )

    tool_specs = [
        ("conversations_history", 27, "Read paginated messages from a Slack channel or direct message.", "slack-conversation-history", "Slack conversation history", False),
        ("conversations_replies", 28, "Read paginated replies from a Slack message thread.", "slack-thread-replies", "Slack thread replies", False),
        ("conversations_add_message", 29, "Send a message or thread reply, including optional Block Kit content.", "slack-send-message", "Slack message sending", True),
        ("reactions_add", 30, "Add an emoji reaction to a Slack message.", "slack-add-reaction", "Slack reaction creation", True),
        ("reactions_remove", 31, "Remove an emoji reaction from a Slack message.", "slack-remove-reaction", "Slack reaction removal", True),
        ("attachment_get_data", 32, "Download bounded Slack attachment content and metadata by file id.", "slack-attachment-retrieval", "Slack attachment retrieval", False),
        ("conversations_search_messages", 33, "Search Slack messages using the authenticated workspace search interface.", "slack-message-search", "Slack message search", False),
        ("conversations_unreads", 34, "List unread Slack conversations and their unread messages.", "slack-unread-conversations", "Slack unread conversations", False),
        ("conversations_mark", 35, "Advance a Slack conversation's read marker.", "slack-mark-conversation-read", "Slack conversation read marker", True),
        ("conversations_leave", 36, "Leave a Slack channel.", "slack-leave-channel", "Slack channel leave", True),
        ("conversations_join", 37, "Join a Slack channel.", "slack-join-channel", "Slack channel join", True),
        ("channels_list", 38, "List Slack channels visible to the authenticated identity.", "slack-channel-listing", "Slack channel listing", False),
        ("channels_me", 39, "List Slack channels to which the authenticated identity belongs.", "slack-member-channel-listing", "Slack member-channel listing", False),
        ("usergroups_list", 40, "List Slack user groups and optional membership/default-channel details.", "slack-usergroup-listing", "Slack user-group listing", False),
        ("usergroups_me", 41, "Add or remove the authenticated user from a Slack user group.", "slack-self-usergroup-membership", "Slack self user-group membership", True),
        ("usergroups_create", 42, "Create a Slack user group.", "slack-usergroup-creation", "Slack user-group creation", True),
        ("usergroups_update", 43, "Update Slack user-group name, handle, description or default channels.", "slack-usergroup-update", "Slack user-group update", True),
        ("usergroups_users_update", 44, "Replace the complete member list of a Slack user group.", "slack-usergroup-members-replacement", "Slack user-group member replacement", True),
        ("users_search", 45, "Search Slack users visible to the authenticated identity.", "slack-user-search", "Slack user search", False),
        ("saved_list", 46, "List messages in the authenticated user's Save for Later panel.", "slack-saved-item-listing", "Slack saved-item listing", False),
        ("saved_update", 47, "Update completion and due-date state for a Slack saved item.", "slack-saved-item-update", "Slack saved-item update", True),
        ("saved_clear_completed", 48, "Bulk-clear completed items from Slack Save for Later.", "slack-clear-completed-saved-items", "Slack completed saved-item clearing", True),
    ]
    for name, line, description, slug, cap_name, mutating in tool_specs:
        entity = review.make("TOOL", name, "pkg/server/server.go", line)
        review.finish(
            entity,
            description,
            [(slug, cap_name, [name])],
            "SECURITY REVIEW REQUIRED" if mutating else "INTEGRATE VIA MCP",
            "operational:02",
            "COMPONENT",
            "FULL",
            ["Slack MCP server", "credential with matching Slack access"],
            "One independently invocable MCP tool provided by the server.",
            categories,
            [],
            extra={"mutating": mutating, "mcp_tool_name": name},
        )
        review.relate("PROVIDES", server_entity["id"], entity["id"], "pkg/server/server.go", line)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:02",
        {
            "MCP_SERVER": "Production Slack MCP server retained; test server removed.",
            "TOOL": "Twenty-two explicitly registered production tools retained; test tool removed.",
            "CLI": "npm launcher retained.",
            "PACKAGE": "One cross-platform wrapper retained; six architecture packages recorded as variants.",
            "WORKFLOW": "Repository testing/release CI is not catalogued as a standalone capability.",
        },
        deep_review="Authentication and mutation trigger reviewed narrowly. Read access follows the supplied Slack identity; browser-session-only saved-item tools require xoxc/xoxd credentials; message, reaction and attachment tools are opt-in when no explicit tool allowlist is supplied, while several membership/read-state tools are mutating. MCP annotations label read-only and destructive operations, but deployment must still constrain credentials and enabled tools.",
        details=["test MCP server/tool", "architecture-specific npm packages", "project CI workflows", "provider internals"],
    )
    return complete_scoped(
        review,
        result,
        [("pkg/server/server.go", 27), ("pkg/server/server.go", 97), ("docs/01-authentication-setup.md", 1)],
        "Inventory is complete. Deployment requires least-privilege Slack credentials, explicit enabled-tool policy, protected browser-session tokens and confirmation/audit controls for mutating operations; no Slack call was executed.",
    )


def main() -> None:
    results = [
        review_deep_live_cam(),
        review_mobile_agent(),
        review_agent_sdk_mobile(),
        review_voice_cloning(),
        review_slack_mcp(),
    ]
    r.build()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
