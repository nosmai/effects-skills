#!/usr/bin/env python3
"""Render and verify Nosmai Effects version snapshots from versions.json."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import tarfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SKILL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
MANIFEST_PATH = SKILL_ROOT / "versions.json"


def load_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported versions.json schema_version")

    date.fromisoformat(data["last_verified"])
    required = {"ios", "android", "flutter", "react_native", "web"}
    missing = required.difference(data.get("platforms", {}))
    if missing:
        raise ValueError(f"Missing platform records: {', '.join(sorted(missing))}")

    version_pattern = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
    for platform, details in data["platforms"].items():
        version = details.get("version", "")
        if not version_pattern.fullmatch(version):
            raise ValueError(f"Invalid {platform} version: {version!r}")
    return data


def display_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.day} {parsed.strftime('%B %Y')}"


def code_list(values: list[str], conjunction: str = " and ") -> str:
    formatted = [f"`{value}`" for value in values]
    if len(formatted) < 2:
        return "".join(formatted)
    return ", ".join(formatted[:-1]) + conjunction + formatted[-1]


def generated_sections(data: dict[str, Any]) -> dict[Path, dict[str, str]]:
    verified_iso = data["last_verified"]
    verified = display_date(verified_iso)
    p = data["platforms"]
    ios = p["ios"]
    android = p["android"]
    flutter = p["flutter"]
    rn = p["react_native"]
    web = p["web"]

    android_artifact = android["artifact"].format(version=android["version"])
    web_archive = web["archive"].format(version=web["version"])
    android_abis = code_list(android["abis"])
    rn_abis = code_list(rn["android_abis"])

    return {
        REPO_ROOT / "README.md": {
            "version-readme": f"""The platform references were last verified on {verified}. The generated snapshot below comes from [`skills/nosmai-effects/versions.json`](skills/nosmai-effects/versions.json):

| Platform | Verified public release |
| --- | --- |
| iOS | `{ios['package']}` `{ios['version']}` |
| Android | `{android_artifact}` |
| Flutter | `{flutter['package']}` `{flutter['version']}` |
| React Native | `{rn['package']}` `{rn['version']}` |
| Web | `{web['version']}` {web['status']}, authorized archive |""",
        },
        SKILL_ROOT / "references/ios.md": {
            "version-ios-baseline": f"""Last verified {verified}:

