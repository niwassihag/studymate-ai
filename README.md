# StudyMate AI

Mobile study planner with a warm cream and orange design, tasks, focus timer, mock results and local persistence.

[Download Android APK](../../raw/refs/heads/main/StudyMate-AI.apk)

## Android

Download StudyMate-AI.apk and open it on Android 6.0 or later. See [installation instructions](INSTALL-StudyMate.md).

The APK launched successfully on a Pixel 7 Android 13 online emulator. Testbook login and end-to-end result capture are not yet emulator-verified.

## Testbook capture

In the Android app, open Platforms > Testbook, sign in, open an attempted test and select Analysis. Supported result pages supply score and accuracy automatically. Duplicate attempts update the existing record. Available sections below 70% accuracy become focus areas. Dates are import dates.

This is experimental page-based capture, not an official provider integration or background sync. Website changes and login restrictions can break capture. Oliveboard and custom platforms remain manual. Ordinary links and the PWA cannot read third-party results. Authorized provider integrations are needed for reliable automatic background detection.

## Run the web app

Run `node server.cjs`, then open http://localhost:8080. For phone PWA installation, host these files on HTTPS. The planner works offline after first load. No external AI service is used: suggestions are calculated locally from recent results and weak areas.

## Build Android APK

Use Python 3 with `pip install -r requirements.txt`, then run `python build_android.py`. The APK is written to `dist/StudyMate-AI.apk`.

The builder generates Android bytecode/resources directly and signs the APK. It creates a private signing identity under work/ on the first build. Keep that identity private and backed up for your own future updates. The signing key used for the downloadable APK is deliberately not published; your build has a different signature and cannot update that installed APK in place.

## Privacy

Study records remain on the device. Backups contain your records. Testbook manages its login session inside the Android WebView. No personal records, login sessions, credentials or private signing keys are included in this repository. Clear-data/uninstall removes local records; export a backup first.
