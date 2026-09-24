# iOS

Use this reference for native iOS projects and for the iOS host side of Flutter or React Native integrations.

## Verified baseline

Last verified 24 September 2026:

- Native SDK: `NosmaiCameraSDK` `3.0.5`
- Minimum deployment target: iOS 15
- Runtime target: physical arm64 iPhone or iPad
- Distribution: CocoaPods or the verified framework ZIP from the [official iOS release](https://github.com/nosmai/nosmai_effects_sdk_ios/releases/tag/v3.0.5)
- Simulator: unsupported because the current framework has no simulator slice

Check [platform support](https://nosmai.com/docs/effects/platform-support/) and the [latest iOS release](https://github.com/nosmai/nosmai_effects_sdk_ios/releases/latest) before changing a version.

## Install

CocoaPods is preferred:

```ruby
platform :ios, '15.0'

target 'CameraApp' do
  use_frameworks!
  pod 'NosmaiCameraSDK', '3.0.5'
end
```

Run `pod install --repo-update` and open the generated `.xcworkspace`. Do not also embed a manual framework.

For manual installation, download `nosmai.framework.zip` and `SHA256SUMS` from the same release, verify them with `shasum -a 256 -c SHA256SUMS`, add the framework to the application target, and select **Embed & Sign**.

## Permissions

Add only the usage descriptions needed by enabled features:

```xml
<key>NSCameraUsageDescription</key>
<string>This app uses the camera for real-time effects.</string>
<key>NSMicrophoneUsageDescription</key>
<string>This app uses the microphone when recording video.</string>
<key>NSPhotoLibraryAddUsageDescription</key>
<string>This app saves captured media to your library.</string>
```

Camera permission is required for preview. Microphone and Photos access are feature-dependent.

## Initialization and preview order

Keep the key outside source control and initialize before reading camera or effects interfaces:

```objc
#import <nosmai/Nosmai.h>

[[NosmaiCore shared]
    initializeWithAPIKey:runtimeLicenseKey
              completion:^(BOOL success, NSError *error) {
  if (!success) {
    [self handleNosmaiError:error];
    return;
  }

  NosmaiCamera *camera = [NosmaiCore shared].camera;
  [camera attachToView:self.previewView];
  if ([camera startCapture]) {
    [[NosmaiCore shared].effects applySkinSmoothing:0.35f];
  }
}];
```

The host should:

1. Request camera permission.
2. Initialize once with the key issued for the signed bundle identifier.
3. Attach the preview on the main thread.
4. Start capture.
5. Apply effects only after camera/effects interfaces are ready.

## Lifecycle

- Stop capture and detach the preview when its screen disappears.
- Reattach and restart capture when the same initialized SDK returns to a camera screen.
- Keep one active camera owner.
- Call full SDK cleanup only when the logical SDK session is finished, not on every transient foreground/background event.
- Stop recording and streaming callbacks before releasing their consumers.

## Build and runtime checks

- Confirm the final bundle identifier matches the iOS identity registered in Nosmai Console.
- Inspect `Podfile.lock` for one intended `NosmaiCameraSDK` version.
- Confirm the app contains one embedded `nosmai.framework`.
- Build and run on a physical device.
- Test first launch, permission denial, background/foreground, camera-screen reopening, camera switching, active effects, recording, and any streaming path.

## Common failures

| Symptom | Check |
| --- | --- |
| `No such module 'nosmai'` or header not found | Run CocoaPods and open the workspace, not the project file |
| Simulator architecture/linker error | Select a physical arm64 device |
| `dyld` cannot load `nosmai.framework` | Ensure the manual framework is **Embed & Sign**, or use CocoaPods |
| `Pods_Runner` not found in Flutter | Regenerate pods from the Flutter project and open `Runner.xcworkspace` |
| License becomes invalid | Verify final bundle ID, iOS-specific key, project status, network, and automatic date/time |
| Effect call succeeds but is not visible | Wait for preview readiness, use a nonzero supported value, and confirm entitlement |
| Second camera screen is blank | Ensure the old screen detached/stopped before the new preview attached; do not initialize competing camera owners |

## Official references

- [iOS installation](https://nosmai.com/docs/effects/installation/ios/)
- [iOS quickstart](https://nosmai.com/docs/effects/quickstart/ios/)
- [License key flow](https://nosmai.com/docs/effects/license-key/)
- [iOS release repository](https://github.com/nosmai/nosmai_effects_sdk_ios)
- [CocoaPods package](https://cocoapods.org/pods/NosmaiCameraSDK)