- Native SDK: `{ios['package']}` `{ios['version']}`
- Minimum deployment target: iOS {ios['minimum_ios']}
- Runtime target: physical {code_list(ios['architectures'])} iPhone or iPad
- Distribution: CocoaPods or the verified framework ZIP from the [official iOS release](https://github.com/{ios['source']['repository']}/releases/tag/{ios['release_tag']})
- Simulator: unsupported because the current framework has no simulator slice""",
            "version-ios-install": f"""CocoaPods is preferred:

```ruby
platform :ios, '{ios['minimum_ios']}.0'

target 'CameraApp' do
  use_frameworks!
  pod '{ios['package']}', '{ios['version']}'
end
```

Run `pod install --repo-update` and open the generated `.xcworkspace`. Do not also embed a manual framework.""",
        },
        SKILL_ROOT / "references/android.md": {
            "version-android-baseline": f"""Last verified {verified}:

- Native SDK: `{android_artifact}`
- Minimum Android API: {android['minimum_api']}
- Compile SDK baseline: {android['compile_sdk']}
- Java bytecode compatibility: Java {android['java']}
- Supported native ABIs: {android_abis}
- Runtime target: physical ARM Android device
- Unsupported runtime targets: x86 and x86_64 emulators""",
            "version-android-install": f"""Download the AAR and `SHA256SUMS` from the same official release. Verify the file before integration:

```sh
shasum -a 256 -c SHA256SUMS
```

Place the verified file in the native app module, for example `app/libs/{android_artifact}`, and add it once:

```kotlin
android {{
    compileSdk = {android['compile_sdk']}

    defaultConfig {{
        minSdk = {android['minimum_api']}
        ndk {{
            abiFilters += listOf({', '.join(json.dumps(abi) for abi in android['abis'])})
        }}
    }}

    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_{android['java']}
        targetCompatibility = JavaVersion.VERSION_{android['java']}
    }}
}}

dependencies {{
    implementation(files("libs/{android_artifact}"))
}}
```

This manual AAR step is for a native Android integration. A wrapper may resolve the AAR itself. Inspect the installed Flutter or React Native package before adding a second copy.""",
        },
        SKILL_ROOT / "references/flutter.md": {
            "version-flutter-baseline": f"""Last verified {verified}:

- Flutter package: `{flutter['package']}` `{flutter['version']}`
- Flutter: {flutter['minimum_flutter']} or later
- Dart: {flutter['minimum_dart']} or later
- Android: API {android['minimum_api']}+, physical device using {code_list(android['abis'], conjunction=' or ')}
- iOS: iOS {ios['minimum_ios']}+, physical {code_list(ios['architectures'])} device
- Native dependencies used by the published package: Android `{flutter['android_native_version']}`, iOS `{ios['package']} {flutter['ios_native_constraint']}`""",
            "version-flutter-install": f"""```sh
flutter pub add {flutter['package']}:^{flutter['version']}
flutter pub add permission_handler
```

The published `{flutter['version']}` package resolves its Android `{flutter['android_native_version']}` AAR through the plugin's Gradle configuration and its iOS framework through CocoaPods. Do not add a manual `nosmai-release.aar` or framework copy on top of this package. If an older guide or existing project contains a manual copy, inspect the resolved dependency graph before removing or retaining it; the final application must contain exactly one native SDK version.

Set Android `minSdk` to at least {android['minimum_api']}. Set iOS to at least {ios['minimum_ios']} and run CocoaPods:

```ruby
platform :ios, '{ios['minimum_ios']}.0'
```

Add camera and internet permissions on Android, and `NSCameraUsageDescription` on iOS. Add microphone and photo-library permissions only for the features that need them.""",
        },
        SKILL_ROOT / "references/react-native.md": {
            "version-react-native-baseline": f"""Last verified {verified} from the published npm `{rn['version']}` artifact:

- Package: `{rn['package']}` `{rn['version']}`
- Expo: `{rn['expo_range']}` with a custom development or EAS build
- React Native: `{rn['react_native_range']}`
- React: `{rn['react_range']}`
- Node.js: {rn['node_minimum']} or later
- Architecture: New Architecture only, using TurboModules and Fabric
- Android: API {rn['android_minimum_api']}+, compile SDK {rn['android_compile_sdk']}, Java {rn['android_java']}, physical {rn_abis} device
- iOS: iOS {rn['ios_minimum']}+, physical arm64 device
- Native baseline in the published package: Android `{rn['native_android_version']}` and iOS `{rn['native_ios_version']}`

The published `{rn['version']}` Android package supports {rn_abis}. Do not inherit ABI claims from the standalone native SDK; verify the exact npm artifact first.""",
            "version-react-native-install": f"""```sh
yarn add {rn['package']}@{rn['version']}
```

The npm package does not redistribute the proprietary Android AAR. Obtain the authorized AAR required by the package, verify it, place one copy at `android/app/libs/nosmai-release.aar`, and link it from the host app. Do not commit it to a public repository.

The iOS podspec resolves its compatible `{ios['package']}`; run CocoaPods from the application and use a physical device.""",
        },
        SKILL_ROOT / "references/web.md": {
            "version-web-baseline": f"""Last verified {verified}:

- Web SDK: `{web['version']}` {web['status']}
- Distribution: authorized `{web_archive}` archive
- Package import: `{web['package']}`
- Runtime: a modern browser in HTTPS or on `localhost`
- Required browser capabilities: camera access, WebGL2, WebAssembly, and Web Crypto
- Toolchain: Node.js {web['node_ranges'][0].removeprefix('>=')}+ or {web['node_ranges'][1].removeprefix('>=')}+ and an ESM-capable bundler

The Web preview is not a public npm release. Do not replace the authorized archive with an unverified package that happens to use the same import name.""",
            "version-web-install": f"""Store the authorized archive in a private application-owned location and install it as a file dependency:

```sh
npm install ./vendor/{web_archive}
```

Do not commit the archive, licensed effect packages, or a complete licence key to a public repository. Ensure the lockfile resolves the expected local archive.""",
        },
    }


def render_block(text: str, block_name: str, content: str, path: Path) -> str:
    begin = f"<!-- BEGIN GENERATED:{block_name} -->"
    end = f"<!-- END GENERATED:{block_name} -->"
    pattern = re.compile(
        rf"{re.escape(begin)}\n.*?\n{re.escape(end)}",
        flags=re.DOTALL,
    )
    replacement = f"{begin}\n{content.rstrip()}\n{end}"
    updated, count = pattern.subn(lambda _: replacement, text)
    if count != 1:
        raise ValueError(f"Expected one {block_name!r} block in {path}, found {count}")
    return updated


def validate_no_unmanaged_versions(path: Path, text: str) -> None:
    unmanaged_text = re.sub(
        r"<!-- BEGIN GENERATED:[^>]+ -->\n.*?\n<!-- END GENERATED:[^>]+ -->",
        "",
        text,
        flags=re.DOTALL,
    )
    semantic_versions = sorted(
        set(
            re.findall(
                r"(?<![\d.])\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?(?![\d.])",
                unmanaged_text,
            )
        )
    )
    if semantic_versions:
        values = ", ".join(semantic_versions)
        raise ValueError(
            f"Unmanaged semantic version in {path.relative_to(REPO_ROOT)}: {values}. "
            "Move it into a generated version block."
        )


def synchronize(data: dict[str, Any], write: bool) -> list[Path]:
    changed: list[Path] = []
    rendered_files: dict[Path, str] = {}
    for path, blocks in generated_sections(data).items():
        original = path.read_text(encoding="utf-8")
        rendered = original
        for block_name, content in blocks.items():
            rendered = render_block(rendered, block_name, content, path)
        validate_no_unmanaged_versions(path, rendered)
        rendered_files[path] = rendered
        if rendered != original:
            changed.append(path)
    if write:
        for path in changed:
            path.write_text(rendered_files[path], encoding="utf-8")
    return changed


def request_bytes(url: str, accept: str = "application/octet-stream") -> bytes:
    headers = {
        "Accept": accept,
        "User-Agent": "nosmai-effects-version-check",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def request_json(url: str) -> dict[str, Any]:
    return json.loads(request_bytes(url, accept="application/json"))


def read_tar_members(url: str, suffixes: dict[str, str]) -> dict[str, str]:
    payload = request_bytes(url)
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            result: dict[str, str] = {}
            for label, suffix in suffixes.items():
                normalized_suffix = suffix.lstrip("/")
                matches = [
                    member
                    for member in archive.getmembers()
                    if member.isfile() and member.name.endswith(normalized_suffix)
                ]
                if matches:
                    shallowest = min(len(Path(member.name).parts) for member in matches)
                    matches = [
                        member
                        for member in matches
                        if len(Path(member.name).parts) == shallowest
                    ]
                if len(matches) != 1:
                    raise ValueError(
                        f"Expected one {suffix!r} in published archive, found {len(matches)}"
                    )
                extracted = archive.extractfile(matches[0])
                if extracted is None:
                    raise ValueError(f"Could not read {matches[0].name!r}")
                result[label] = extracted.read().decode("utf-8")
            return result
    except (tarfile.TarError, UnicodeDecodeError) as error:
        raise ValueError(f"Invalid published package archive: {error}") from error


def require_pattern(
    platform: str,
    label: str,
    text: str,
    pattern: str,
    expected: str,
) -> list[str]:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return [f"{platform}: could not read {label} from the published package"]
    actual = match.group(1)
    if actual != expected:
        return [f"{platform}: {label} is {actual}, versions.json has {expected}"]
    return []


def verify_flutter_artifact(
    payload: dict[str, Any],
    flutter: dict[str, Any],
    android: dict[str, Any],
    ios: dict[str, Any],
) -> list[str]:
    files = read_tar_members(
        str(payload["latest"]["archive_url"]),
        {
            "gradle": "/android/build.gradle",
            "podspec": "/ios/nosmai_effects_sdk.podspec",
        },
    )
    errors: list[str] = []
    errors += require_pattern(
        "flutter",
        "Android native version",
        files["gradle"],
        r"com\.nosmai:nosmai-sdk:([^@\"']+)@aar",
        str(flutter["android_native_version"]),
    )
    errors += require_pattern(
        "flutter",
        "Android compile SDK",
        files["gradle"],
        r"^\s*compileSdk\s*=\s*(\d+)",
        str(android["compile_sdk"]),
    )
    errors += require_pattern(
        "flutter",
        "Android minimum API",
        files["gradle"],
        r"^\s*minSdk\s*=\s*(\d+)",
        str(android["minimum_api"]),
    )
    errors += require_pattern(
        "flutter",
        "Android Java version",
        files["gradle"],
        r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)",
        str(android["java"]),
    )
    abi_line = re.search(r"^\s*abiFilters\s+(.+)$", files["gradle"], re.MULTILINE)
    actual_abis = re.findall(r'[\"\']([^\"\']+)[\"\']', abi_line.group(1)) if abi_line else []
    if actual_abis != android["abis"]:
        errors.append(
            f"flutter: Android ABIs are {actual_abis}, versions.json has {android['abis']}"
        )
    errors += require_pattern(
        "flutter",
        "iOS native constraint",
        files["podspec"],
        r"s\.dependency\s+['\"]NosmaiCameraSDK['\"],\s*['\"]([^'\"]+)['\"]",
        str(flutter["ios_native_constraint"]),
    )
    errors += require_pattern(
        "flutter",
        "iOS minimum version",
        files["podspec"],
        r"s\.platform\s*=\s*:ios,\s*['\"]([^'\"]+)['\"]",
        f"{ios['minimum_ios']}.0",
    )
    return errors


def verify_react_native_artifact(
    payload: dict[str, Any],
    rn: dict[str, Any],
) -> list[str]:
    published = payload["versions"][rn["version"]]
    files = read_tar_members(
        str(published["dist"]["tarball"]),
        {
            "gradle": "/android/build.gradle",
            "podspec": "/NosmaiReactNativeCameraSdk.podspec",
        },
    )
    errors: list[str] = []
    expected_metadata = {
        "Expo peer range": (published.get("peerDependencies", {}).get("expo"), rn["expo_range"]),
        "React Native peer range": (
            published.get("peerDependencies", {}).get("react-native"),
            rn["react_native_range"],
        ),
        "React peer range": (published.get("peerDependencies", {}).get("react"), rn["react_range"]),
        "Node.js minimum": (published.get("engines", {}).get("node"), f">={rn['node_minimum']}"),
    }
    for label, (actual, expected) in expected_metadata.items():
        if actual != expected:
            errors.append(
                f"react_native: {label} is {actual!r}, versions.json has {expected!r}"
            )

    errors += require_pattern(
        "react_native",
        "Android minimum API",
        files["gradle"],
        r"minSdkVersion:\s*(\d+)",
        str(rn["android_minimum_api"]),
    )
    errors += require_pattern(
        "react_native",
        "Android compile SDK",
        files["gradle"],
        r"compileSdkVersion:\s*(\d+)",
        str(rn["android_compile_sdk"]),
    )
    errors += require_pattern(
        "react_native",
        "Android Java version",
        files["gradle"],
        r"sourceCompatibility\s+JavaVersion\.VERSION_(\d+)",
        str(rn["android_java"]),
    )
    abi_line = re.search(r"^\s*abiFilters\s+(.+)$", files["gradle"], re.MULTILINE)
    actual_abis = re.findall(r'[\"\']([^\"\']+)[\"\']', abi_line.group(1)) if abi_line else []
    if actual_abis != rn["android_abis"]:
        errors.append(
            f"react_native: Android ABIs are {actual_abis}, versions.json has {rn['android_abis']}"
        )
    errors += require_pattern(
        "react_native",
        "iOS native constraint",
        files["podspec"],
        r"s\.dependency\s+['\"]NosmaiCameraSDK['\"],\s*['\"]~>\s*([^'\"]+)['\"]",
        str(rn["native_ios_version"]),
    )
    errors += require_pattern(
        "react_native",
        "iOS minimum version",
        files["podspec"],
        r"s\.platform\s*=\s*:ios,\s*['\"]([^'\"]+)['\"]",
        f"{rn['ios_minimum']}.0",
    )
    if rn.get("native_android_verification") == "manual":
        print(
            "SKIP react_native Android native baseline: the host-owned AAR version "
            "is not machine-readable in the npm package"
        )
    return errors


def verify_public_versions(data: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    platforms = data["platforms"]
    for platform, details in platforms.items():
        source = details["source"]
        source_type = source["type"]
        if source_type == "manual":
            print(f"SKIP {platform}: {source['reason']}")
            continue

        try:
            if source_type == "github_release":
                payload = request_json(
                    f"https://api.github.com/repos/{source['repository']}/releases/latest"
                )
                actual = str(payload["tag_name"]).removeprefix("v")
            elif source_type == "pub":
                payload = request_json(
                    f"https://pub.dev/api/packages/{source['package']}"
                )
                actual = str(payload["latest"]["version"])
            elif source_type == "npm":
                encoded = source["package"].replace("/", "%2F")
                payload = request_json(f"https://registry.npmjs.org/{encoded}")
                actual = str(payload["dist-tags"]["latest"])
            else:
                raise ValueError(f"Unsupported source type {source_type!r}")
        except (KeyError, OSError, ValueError, urllib.error.URLError) as error:
            mismatches.append(f"{platform}: public version check failed: {error}")
            continue

        expected = str(details["version"])
        if actual != expected:
            mismatches.append(
                f"{platform}: versions.json has {expected}, public source reports {actual}"
            )
        else:
            print(f"OK   {platform}: {actual}")
            if platform == "flutter":
                mismatches.extend(
                    verify_flutter_artifact(
                        payload,
                        details,
                        platforms["android"],
                        platforms["ios"],
                    )
                )
            elif platform == "react_native":
                mismatches.extend(verify_react_native_artifact(payload, details))
    return mismatches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize version-aware Markdown from versions.json."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Update generated blocks")
    mode.add_argument("--check", action="store_true", help="Fail if generated blocks differ")
    parser.add_argument(
        "--verify-public",
        action="store_true",
        help="Compare public releases with versions.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_manifest()
        check_only = args.check or not args.write
        changed = synchronize(data, write=args.write)
        if changed and check_only:
            print("Generated version sections are stale:", file=sys.stderr)
            for path in changed:
                print(f"  - {path.relative_to(REPO_ROOT)}", file=sys.stderr)
            print(
                "Run: python3 skills/nosmai-effects/scripts/sync_versions.py --write",
                file=sys.stderr,
            )
            return 1
        if args.write:
            for path in changed:
                print(f"UPDATED {path.relative_to(REPO_ROOT)}")
            if not changed:
                print("Version sections already up to date")

        if args.verify_public:
            mismatches = verify_public_versions(data)
            if mismatches:
                for mismatch in mismatches:
                    print(f"ERROR {mismatch}", file=sys.stderr)
                return 1
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
