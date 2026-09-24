# React Native

Use this reference for the public `@nosmai/react-native-effects-sdk` package, including Expo development builds.

## Verified baseline

<!-- BEGIN GENERATED:version-react-native-baseline -->
Last verified 24 September 2026 from the published npm `1.0.0` artifact:

- Package: `@nosmai/react-native-effects-sdk` `1.0.0`
- Expo: `>=54.0.0 <55.0.0` with a custom development or EAS build
- React Native: `>=0.81.5 <0.82.0`
- React: `>=19.1.0 <20`
- Node.js: 20.19.4 or later
- Architecture: New Architecture only, using TurboModules and Fabric
- Android: API 24+, compile SDK 36, Java 17, physical `arm64-v8a` device
- iOS: iOS 15+, physical arm64 device
- Native baseline in the published package: Android `3.0.4` and iOS `3.0.4`

The published `1.0.0` Android package supports `arm64-v8a`. Do not inherit ABI claims from the standalone native SDK; verify the exact npm artifact first.
<!-- END GENERATED:version-react-native-baseline -->

## Install

<!-- BEGIN GENERATED:version-react-native-install -->
```sh
yarn add @nosmai/react-native-effects-sdk@1.0.0
```

The npm package does not redistribute the proprietary Android AAR. Obtain the authorized AAR required by the package, verify it, place one copy at `android/app/libs/nosmai-release.aar`, and link it from the host app. Do not commit it to a public repository.

The iOS podspec resolves its compatible `NosmaiCameraSDK`; run CocoaPods from the application and use a physical device.
<!-- END GENERATED:version-react-native-install -->

## Expo

Expo Go cannot load the custom native module. Use `expo-dev-client`, a local native build, or EAS.

The packaged config plugin accepts an app-owned Android AAR path and permission descriptions. Keep the source AAR outside generated `android/` when running `expo prebuild --clean`, for example under a private `vendor/` directory. The config plugin must not receive or store the runtime license key.

After configuring the plugin:

```sh
npx expo install expo-dev-client
npx expo prebuild --clean
npx expo run:android
```

Use `npx expo run:ios --device` for iOS. Warn before `--clean` when the project contains unrelated manual native changes because prebuild recreates the native directories.

## Preview and initialization

Mount the Fabric view before starting native processing. Register listeners before initialization because final license verification is asynchronous:

```tsx
import { useEffect, useState } from 'react';
import {
  NosmaiCameraSdk,
  NosmaiCameraView,
} from '@nosmai/react-native-effects-sdk';

function EffectsPreview({ licenseKey }: { licenseKey: string }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (!mounted) return;

    const license = NosmaiCameraSdk.addLicenseStatusChangedListener(
      handleLicenseStatus,
    );
    const errors = NosmaiCameraSdk.addErrorListener(handleNosmaiError);
    let disposed = false;

    void (async () => {
      const accepted = await NosmaiCameraSdk.initialize(licenseKey);
      if (!accepted || disposed) return;
      await NosmaiCameraSdk.configureCamera({ position: 'front' });
      if (!disposed) await NosmaiCameraSdk.startProcessing();
    })().catch(handleNosmaiError);

    return () => {
      disposed = true;
      license.remove();
      errors.remove();
      void NosmaiCameraSdk.cleanup().catch(handleNosmaiError);
    };
  }, [licenseKey, mounted]);

  return (
    <NosmaiCameraView
      style={{ flex: 1 }}
      cameraPosition="front"
      mirror
      onLayout={() => setMounted(true)}
      onReady={handlePreviewReady}
      onError={handleNosmaiError}
    />
  );
}
```

Request Android camera permission before `startProcessing`. Treat `onReady` as render readiness; a resolved start request alone does not prove that a processed frame rendered.

## Lifecycle

- Keep one `NosmaiCameraView` owner at a time.
- Remove event subscriptions during cleanup.
- Await or serialize cleanup before mounting another processing view.
- Reapply the application's beauty and effect state after the next `onReady` event.
- Keep the platform key stable for the process on the published compatibility line.
- Do not use LiveKit, WebRTC, or another camera module to open a second capture session when Nosmai owns the camera.

## Cloud Filters

Check entitlement before showing the catalog. Use the catalog item's cloud identifier for download and cache removal, and use the returned local path for `applyEffect`. Download progress is advisory; the returned Promise is authoritative. Remove active visual state before deleting its cached package.

## Common failures

| Symptom | Check |
| --- | --- |
| Native module unavailable | New Architecture, native rebuild, autolinking, and Expo Go usage |
| Android AAR cannot be resolved | Authorized file path, host `implementation`, and config-plugin output |
| iOS links for Simulator and fails | Use a physical arm64 device |
| License is invalid | Final package/bundle identity, platform-specific key, project state, network, time, and stale native artifact |
| Preview starts but no processed frame appears | Wait for Fabric view mount and `onReady`; verify one camera owner |
| Second preview freezes | Complete the previous view/track/camera cleanup before mounting a new view |
| TypeScript method is missing | Check the installed package declarations; do not assume Flutter/native method names exist in React Native |

## Validation

Run type checking and a clean native build. Test a signed development/release build on physical Android and iOS devices, including permission denial, foreground/background, two camera-screen cycles, effect restoration, capture, recording, Cloud Filter reuse, and any streaming bridge.

## Official references

- [React Native installation](https://nosmai.com/docs/effects/installation/react-native/)
- [React Native quickstart](https://nosmai.com/docs/effects/quickstart/react-native/)
- [npm package](https://www.npmjs.com/package/@nosmai/react-native-effects-sdk)
- [Source repository](https://github.com/nosmai/nosmai_effects_sdk_react_native)
- [License key flow](https://nosmai.com/docs/effects/license-key/)
