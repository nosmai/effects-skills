# Web

Use this reference for the authorized Nosmai Effects Web developer preview.

## Verified baseline

Last verified 24 September 2026:

- Web SDK: `0.2.0` developer preview
- Distribution: authorized `nosmai-web-sdk-0.2.0.tgz` archive
- Package import: `@nosmai/web-sdk`
- Runtime: a modern browser in HTTPS or on `localhost`
- Required browser capabilities: camera access, WebGL2, WebAssembly, and Web Crypto
- Toolchain: Node.js 20.19+ or 22.12+ and an ESM-capable bundler

The Web preview is not a public npm release. Do not replace the authorized archive with an unverified package that happens to use the same import name.

## Install

Store the authorized archive in a private application-owned location and install it as a file dependency:

```sh
npm install ./vendor/nosmai-web-sdk-0.2.0.tgz
```

Do not commit the archive, licensed effect packages, or a complete licence key to a public repository. Ensure the lockfile resolves the expected local archive.

## Browser and deployment requirements

- Use HTTPS in deployed environments. Camera access on plain HTTP is not supported.
- Start camera access from a user gesture so browser permission prompts are reliable.
- If the experience is embedded, explicitly allow camera access:

```html
<iframe src="https://camera.example.com" allow="camera"></iframe>
```

- Configure Content Security Policy and CORS for the application's own scripts, workers, WASM files, effect packages, and authorized network destinations.
- Keep optional runtime assets on controlled, versioned URLs. Do not expose private service endpoints or signing material in frontend configuration.
- The licence key is bound to the registered Web origin. Development and production origins may require separate configuration.

## Minimal camera flow

Create one SDK instance for one canvas, verify the licence, and then start the camera:

```ts
import { NosmaiWebSDK } from '@nosmai/web-sdk'

const canvas = document.querySelector<HTMLCanvasElement>('#preview')
if (!canvas) throw new Error('Preview canvas is missing')

const sdk = await NosmaiWebSDK.create({
  canvas,
  camera: {
    facingMode: 'user',
    width: 1280,
    height: 720,
  },
  license: {
    publicKeyPem: runtimeVerificationKey,
    sdkVersion: '0.2.0',
  },
})

const status = await sdk.verifyLicense(runtimeLicenseKey)
if (status !== 'valid') throw new Error(`Licence status: ${status}`)

await sdk.startCamera()
const result = await sdk.applyEffect('/filters/first-effect.nosmai')
inspectCompatibility(result.compatibility)
```

The public verification key used by the browser is not a private signing key. Never place a private key in a Web bundle.

Do not modify or unpack `first-effect.nosmai`. Serve the exact authorized package bytes with appropriate access control and cache headers.

## Capability boundary

Web `0.2.0` is a developer preview, not a claim of mobile feature parity.

- Compatible authored `.nosmai` packages render into the configured canvas.
- Package parameters, face-aware effects, selected 3D content, triggers, and compatible background packages are preview capabilities.
- The compatibility result is authoritative for the selected package. Reject or explain a package whose required primitives are unsupported.
- Native-style direct beauty and reshape methods are not generally available. Use compatible authored packages instead.
- Cloud Filter catalog/download APIs, camera games, processed photo capture, processed video recording, background video, native off-screen streaming handoff, and custom host overlays are not available in the current Web preview.
- The processed visual output is the canvas. Browser capture or streaming built around that canvas is host-application work unless a documented Nosmai integration says otherwise.

## Lifecycle

- Keep one active SDK instance and one camera owner for a canvas.
- Use `pause()` and `resume()` for a temporarily retained session.
- Use `removeEffect()` to clear the active package without destroying the camera.
- Use `stopCamera()` when camera capture should end but the instance may remain.
- Call `destroy()` when the page or component permanently releases the SDK.
- Remove host event listeners and prevent late asynchronous UI updates after component unmount.

```ts
window.addEventListener('pagehide', () => {
  sdk.destroy()
})
```

## Common failures

| Symptom | Check |
| --- | --- |
| Package import cannot be resolved | Install the authorized archive and refresh the package-manager lockfile |
| Camera permission is denied | HTTPS or localhost, user gesture, browser permission, and iframe camera policy |
| WebGL initialization fails | WebGL2 availability, hardware acceleration, GPU/browser support, and restrictive policy |
| Licence is invalid | Registered origin, correct Web key, verification configuration, network, and automatic date/time |
| Effect package cannot be fetched | URL, authentication, CORS, Content Security Policy, and response integrity |
| Effect loads with missing visuals | Inspect the returned compatibility report and use a Web-compatible package |
| Camera remains active after navigation | Stop or destroy the owning SDK instance during component/page cleanup |

## Validation

Run type checking and a production bundle. Test the exact deployed origin in at least the browsers and GPUs the product supports. Verify permission denial, tab background/foreground, route reopening, camera switching when used, effect replacement/removal, compatibility reporting, and final camera cleanup.

Measure JavaScript chunks, optional runtime assets, authored packages, startup time, and sustained frame rate separately. Do not present a development bundle or a single desktop result as a universal size or performance figure.

## Official references

- [Web installation](https://nosmai.com/docs/effects/installation/web/)
- [Web quickstart](https://nosmai.com/docs/effects/quickstart/web/)
- [Platform support](https://nosmai.com/docs/effects/platform-support/)
- [License key flow](https://nosmai.com/docs/effects/license-key/)
- [Filters and effects](https://nosmai.com/docs/effects/concepts/filters-and-effects/)
