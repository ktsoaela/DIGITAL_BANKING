# KHOEBO mobile client

Flutter starter for the KHOEBO DIGITAL BANKING mobile experience.

## Run

```powershell
cd KHOEBO_DIGITAL_BANKING/mobile
flutter pub get
flutter run --dart-define=BANKA_API_URL=http://10.0.2.2:8001
```

The Android emulator uses `10.0.2.2` to reach the host machine. A physical device needs the host machine's LAN address. The client is intentionally API-ready and should add secure token storage, biometric platform integration, certificate pinning, and device binding before production use.
