# Google Cloud deployment (private personal instance)

This guide prepares ZORO for Cloud Run in Mumbai. It is not an instruction to create paid resources without checking the estimated bill. The owner needs a Google Cloud project, billing, and budget alerts first. The current workstation has no `gcloud` login; Google Cloud Shell can run these commands after the repository is pushed.

## Resources

- Cloud Run service `zoro-api`, region `asia-south1`, minimum one warm instance, maximum two instances, request timeout 3600 seconds.
- Cloud SQL for PostgreSQL in `asia-south1`, connected to Cloud Run through the Cloud SQL connector socket.
- Artifact Registry repository `zoro` and a dedicated runtime service account with Cloud SQL Client plus access only to the secrets it needs.
- Secret Manager entries for `zoro-database-url` and `zoro-jwt-secret` before the first backend deployment. The owner email is a normal environment setting. Do not store secrets in the Android project or Git.
- Separate, temporary `zoro-bootstrap-password` secret for the one-off owner create/reset job. Delete or disable its active version after the job completes.

Cloud Run must allow unauthenticated requests at the platform edge so Exotel can open the media WebSocket. The API protects owner data with bearer authentication; the Exotel media route separately requires the configured Exotel Basic Authentication. Health and readiness are public. Production API documentation is disabled.

## Deploy order

1. Create a Cloud project, enable billing, and set a budget alert. Review Cloud Run, Cloud SQL, and storage estimates first. Do not enable live calls yet.
2. Create the Cloud SQL PostgreSQL instance, database, and least-privilege database user in Mumbai. Create Secret Manager entries for the full SQLAlchemy URL and a randomly generated JWT secret (at least 32 characters). URL-encode special characters in the database password. The URL uses the Cloud SQL socket, for example `postgresql+asyncpg://USER:PASSWORD@/DATABASE?host=/cloudsql/PROJECT:asia-south1:INSTANCE`.
3. Build and upload the image from the repository root:

   ```bash
   PROJECT_ID="your-project-id"
   REGION="asia-south1"
   IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/zoro/backend:initial"
   gcloud config set project "$PROJECT_ID"
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com
   gcloud artifacts repositories create zoro --repository-format=docker --location="$REGION"
   gcloud builds submit backend --tag "$IMAGE"
   ```

4. Create the runtime service account and grant it Cloud SQL Client and Secret Manager Secret Accessor on only `zoro-database-url` and `zoro-jwt-secret`. The account used to deploy also needs permission to act as this service account.
5. Run a one-off Cloud Run Job using the built image and the command `alembic upgrade head`. Attach the Cloud SQL instance and provide production settings and the two required secrets to the job. Confirm the migration succeeds before creating the owner.
6. Run a second one-off Cloud Run Job using `python -m app.bootstrap_owner`, with production settings, the SQL/JWT secrets, `ZORO_OWNER_EMAIL`, and `ZORO_BOOTSTRAP_PASSWORD` sourced from Secret Manager. To reset the owner later, additionally set `ZORO_BOOTSTRAP_RESET=true`; this revokes all owner sessions.
7. Deploy the API image to Cloud Run with `--region=asia-south1`, `--port=8080`, `--min=1`, `--max=2`, `--timeout=3600`, the Cloud SQL attachment, the runtime service account, and `--allow-unauthenticated`. Set `ZORO_APP_ENV=production`, `ZORO_OWNER_EMAIL`, and `ZORO_LIVE_CALLS_ENABLED=false`; inject the database URL and JWT secret from Secret Manager. Keep Exotel and AI secrets unset until those accounts and consent flow are ready.
8. Open `/health` and `/ready` on the deployed HTTPS service. Sign in from the Android app after building a release pointed at that HTTPS base URL. Keep the call feature off until provider setup and the controlled-call checks in `docs/DEPLOYMENT_PLAN.md` are complete.

The cloud migration job needs the same SQL database URL as the service and runs before traffic receives requests. Do not put the temporary bootstrap password into the running Cloud Run service.

## Android private release

The Android app is the frontend; the backend remains independently available on Cloud Run while the phone or computer is offline. Build an Android App Bundle using target API 36 and the HTTPS Cloud Run base URL. Sign it using the owner's upload key, then use Google Play internal testing for private updates if Play Console is ready. The release build hides public account creation because the owner account is provisioned in the backend.
