# تحليل تفصيلي لـ AndroidManifest.xml — AbbasiyCashiers

**اسم الحزمة:** `com.egy.webpaymentapp`
**اسم العرض:** `ECAS WEB`
**versionCode:** 18 | **versionName:** `Ecas v18.4`
**minSdkVersion:** 19 (Android 4.4 KitKat) | **targetSdkVersion:** 32 (Android 12L)
**compileSdkVersion:** 32

---

## 1. الأذونات المطلوبة (Permissions)

### الأذونات الحساسة جداً 🔴

| الإذن | الخطورة | التحليل |
|------|---------|---------|
| `READ_PHONE_STATE` | **عالية** | للوصول إلى IMEI/رقم الهاتف. يُستخدم كـ device fingerprint (راجع `MediaSessionCompat.D()`) |
| `ACCESS_FINE_LOCATION` | **عالية** | موقع GPS دقيق - يُرسل عبر `saveCustLocation` |
| `ACCESS_COARSE_LOCATION` | **عالية** | موقع تقريبي عبر الشبكة |
| `CAMERA` / `CAMERA2` | **عالية** | لالتقاط صور العدادات (راجع OprationsActivity سطر 312) |
| `READ_EXTERNAL_STORAGE` | **متوسطة** | الوصول للملفات الخارجية |
| `WRITE_EXTERNAL_STORAGE` | **متوسطة** | الكتابة على التخزين الخارجي |
| `MANAGE_EXTERNAL_STORAGE` | **عالية جداً** | إذن "All Files Access" - مفرط للغاية (انتهاك Google Play policy) |
| `REQUEST_INSTALL_PACKAGES` | **عالية جداً** | تثبيت تطبيقات أخرى! - **مشبوه** في تطبيق POS |
| `DOWNLOAD_WITHOUT_NOTIFICATION` | **متوسطة** | تنزيل دون إشعار المستخدم |
| `RECEIVE_BOOT_COMPLETED` | **متوسطة** | تشغيل تلقائي عند الإقلاع |
| `ACCESS_SUPERUSER` | **متوسطة** | إذن قديم/مهجور، قد يكون من أجل الجذر |
| `CALL_PHONE` | **متوسطة** | إجراء مكالمات (للتواصل مع العملاء) |

### الأذونات العادية ⚪
- `INTERNET`, `ACCESS_NETWORK_STATE`, `ACCESS_WIFI_STATE`, `FOREGROUND_SERVICE`
- Bluetooth (LEGACY + new): `BLUETOOTH`, `BLUETOOTH_ADMIN`, `BLUETOOTH_SCAN`, `BLUETOOTH_CONNECT`, `BLUETOOTH_ADVERTISE`, `BLUETOOTH_PRIVILEGED` (لتوصيل الطابعات والأجهزة الطرفية)

### أذونات غير صحيحة / مشبوهة ⚠️
ثلاثة أذونات بأسماء غير صحيحة (تبدأ بـ `Manifest.permission.` بدلاً من `android.permission.`):
```xml
<uses-permission android:name="Manifest.permission.READ_EXTERNAL_STORAGE"/>
<uses-permission android:name="Manifest.permission.WRITE_EXTERNAL_STORAGE"/>
<uses-permission android:name="Manifest.permission.READ_PRIVILEGED_PHONE_STATE"/>
```
**التفسير:** خطأ من المطور (نسخ Java syntax إلى XML). هذه الأذونات لن تعمل، لكنها تكشف **محاولة طلب صلاحية مميزة** `READ_PRIVILEGED_PHONE_STATE` (Signature-level permission).

أذونات إضافية مهجورة في Android الحديث:
- `READ_INTERNAL_STORAGE` / `WRITE_INTERNAL_STORAGE` - غير موجودة رسمياً
- `ACCESS_LOCATION_EXTRA_COMMANDS` - معمل قديم

---

## 2. مكونات التطبيق

### Activities (الشاشات)

| الـ Activity | exported | الـ Intent Filter | الملاحظات |
|--------------|----------|-------------------|-----------|
| **LoginActivity** ⭐ | **true** | MAIN+LAUNCHER, VIEW (deeplink) | نقطة الدخول الرئيسية + يقبل deeplinks من `https://ecas.web.link` |
| MainActivity | false | — | الشاشة الرئيسية بعد تسجيل الدخول |
| OprationsActivity | false | — | شاشة عمليات الدفع/القراءة (~624 سطر) |
| WebviewActivity | false | — | عارض WebView (تقارير + JS-bridge) |
| ChangePassActivity | false | — | تغيير كلمة المرور |
| Setting_Printer_Activity | false | — | إعدادات الطابعة |
| BixlonPrinterManger.ScanActivity | false | — | مسح طابعات Bixolon |
| com.karumi.dexter.DexterActivity | (مكتبة) | — | إدارة الأذونات (Dexter library) |
| com.google.android.gms.common.api.GoogleApiActivity | false | — | Google Play Services |

