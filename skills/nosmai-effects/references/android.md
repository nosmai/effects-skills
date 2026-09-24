# Android

Use this reference for native Android projects and when diagnosing the native host side of Flutter or React Native.

## Verified baseline

<!-- BEGIN GENERATED:version-android-baseline -->
Last verified 24 September 2026:

- Native SDK: `nosmai-sdk-3.0.5.aar`
- Minimum Android API: 24
- Compile SDK baseline: 35
- Java bytecode compatibility: Java 11
- Supported native ABIs: `arm64-v8a` and `armeabi-v7a`
- Runtime target: physical ARM Android device
- Unsupported runtime targets: x86 and x86_64 emulators
<!-- END GENERATED:version-android-baseline -->

Check the [latest Android release](https://github.com/nosmai/nosmai_effects_sdk_android/releases/latest) before changing the version.

## Native installation

<!-- BEGIN GENERATED:version-android-install -->
Download the AAR and `SHA256SUMS` from the same official release. Verify the file before integration:

```sh
shasum -a 256 -c SHA256SUMS
```

Place the verified file in the native app module, for example `app/libs/nosmai-sdk-3.0.5.aar`, and add it once:

```kotlin
android {
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(files("libs/nosmai-sdk-3.0.5.aar"))
}
```

This manual AAR step is for a native Android integration. A wrapper may resolve the AAR itself. Inspect the installed Flutter or React Native package before adding a second copy.
<!-- END GENERATED:version-android-install -->

## Permissions

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

Request camera permission at runtime. Request microphone permission only for audio recording or publishing.

## Initialization and preview order

Use the application context and the runtime key registered for the final application ID:

```java
NosmaiSDK.initialize(
    getApplicationContext(),
    runtimeLicenseKey
);

previewView.enableOesInput(true);
NosmaiSDK.startProcessing(previewView);

previewView.addOnPipelineReady(() -> {
    NosmaiBeauty.applySkinSmoothing(0.35f);
});
```

The camera source, preview input mode, orientation, and mirroring must agree. Prefer the qualified camera helper supplied by an official sample for production rather than inventing a second frame pipeline.

## Lifecycle

- Keep one active `NosmaiPreviewView` and one camera owner.
- On pause, close the camera session and pause the preview according to the public API.
- On resume, restore the preview/camera session without initializing a competing SDK instance.
- On final screen destruction, stop processing and release camera surfaces, sessions, devices, and owned worker threads.
- Persist effect values in application state and reapply them after a new pipeline-ready event.
- For streaming, publish Nosmai's processed output through the verified bridge; do not open a second camera in the streaming SDK.

## Dependency and ABI diagnostics

Check device ABI:

```sh
adb shell getprop ro.product.cpu.abilist
```

Inspect Gradle dependencies and the packaged APK/AAB when behavior differs across builds. Keep exactly one Nosmai AAR version. A file renamed to `nosmai-release.aar` is not proof of its version; inspect the artifact or replace it with a verified release.

For 32-bit testing, use a device whose ABI list starts with or contains `armeabi-v7a`, build that ABI, and confirm the packaged application includes Nosmai native libraries under `lib/armeabi-v7a/`.

## Common failures

| Symptom | Check |
| --- | --- |
| `INSTALL_FAILED_NO_MATCHING_ABIS` | Device and packaged app must share `arm64-v8a` or `armeabi-v7a` |
| `UnsatisfiedLinkError` | Verify AAR checksum, ABI contents, packaging rules, and duplicate copies |
| Duplicate classes/native libraries | Remove old or transitive AAR duplicates and keep one version |
| License reports invalid | Verify final `applicationId`, Android-specific key, network permission, project state, and automatic date/time |
| Camera error `CAMERA_IN_USE` | Release the previous camera controller before starting Nosmai |
| Black or frozen second session | Complete old camera/preview/stream teardown, then create one new session and reapply state after readiness |
| Effect method completes but nothing changes | Wait for pipeline readiness, use the documented range, and verify feature entitlement |

## Validation

Build a clean signed release, not only Debug. Test both supported ABIs where the app promises both. Exercise permission denial, app background/foreground, repeated screen entry, camera switching, active effect changes, Cloud Filter reuse, capture/recording, and streaming.

## Official references

- [Android installation](https://nosmai.com/docs/effects/installation/android/)
- [Android quickstart](https://nosmai.com/docs/effects/quickstart/android/)
- [License key flow](https://nosmai.com/docs/effects/license-key/)
- [Android releases](https://github.com/nosmai/nosmai_effects_sdk_android/releases)
