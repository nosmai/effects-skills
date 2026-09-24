# Nosmai Effects Skills

This repository contains the `nosmai-effects` agent skill for integrating and troubleshooting [Nosmai Effects](https://nosmai.com/docs/effects/) across supported platforms.

## Included skill

```text
skills/
└── nosmai-effects/
    ├── SKILL.md
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

The platform references were last verified on 24 September 2026 against:

| Platform | Verified public release |
| --- | --- |
| iOS | `NosmaiCameraSDK` `3.0.5` |
| Android | `nosmai-sdk-3.0.5.aar` |
| Flutter | `nosmai_effects_sdk` `1.0.3` |
| React Native | `@nosmai/react-native-effects-sdk` `1.0.0` |
| Web | `0.2.0` developer preview, authorized archive |

Always check [Nosmai Effects platform support](https://nosmai.com/docs/effects/platform-support/) before publishing version, feature, ABI, or compatibility claims.

## Security

Do not add license keys, proprietary native binaries, authorized Web archives, or licensed `.nosmai` packages to this repository. Public examples must use placeholders and public SDK interfaces only.

## Official resources

- [Documentation](https://nosmai.com/docs/effects/)
- [Android releases](https://github.com/nosmai/nosmai_effects_sdk_android/releases)
- [iOS releases](https://github.com/nosmai/nosmai_effects_sdk_ios/releases)
- [Flutter package](https://pub.dev/packages/nosmai_effects_sdk)
- [React Native package](https://www.npmjs.com/package/@nosmai/react-native-effects-sdk)