### Content Providers
```xml
<provider 
    android:authorities="com.egy.webpaymentapp" 
    android:exported="false" 
    android:grantUriPermissions="true" 
    android:name="androidx.core.content.FileProvider">
    <meta-data android:name="android.support.FILE_PROVIDER_PATHS" 
               android:resource="@xml/file_provider_path"/>
</provider>
```
**التحليل:** FileProvider قياسي لمشاركة الملفات (صور العدادات بعد التقاطها) — مُعطل التصدير (آمن).

### Services / Broadcast Receivers
- **لا توجد Services مُعرَّفة** في الـ manifest
- **لا توجد BroadcastReceivers مُعرَّفة** في الـ manifest
- ملاحظة: إذن `RECEIVE_BOOT_COMPLETED` موجود لكن لا يوجد receiver يستخدمه (إذن غير مستخدم)

---

## 3. نقطة الدخول الرئيسية (Main Entry Point)

### Intent Filter #1 - Launcher Default
```xml
<activity android:exported="true" 
          android:name="com.egy.webpaymentapp.Screens.LoginActivity">
    <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
    </intent-filter>
</activity>
```
عادي — هذه نقطة الدخول من قائمة التطبيقات.

### Intent Filter #2 - Deeplink HTTPS 🔴
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW"/>
    <category android:name="android.intent.category.DEFAULT"/>
    <category android:name="android.intent.category.BROWSABLE"/>
    <data android:host="ecas.web.link" android:scheme="https"/>
</intent-filter>
```

**سطح الهجوم:**
- أي صفحة ويب تستطيع فتح هذا التطبيق
- المعامل `?ip=` يُستخدم في `LoginActivity.A()` لتغيير عنوان الخادم
- **لا يوجد `android:autoVerify="true"`** → معالج deeplink مشترك (يمكن لتطبيقات ضارة المنافسة عليه)
- النطاق `ecas.web.link` لا يحمل ملف `.well-known/assetlinks.json` بشكل موثوق

---

## 4. إعدادات الأمان للتطبيق (Application Security Flags)

```xml
<application 
    android:allowBackup="false"                  ✅ جيد
    android:supportsRtl="true"                   ⚪ عادي
    android:requestLegacyExternalStorage="true"  ⚠️ يطلب وضع scoped storage القديم
    android:usesCleartextTraffic="true"          🔴 خطير
    android:name="androidx.multidex.MultiDexApplication">
```

### تحليل العلامات الحرجة:

| العلامة | القيمة | التقييم |
|--------|--------|---------|
| `allowBackup` | `false` | ✅ جيد - يمنع نسخ adb backup |
| `usesCleartextTraffic` | `true` | 🔴 **خطير** - يسمح HTTP بدون TLS |
| `requestLegacyExternalStorage` | `true` | ⚠️ - يتجنب scoped storage |
| `debuggable` | (غير موجود) | ✅ افتراضياً false - جيد |
| `networkSecurityConfig` | (غير موجود) | 🔴 لا يوجد تكوين أمان شبكي |
| `android:exported` للأنشطة الداخلية | `false` افتراضياً | ✅ جيد |

### نقطة مهمة:
عدم وجود `networkSecurityConfig` يعني أن التطبيق:
1. يسمح بـ cleartext traffic (HTTP)
2. لا يُجبر استخدام شهادات نظام التشغيل فقط
3. لا يُفعّل Certificate Pinning نظامياً

---

## 5. ملخص نتائج تحليل الـ Manifest

### نقاط القوة ✅
- `allowBackup="false"`
- معظم الأنشطة `exported="false"` افتراضياً
- لا توجد BroadcastReceivers مُصدَّرة
- استخدام FileProvider بدلاً من `file://` URIs

### نقاط الضعف 🔴
1. **`usesCleartextTraffic="true"`** - يسمح بحركة HTTP غير مشفرة
2. **لا يوجد `networkSecurityConfig`** - لا قيود على الشهادات
3. **deeplink بدون `autoVerify`** على `ecas.web.link`
4. **أذونات مفرطة**: `MANAGE_EXTERNAL_STORAGE`, `REQUEST_INSTALL_PACKAGES`, `DOWNLOAD_WITHOUT_NOTIFICATION`, `ACCESS_SUPERUSER`
5. **3 أذونات بأسماء غير صحيحة** (خطأ Manifest.permission.XXX)
6. **`requestLegacyExternalStorage="true"`** - يتجاوز Scoped Storage في Android 10+

### توصيات الإصلاح (Recommendations)
1. إزالة `usesCleartextTraffic` أو ضبطه على `false`
2. إضافة `networkSecurityConfig` يفرض TLS فقط مع pinning
3. تصحيح أسماء الأذونات (إزالة `Manifest.permission.` prefix)
4. إزالة `REQUEST_INSTALL_PACKAGES` و `DOWNLOAD_WITHOUT_NOTIFICATION` إن لم تكن ضرورية
5. تطبيق `autoVerify="true"` على intent filter للـ deeplink + إضافة assetlinks.json
6. التحول لأذونات runtime الدقيقة بدلاً من `MANAGE_EXTERNAL_STORAGE`
