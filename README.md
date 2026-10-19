# Nosmai Effects Skills

This repository contains the `nosmai-effects` agent skill for integrating and troubleshooting [Nosmai Effects](https://nosmai.com/docs/effects/) across supported platforms.

## Included skill

```text
skills/
└── nosmai-effects/
    ├── SKILL.md
    ├── versions.json
    ├── scripts/
    │   └── sync_versions.py
    └── references/
        ├── ios.md
        ├── android.md
        ├── flutter.md
        ├── react-native.md
        └── web.md
```

The entrypoint routes an agent to one platform reference and defines shared rules for licensing, lifecycle, protected effect packages, Cloud Filters, security, and verification.

## Install

Clone the repository and copy the skill folder into the skills directory supported by your coding agent. For Codex:

```sh
git clone https://github.com/nosmai/effects-skills.git
mkdir -p ~/.codex/skills
cp -R effects-skills/skills/nosmai-effects ~/.codex/skills/nosmai-effects
```

Restart or reload the agent if it does not discover new skills automatically. Invoke the skill by asking for a Nosmai Effects integration or by naming `$nosmai-effects` explicitly.

## Version policy

SDK versions change independently. The skill requires agents to verify the installed package and the current official release instead of assuming that a version embedded in an old guide is still current.

<!-- BEGIN GENERATED:version-readme -->
The platform references were last verified on 19 October 2026. The generated snapshot below comes from [`skills/nosmai-effects/versions.json`](skills/nosmai-effects/versions.json):

| Platform | Verified public release |
| --- | --- |
| iOS | `NosmaiCameraSDK` `3.0.7` |
| Android | `nosmai-sdk-3.0.7.aar` |
| Flutter | `nosmai_effects_sdk` `2.0.2` |
| React Native | `@nosmai/react-native-effects-sdk` `2.0.1` |
| Web | `0.2.0` developer preview, authorized archive |
<!-- END GENERATED:version-readme -->

Always check [Nosmai Effects platform support](https://nosmai.com/docs/effects/platform-support/) before publishing version, feature, ABI, or compatibility claims.

## Release version update

Update [`versions.json`](skills/nosmai-effects/versions.json), including `last_verified`, then regenerate every version-aware section:

```sh
python3 skills/nosmai-effects/scripts/sync_versions.py --write --verify-public
python3 skills/nosmai-effects/scripts/sync_versions.py --check
```

The public check compares native GitHub releases, pub.dev, and npm. It also inspects published Flutter and React Native package metadata for declared native dependencies, platform requirements, peer ranges, and ABIs. The React Native host-owned Android AAR baseline and authorized Web preview have no machine-readable public registry record, so those values remain manual release checks. Commit the manifest and generated Markdown together. CI rejects stale generated sections and semantic versions written outside managed blocks, checks public releases on every change, and repeats the check weekly.

## Security

Do not add license keys, proprietary native binaries, authorized Web archives, or licensed `.nosmai` packages to this repository. Public examples must use placeholders and public SDK interfaces only.

## Official resources

- [Documentation](https://nosmai.com/docs/effects/)
- [Android releases](https://github.com/nosmai/nosmai_effects_sdk_android/releases)
- [iOS releases](https://github.com/nosmai/nosmai_effects_sdk_ios/releases)
- [Flutter package](https://pub.dev/packages/nosmai_effects_sdk)
- [React Native package](https://www.npmjs.com/package/@nosmai/react-native-effects-sdk)
