# Дневник настроения — Android

Веб-прототип из `../mood-diary-pc/index.html` уже скопирован сюда как `index.html`.
Этот же файл заворачивается в нативное Android-приложение через Capacitor.

## Почему так
- Один код для ПК (браузер) и Android (WebView).
- Данные пока в localStorage. Для релиза заменить на SQLite (@capacitor/preferences или @capacitor-community/sqlite).

## Как собрать APK локально (нужны Node 20+ и Android Studio)
```powershell
npm i -g @capacitor/cli
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap add android
npx cap sync
# открыть android/ в Android Studio -> Build -> Build APK
```

## Как выложить APK на GitHub (рекомендую)
1. Залить репозиторий на GitHub.
2. Добавить workflow `.github/workflows/android.yml` (пример ниже) — он соберёт debug-APK в облаке при каждом пуше.
3. APK забирать в `Actions -> Artifacts`, а релизный — прикрепить в `Releases`.
4. Для раздачи людям подписать release-ключом (хранить в GitHub Secrets).

Debug-APK ставится на телефон с разрешением "установка из неизвестных источников".
На iOS этот путь не работает — там нужен App Store / TestFlight.

## Пример workflow (.github/workflows/android.yml)
```yaml
name: android-apk
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - run: npm i -g @capacitor/cli && npm install @capacitor/core @capacitor/cli @capacitor/android
      - run: npx cap add android; npx cap sync
        working-directory: mood-diary-android
      - run: ./gradlew assembleDebug
        working-directory: mood-diary-android/android
      - uses: actions/upload-artifact@v4
        with: { name: app-debug, path: mood-diary-android/android/app/build/outputs/apk/debug/app-debug.apk }
```
