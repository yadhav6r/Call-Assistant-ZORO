# Android app — development scaffold

The Android client is a native Kotlin/Jetpack Compose app. It currently supports account creation/sign-in, encrypted local session tokens, profile loading, availability mode display/updates, contact listing/add/edit/delete, refresh-token rotation, and sign-out.

## Open and run

Open this `android/` folder in Android Studio Meerkat Patch 1 or newer with JDK 17 and allow Gradle sync. The project now targets API 36 and uses Android Gradle Plugin 8.11.1, which requires Gradle 8.13. This environment has no Gradle executable or Android SDK available, so the app has not been built here.

The default API URL is `http://10.0.2.2:8000/`, which reaches the host machine from an Android emulator. Start the backend separately after applying its migrations. For a physical device, override the URL with the development machine's LAN address using the Gradle property `ZORO_API_BASE_URL`.

Debug builds permit cleartext HTTP for local development and show account creation. Release builds reject cleartext traffic and hide account creation; set `ZORO_API_BASE_URL` to the deployed HTTPS endpoint before creating a release build. The release APK/AAB must be signed with an upload key; keep the keystore and passwords outside the repository.

## Security and current limits

- Access and refresh tokens are encrypted using AES-GCM with a key held in Android Keystore.
- Development builds call the development registration endpoint. Production creates the single owner account through a secure one-time backend job, then allows only that owner to sign in. Email verification/recovery, push registration, and call history are not implemented.
- Never ship the emulator URL or development backend as a production configuration.

