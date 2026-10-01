# Дневник настроения — Android

Веб-приложение из `../mood-diary-pc/index.html` завернуто в нативное
Android-приложение через Capacitor (WebView). Один код для ПК (браузер)
и телефона, поведение на телефоне проверено на устройстве.

## Структура

- `www/index.html` — копия `../mood-diary-pc/index.html`, именно она
  попадает в APK. Источник правды — pc-файл: правится он, затем копируется
  сюда и выполняется `npx cap sync android`.
- `capacitor.config.json` — `appId: ru.mooddiary`, `webDir: www`.
- `android/` — сгенерированный нативный проект (`npx cap add android`),
  коммитится в репозиторий, кроме `build/` и `local.properties`.
- `mood-diary.jks` + `keystore.properties` — ключ подписи релиза и пароли.
  В репозиторий НЕ попадают (см. корневой `.gitignore`): иначе любой смог
  бы выпускать обновления от вашего имени. Храните копию ключа отдельно.

## Отличия телефонной версии от браузерной

В WebView нет части браузерных API, поэтому в приложении (`window.Capacitor`):

- кнопки JSON/CSV пишут файл во внутренний кэш и открывают системный диалог
  «Поделиться» (плагины `@capacitor/filesystem`, `@capacitor/share`);
- кнопка «PDF для психолога» вместо `window.print()` отправляет текстовую
  сводку отчёта через «Поделиться»;
- блок напоминаний скрыт: WebView не поддерживает Notification API,
  кнопки были бы мёртвыми. Напоминания пока работают только в браузере
  при открытой вкладке.

В браузере поведение не меняется: там этот код не выполняется.

## Сборка

Нужны Node 20+, JDK 21 и Android SDK (платформа 36). Путь к SDK — в
`android/local.properties` (`sdk.dir=...`), файл локальный.

```powershell
# 1. Обновить витрину из исходника и синхронизировать
Copy-Item ..\mood-diary-pc\index.html .\www\index.html -Force
npx cap sync android

# 2. Debug APK для проверки на телефоне
$env:JAVA_HOME="<путь к JDK 21>"
.\android\gradlew.bat -p android :app:assembleDebug
# -> android/app/build/outputs/apk/debug/app-debug.apk

# 3. Подписанный релиз (нужны mood-diary.jks и keystore.properties рядом)
.\android\gradlew.bat -p android :app:assembleRelease
# -> android/app/build/outputs/apk/release/app-release.apk
```

APK подписан схемами v1+v2: часть прошивок не принимает пакеты только
с подписью v2.

## Совместимость

Android 7.0 и выше (minSdk 24 — минимум Capacitor 8), targetSdk 35.
Google Play Services не нужны. Проверено на TECNO BF7 (Android 12).
