# Android app — development scaffold

The Android client is a native Kotlin/Jetpack Compose app. It currently supports account creation/sign-in, encrypted local session tokens, profile loading, availability mode display/updates, contact listing/add/edit/delete, refresh-token rotation, and sign-out.

## Open and run

Open this `android/` folder in Android Studio with JDK 17 or newer and allow Gradle sync. This environment has no Gradle executable or Android SDK available, so the app has not been built here. If Android Studio asks, generate a Gradle wrapper for the configured Gradle 8.9 distribution.

The default API URL is `http://10.0.2.2:8000/`, which reaches the host machine from an Android emulator. Start the backend separately after applying its migrations. For a physical device, override the URL with the development machine's LAN address using the Gradle property `ZORO_API_BASE_URL`.

Debug builds permit cleartext HTTP for local development. Release builds reject cleartext traffic; set `ZORO_API_BASE_URL` to an HTTPS endpoint before creating a release build.

## Security and current limits

- Access and refresh tokens are encrypted using AES-GCM with a key held in Android Keystore.
- This UI calls the backend's development-only auth endpoints. Email verification, password recovery, push registration, contacts UI, call history, and production configuration are not implemented.
- Never ship the emulator URL or development backend as a production configuration.

