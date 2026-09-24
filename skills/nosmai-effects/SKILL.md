---
name: nosmai-effects
description: Integrate, upgrade, and troubleshoot Nosmai Effects on iOS, Android, Flutter, React Native, or Web. Use for SDK installation, licensing, camera lifecycle, beauty and AR effects, protected .nosmai packages, Cloud Filters, capture, recording, processed output, or streaming integration. Do not use for Nosmai Moderation or unreleased Try-ons work.
---

# Nosmai Effects

Build against the public Nosmai Effects contract and leave the host application in a verifiable state.

## Route the task

Read only the reference needed for the target platform. Read multiple references when a wrapper and its native host are both involved.

- iOS: [references/ios.md](references/ios.md)
- Android: [references/android.md](references/android.md)
- Flutter: [references/flutter.md](references/flutter.md)
- React Native: [references/react-native.md](references/react-native.md)
- Web: [references/web.md](references/web.md)

For platform comparisons, start with the [platform support matrix](https://nosmai.com/docs/effects/platform-support/), then verify the current package or release before making version, ABI, size, or feature-parity claims.

For installation, upgrade, compatibility, or release work, read [`versions.json`](versions.json) before the platform reference. It is the skill's single maintained version snapshot; do not copy version numbers from one platform guide into another.

## Source-of-truth order

Nosmai releases independently across native SDKs and wrappers. Never infer compatibility from similar version numbers.

1. Inspect the API and dependency metadata of the artifact actually installed in the project.
2. Read the matching record in [`versions.json`](versions.json).
3. Check the latest official registry entry or GitHub release for the same artifact.
4. Use the matching Nosmai documentation page.
5. If these disagree, do not silently combine instructions. Report the discrepancy and follow the installed artifact unless the user asks to upgrade.

Use only official sources:

- [Nosmai Effects documentation](https://nosmai.com/docs/effects/)
- [Android releases](https://github.com/nosmai/nosmai_effects_sdk_android/releases)
- [iOS releases](https://github.com/nosmai/nosmai_effects_sdk_ios/releases)
- [Flutter package](https://pub.dev/packages/nosmai_effects_sdk)
- [React Native package](https://www.npmjs.com/package/@nosmai/react-native-effects-sdk)

## Release maintenance

When a public SDK or wrapper is released, update the matching record and `last_verified` in [`versions.json`](versions.json). Do not hand-edit content between `BEGIN GENERATED` and `END GENERATED` comments. From the repository root, run:

```sh
python3 skills/nosmai-effects/scripts/sync_versions.py --write --verify-public
python3 skills/nosmai-effects/scripts/sync_versions.py --check
```

The Web preview has no public registry check and must be confirmed from its authorized release record. Review wrapper-owned native versions and ABIs independently; a new native SDK release does not automatically change Flutter or React Native compatibility.

## Integration workflow

1. Identify the platform, installed package version, native SDK version, application identity, device architecture, and requested capability.
2. Inspect existing dependencies before adding anything. Keep exactly one Nosmai native SDK per platform target.
3. Confirm the final Android application ID, iOS bundle identifier, or licensed Web origin matches the key's registered identity.
4. Register license and error listeners before initialization when the platform exposes them. Initialize once and wait for acceptance before starting camera processing.
5. Mount or attach one Nosmai preview, wait for preview or pipeline readiness, and only then apply visible effects.
6. Preserve one camera owner. Do not start a second host, WebRTC, or streaming camera when Nosmai already owns capture.
7. Pause, resume, end, and dispose the camera using the platform lifecycle contract. Do not confuse ending a camera screen with permanently disposing the process-wide SDK.
8. Validate the smallest relevant build, then test camera, background/foreground, screen reopening, and effect restoration on a supported physical device.

## Non-negotiable rules

- Never commit, print, screenshot, or include a complete license key in diagnostics. Redact it to a short suffix if correlation is necessary.
- Do not expose private service endpoints, request signing, internal models, proprietary implementation details, or unrelated third-party technology in generated application logs or public documentation.
- Use verified release assets. Do not copy an AAR or framework from another app, a build cache, a chat attachment, or an unverified mirror.
- Do not modify, unpack, rename internally, or regenerate a protected `.nosmai` package. Apply the authorized file through the public SDK API.
- Do not put proprietary AARs, frameworks, authorized Web archives, license keys, or licensed `.nosmai` assets in a public repository or public package.
- Treat license initialization acceptance and final license status as distinct when a platform reports verification asynchronously.
- A confirmed invalid or expired license is not a camera crash. Keep the application responsive and present an appropriate recovery path.
- Most normal beauty strengths use `0.0` through `1.0`. Do not pass percentages such as `50` or multiply values unless the exact public method documents a different signed range.
- Apply beauty state after preview readiness and reapply the app's stored preset when a new preview session is created.

## Local and Cloud Filters

Keep package origin and lifecycle explicit:

- A bundled/local package already has an app-readable path.
- A Cloud Filter begins as catalog metadata, downloads by its cloud identifier, and returns a local cached path.
- Apply the returned local path, but retain the cloud identifier for cache, update, and removal operations. Do not reclassify a cached Cloud Filter as an app-bundled local asset.
- Deduplicate concurrent downloads per cloud identifier. A completed cache download may outlive the screen that initiated it; UI updates must not.
- Removing an active effect and deleting its cached package are separate operations.

## Validation

Use checks proportional to the change:

- Static analysis or type checking for the wrapper language.
- Dependency inspection to detect stale or duplicate native SDKs.
- A clean Android/iOS build when native dependencies change.
- A supported physical ARM device for camera, effects, lifecycle, recording, streaming, and performance tests.
- A signed release build before making store-size, ABI-delivery, minification, or production-readiness claims.

Report what was verified, on which platform/device, and what remains untested. Do not describe a compile-only result as runtime verification.
