# Flutter

Use this reference for applications using the public `nosmai_effects_sdk` package.

## Verified baseline

Last verified 24 September 2026:

- Flutter package: `nosmai_effects_sdk` `1.0.3`
- Flutter: 3.22 or later
- Dart: 3 or later
- Android: API 24+, physical `arm64-v8a` or `armeabi-v7a` device
- iOS: iOS 15+, physical arm64 device
- Native dependencies used by the published package: Android `3.0.5`, iOS `NosmaiCameraSDK ~> 3.0.5`

Verify the current version on [pub.dev](https://pub.dev/packages/nosmai_effects_sdk) before upgrading.

## Install

```sh
flutter pub add nosmai_effects_sdk:^1.0.3
flutter pub add permission_handler
```

The published `1.0.3` package resolves its Android `3.0.5` AAR through the plugin's Gradle configuration and its iOS framework through CocoaPods. Do not add a manual `nosmai-release.aar` or framework copy on top of this package. If an older guide or existing project contains a manual copy, inspect the resolved dependency graph before removing or retaining it; the final application must contain exactly one native SDK version.

Set Android `minSdk` to at least 24. Set iOS to at least 15 and run CocoaPods:

```ruby
platform :ios, '15.0'
```

Add camera and internet permissions on Android, and `NSCameraUsageDescription` on iOS. Add microphone and photo-library permissions only for the features that need them.

## Initialize once

Register status handling before initialization and keep separate app-bound keys per platform:

```dart
final licenseSubscription =
    NosmaiFlutter.instance.onLicenseStatusChanged.listen((status) {
  handleLicenseStatus(status);
});

final accepted = await NosmaiFlutter.initialize(runtimeLicenseKey);
if (!accepted) {
  throw StateError('Nosmai initialization was not accepted');
}
```

Do not log `runtimeLicenseKey`. The key must match the Android application ID or iOS bundle identifier of the installed build.

## Mount the preview and apply state

Mount one preview only after initialization succeeds. Apply or restore controls in `onInitialized`, not immediately after constructing the widget:

```dart
NosmaiCameraPreview(
  onInitialized: () async {
    await NosmaiFlutter.instance.applySkinSmoothing(0.35);
    await restoreSelectedEffects();
  },
  onError: handleCameraError,
)
```

Normal beauty strengths are clamped to `0.0` through `1.0`. Use the method that exists in the installed package. Do not invent a generic method such as `applyMakeupBlendLevel` when the typed API exposes feature-specific makeup methods.

## Camera-screen lifecycle

`NosmaiCameraPreview` observes foreground/background lifecycle and owns its native platform view. The host still owns navigation and application state.

- Keep the SDK initialized when temporarily leaving and returning to camera functionality.
- Before intentionally removing an active preview route, await `NosmaiFlutter.instance.endCameraSession()` while the old platform view still exists.
- Let the old widget dispose before mounting the next preview.
- Apply stored beauty/effect values again from the next preview's `onInitialized` callback.
- Use `pauseCamera()` and `resumeCamera()` only for temporary camera hardware pauses when the preview session remains logically active.
- Do not call `NosmaiFlutter.instance.dispose()` on every route change. It closes process-level streams and begins permanent cleanup; reserve it for final SDK shutdown.
- Cancel application-owned stream subscriptions in the owning object's `dispose` method.

An initialization call is idempotent for the current logical SDK session. Repeated calls do not replace proper camera-session teardown.

## Cloud Filters

```dart
final filters = await NosmaiFlutter.instance.getCloudFilters();
final selected = filters.first;

final result = await NosmaiFlutter.instance.downloadCloudFilter(
  selected.cloudIdentifier,
);
final path = (result['path'] ?? result['localPath']) as String?;
if (path == null || path.isEmpty) {
  throw StateError('Cloud Filter returned no local path');
}

await NosmaiFlutter.instance.applyEffect(path);
```

Use `cloudIdentifier` for download/cache operations and the returned local path for effect application. Deduplicate repeated taps while download or apply is in progress.

## Native dependency diagnostics

When Flutter behavior differs by platform:

- Run `flutter pub deps` and inspect `pubspec.lock`.
- Inspect Android runtime dependencies and every `android/**/libs` directory for old AARs.
- Inspect `ios/Podfile.lock` for the resolved `NosmaiCameraSDK` version.
- Run `flutter clean` after intentionally changing native binary versions.
- Use a physical device; an iOS Simulator and x86 Android emulator are not valid runtime tests.

## Common failures

| Symptom | Check |
| --- | --- |
| License callback becomes invalid | Final app identity, platform-specific key, network, project entitlement, automatic time, and duplicate/stale native SDKs |
| Build reports duplicate classes or native libraries | Remove the extra manual AAR and keep one native SDK path |
| iOS reports `Pods_Runner` missing | Run `flutter pub get`, reinstall pods, and open the workspace |
| Preview works only on first route entry | Await `endCameraSession`, dispose the old route, mount one new preview, then reapply state in `onInitialized` |
| Effect call logs success but is invisible | Confirm preview readiness, entitlement, a nonzero supported value, and the active camera session |
| App resumes without its selected effect | Persist controls in app state and reapply them after preview readiness |
| Android install fails by ABI | Confirm the device and packaged native libraries share `arm64-v8a` or `armeabi-v7a` |

## Validation

Run `flutter analyze`, build each changed native platform, and test on physical devices. Always test background/foreground and two complete open/close camera cycles, because a first-launch-only test does not validate lifecycle cleanup.

## Official references

- [Flutter installation](https://nosmai.com/docs/effects/installation/flutter/)
- [Flutter quickstart](https://nosmai.com/docs/effects/quickstart/flutter/)
- [Flutter package](https://pub.dev/packages/nosmai_effects_sdk)
- [Flutter source and example](https://github.com/nosmai/nosmai_effects_sdk_flutter)
- [License key flow](https://nosmai.com/docs/effects/license-key/)
- [Cloud Filters](https://nosmai.com/docs/effects/concepts/cloud-filters/)
