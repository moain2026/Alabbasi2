# 01.2 — مخطط البنية المعمارية (Architecture Diagram)

> هذا المخطط هو **مرجع الطريق** لأي مطوّر يدخل المشروع. يوضح: من يتحدث مع من، كيف، وبأي بروتوكول.

---

## المخطط الأعلى مستوى (High-Level)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          AbbasiyCashiers — Android APK                       │
│                            com.egy.webpaymentapp                             │
│                                                                              │
│  ┌───────────────────────────────────┐    ┌────────────────────────────────┐ │
│  │   Native Android Shell (Java)     │    │  Embedded Web Assets (HTML/JS) │ │
│  │   ─────────────────────────────   │    │  ─────────────────────────────  │ │
│  │   • LoginActivity                 │    │  assets/myweb/                  │ │
│  │   • MainActivity   (7 buttons)    │    │  ├── paymentList.html           │ │
│  │   • OprationsActivity (3 modes)   │◀──▶│  ├── readinglist.html           │ │
│  │   • ChangePassActivity            │    │  ├── vReport.html               │ │
│  │   • WebviewActivity ◀────────────┐│    │  ├── default_error_page.html    │ │
│  │   • Setting_Printer_Activity     ││    │  ├── js/                        │ │
│  │   • ScanActivity (Bluetooth)     ││    │  └── css/                       │ │
│  │                                  ││    │                                  │ │
│  │   Helpers:                       ││    │  Bootstrap 4.5.3 + jQuery 3.0.0 │ │
│  │   • c.b.a.c (SharedPrefs)        ││    │                                  │ │
│  │   • c.b.a.f.c (HTTP via Volley)  ││    └────────────────────────────────┘ │
│  │   • c.b.a.f.b (Auth helpers)     ││             ▲                          │
│  │   • MediaSessionCompat (crypto!) ││             │ JavascriptInterface     │
│  │                                  ││             │ "mobile" exposes 6      │
│  └───────────────┬──────────────────┘│             │ @JavascriptInterface    │
│                  │                   │             │ methods                  │
│                  │                   │             │                          │
│  ┌───────────────┴──────────────────▼┴───────────────────────────────────┐   │
│  │            Native Libraries (.so) — armeabi-v7a, x86, x86_64          │   │
│  │  • libJoinImage.so      (image join — probably Bluetooth scanner)     │   │
│  │  • libbxlpdf.so         (Bixolon PDF generator)                       │   │
│  │  • libcomm_serial_port.so (Serial port for printer)                   │   │
│  │  • libopencv_java.so    (OpenCV — likely unused but linked)           │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────┬──────────────────────────────────────────────────────────────┬────┘
           │                                                              │
           │ HTTPS (TLS, self-signed cert, validation DISABLED)          │ Bluetooth
           │ Volley HTTP client, JSON, Bearer auth                       │ Classic
           ▼                                                              ▼
┌────────────────────────────────────────┐               ┌───────────────────────┐
│  Backend Server                        │               │  Bixolon POS Printer  │
│  https://abbasiy.yedns.org:8057/payment│               │  (thermal Bluetooth)  │
│  Likely ASP.NET Web API 2 (/api/...)   │               │  via JPOS framework   │
│  Self-signed cert (Yahya Aljamal,      │               │  + d.a.a.* helpers    │
│   United Power, Yemen)                 │               └───────────────────────┘
└────────────────────────────────────────┘
```

---

## التدفقات الرئيسية (Main Flows)

### تدفق 1: تسجيل دخول مستخدم جديد

```
المستخدم                LoginActivity        MediaSessionCompat       Backend
   │                          │                      │                    │
   │ يدخل (فرع + اسم + كلمة) │                      │                    │
   ├─────────────────────────▶│                      │                    │
   │                          │ هل APP_PK_KEY فارغ؟  │                    │
   │                          ├─────────────────────▶│                    │
   │                          │                      │                    │
   │                          │   getAppPK (no auth) │                    │
   │                          ├──────────────────────┼───────────────────▶│
   │                          │                      │                    │ يبني RSA pair
   │                          │     {apppk: "n&e"}   │                    │ ويرسل (n, e)
   │                          │◀─────────────────────┼────────────────────┤
   │                          │                      │                    │
   │                          │ يخزّن في APP_PK_KEY  │                    │
   │                          │                      │                    │
   │                          │ يطلب RSA-encrypt     │                    │
   │                          ├─────────────────────▶│ a(pk, password)    │
   │                          │ ciphertext_b64       │ a(pk, deviceId)    │
   │                          │◀─────────────────────│                    │
   │                          │                      │                    │
   │                          │  POST /api/Users/Login                    │
   │                          │  {Username, Password=cipher, mob_srl=cipher, user_branch}
   │                          ├──────────────────────┼───────────────────▶│
   │                          │                      │                    │ RSA-decrypt
   │                          │                      │                    │ يتحقّق
   │                          │ {user, areaList}     │                    │
   │                          │◀─────────────────────┼────────────────────┤
   │                          │                      │                    │
   │                          │ يخزّن في APP_USER_KEY│                    │
   │                          │ يخزّن APP_AREADATALIST_KEY                │
   │                          │                      │                    │
   │ ينتقل إلى MainActivity   │                      │                    │
   │◀─────────────────────────┤                      │                    │
```

---

### تدفق 2: حفظ دفعة (Save Payment)

```
المستخدم        OperationsActivity (B=1)      Backend           Bixolon Printer
   │                  │                          │                     │
   │ يدخل رقم المشترك│                          │                     │
   ├─────────────────▶│                          │                     │
   │                  │ POST /api/Payment/GetCustomersData              │
   │                  ├──────────────────────────▶│                     │
   │                  │     {customersList: [{c_no, c_name, c_bal, ...}]}│
   │                  │◀─────────────────────────┤                     │
   │                  │                          │                     │
   │                  │ يعرض بيانات المشترك      │                     │
   │ يدخل المبلغ      │                          │                     │
   ├─────────────────▶│                          │                     │
   │                  │ يحسب الرصيد الجديد       │                     │
   │ يضغط حفظ         │                          │                     │
   ├─────────────────▶│                          │                     │
   │                  │ يعرض حوار تأكيد          │                     │
   │ نعم              │                          │                     │
   ├─────────────────▶│                          │                     │
   │                  │ POST /api/Payment/saveBillRequest               │
   │                  │ {payinfo:{c_no, c_name, c_bal, v_amt, c_note,   │
   │                  │           user_gps_loc}, user, user_no, user_branch}
   │                  ├──────────────────────────▶│                     │
   │                  │ {GEN_API_ERR_NO:0, payinfo:{v_no, v_date}}      │
   │                  │◀─────────────────────────┤                     │
   │                  │                          │                     │
   │                  │ يطبع الإيصال (إن متصل)   │                     │
   │                  ├──────────────────────────┼────────────────────▶│
   │                  │                          │                     │
```

---

### تدفق 3: عرض قائمة المدفوعات (WebView)

```
المستخدم → MainActivity → WebviewActivity ( OP_TYP=1, page=file:///.../paymentList.html )
                                  │
                                  ├─ يحمّل WebView على paymentList.html
                                  ├─ يحقن JavascriptInterface "mobile"
                                  │
              ┌───────────────────┘
              ▼
        paymentList.html
              │
              ├─ يستدعي onload: loadPaymentsData('')
              │       │
              │       └─→ window.mobile.GetPaymentsRequest('')
              │                          │
              │                          └─→ WebviewActivity.v(string="", activity)
              │                                       │
              │                                       └─→ POST /api/Payment/GetPaymentsReportData
              │                                                       │
              │                                                       └─→ Backend
              │                                                              │
              │              ┌───────────────────────────────────────────────┘
              │              ▼
              │       {GEN_API_ERR_NO:0, payList:[{c_no, c_name, c_bal, v_amt, v_date, v_no, ...}]}
              │              │
              │              └─→ WebView.loadUrl("javascript:showpayList('"+ JSON +"');")
              │                                       │
              │                                       └─→ payment.js receives, renders <table>
              │
              ├─ المستخدم يبحث (search input)
              │       │
              │       └─→ serachInTable() — JS-only filter, no API
              │
              ├─ المستخدم يضغط على سطر
              │       │
              │       ├─→ localStorage.setItem("report", JSON.stringify(record))
              │       └─→ window.location.replace('./vReport.html')
              │
              └─ vReport.html
                       │
                       ├─→ getPayReport() from localStorage
                       ├─→ يرسم الإيصال HTML
                       │
                       └─ المستخدم يضغط "طباعة"
                                │
                                ├─→ window.mobile.printPdfReport(JSON)
                                │       │
                                │       └─→ WebviewActivity calls Android Print
                                │
                                └─→ window.mobile.sharexPdfReport(JSON)
                                        │
                                        └─→ يفتح Share Sheet (WhatsApp, …)
```

---

## طبقات البنية (Layers)

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 1 — Presentation                                       │
│  • Activities (Java) — 6 شاشات                                │
│  • Layouts XML (~131 ملف)                                     │
│  • WebView pages (HTML+JS+CSS)                                │
│  • Bootstrap 4.5.3 + jQuery 3.0.0                             │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│  Layer 2 — Bridge / Glue                                      │
│  • i.java (JavascriptInterface "mobile")                      │
│  • WebChromeClient (Alert/Confirm/Prompt handlers)            │
│  • WebViewClient (h.java — SSL bypass, error page)            │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│  Layer 3 — Business Logic                                     │
│  • Login/Logout state machine                                 │
│  • Payment/Reading workflow (OperationsActivity 3 modes)      │
│  • Deeplink IP override                                       │
│  • Magic backdoor (1/1/1)                                     │
│  • Currency calculation, balance update                       │
│  • Arabic number-to-words (in JS)                             │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│  Layer 4 — Data / Network                                     │
│  • c.b.a.f.c (Volley HTTP wrapper)                            │
│  • c.b.a.f.a (custom Volley Request<T> with Gson)             │
│  • c.b.a.f.b (Auth: Login/ChangePass/GetAppPK)                │
│  • c.b.a.f.d (empty X509TrustManager — DANGER)                │
│  • Gson serialization                                          │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│  Layer 5 — Storage                                            │
│  • c.b.a.c (SharedPreferences wrapper, file: USER_DETAILS_PREF)│
│  • Keys: APP_USER_KEY, APP_PK_KEY, APP_SERVER_IP_KEY,         │
│          APP_SERVER_CER_KEY, APP_USER_LOC_KEY,                │
│          APP_AREADATALIST_KEY                                  │
│  • PreferenceManager (for printer settings xml)               │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│  Layer 6 — Crypto                                             │
│  • MediaSessionCompat.a()  — RSA encrypt (n&e from server)    │
│  • MediaSessionCompat.r()  — DESede decrypt (deeplink ip=)    │
│  • MediaSessionCompat.s()  — DESede encrypt (dead in app)     │
│  • MediaSessionCompat.B()  — HMAC-SHA1+SHA-256 (DEAD CODE)    │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│  Layer 7 — Hardware (.so + JPOS)                              │
│  • libbxlpdf.so      → Bixolon PDF                            │
│  • libcomm_serial_port.so → Serial port                       │
│  • libJoinImage.so   → Image stitching                        │
│  • libopencv_java.so → OpenCV (linked, possibly unused)       │
│  • d.a.a.a/b/c (Bluetooth manager helpers)                    │
└──────────────────────────────────────────────────────────────┘
```

---

## شجرة الحزم Java (Package Tree)

```
com.egy.webpaymentapp/
├── Screens/
│   ├── LoginActivity.java
│   ├── MainActivity.java
│   ├── OprationsActivity.java
│   ├── ChangePassActivity.java
│   ├── Setting_Printer_Activity.java
│   ├── a.java .. z.java, a0.java .. h0.java (≈ 50 anonymous helpers)
│   └── web/
│       ├── WebviewActivity.java          (461 lines)
│       ├── i.java                        (JavascriptInterface "mobile")
│       ├── h.java                        (WebViewClient, SSL bypass)
│       ├── j.java                        (auxiliary WebView for print)
│       ├── p.java (interface)
│       └── g/k/l/m/n/o.java              (small runnables)
│
├── BixlonPrinterManger/
│   ├── ScanActivity.java                 (Bluetooth scan UI)
│   ├── ScanActivity_ViewBinding.java     (ButterKnife generated)
│   ├── a.java                            (printer dialog helper, 295 lines)
│   └── b.java                            (printer connect helper, 156 lines)
│
└── webapi/
    └── models/
        ├── User.java                     (167 lines, 21 @SerializedName)
        ├── Payinfo.java                  (91 lines, 15 fields)
        ├── UserRoles.java                (5 lines, EMPTY!)
        ├── a.java                        (customer info — c_no, c_name, c_bal, ...)
        ├── b.java                        (envelope response — GEN_API_ERR_NO, ...)
        ├── c.java                        (payment list entry)
        └── d.java                        (universal request envelope)

c/b/a/                                    (Utilities root — letter-obfuscated)
├── c.java                                (SharedPreferences wrapper)
├── d.java                                (UI helpers: showAlert, isNetworkAvailable)
├── b/                                    (Bluetooth helpers area)
│   └── d.java                            (CountDownTimer/Location handler)
├── a/                                    (Models for adapters)
│   ├── a.java (interface OnItemClick<T>)
│   ├── b.java (RecyclerView adapter)
│   └── c.java (generic item: f1828a=label, f1829b=value, ...)
└── f/                                    (Network/Auth area)
    ├── c.java                            (Volley wrapper, 262 lines, BaseURL constant)
    ├── b.java                            (Login/ChangePass/getAppPK calls)
    ├── a.java                            (custom Volley Request<T>)
    └── d.java                            (empty X509TrustManager — VULNERABLE)

android.support.v4.media.session.MediaSessionCompat
                                          (756 lines, but ~530 are GENUINE Android compat;
                                           lines 225-756 contain INJECTED crypto helpers:
                                           A(), B(), C(), D(), a()..s() — RSA/DESede/HMAC)

d.a.a.*                                   (Bluetooth printer framework — vendor lib)
jpos.*                                    (POS specifications — Bixolon dependency)
mf.org.apache.*                           (Embedded Apache XML libraries)
c.a.b.*                                   (Volley — Google's HTTP library)
c.c.b.*                                   (Gson — Google's JSON library)
butterknife.*                             (Annotation-based view binding)
b.h.* / b.f.* / b.b.*                     (AndroidX — obfuscated)
```

---

## التبعيات الخارجية الرئيسية

| المكتبة | الإصدار التقريبي | الاستخدام |
|---|---|---|
| **Volley** (`c.a.b.*`) | ~1.2.x | كل HTTP في التطبيق |
| **Gson** (`c.c.b.*`) | ~2.8.x | JSON serialization |
| **ButterKnife** | ~10.x | View binding في `ScanActivity` |
| **Bixolon SDK** (`jpos.*`, `com.bxl.*`) | unknown | الطابعة |
| **OpenCV** | unknown | linked but largely unused |
| **Dexter** (`com.karumi.dexter`) | ~6.x | runtime permissions UX |
| **Google Play Services** | base, basement, location, maps, places | GPS فقط (لا maps فعلياً) |
| **AndroidX** (multidex, fragment, appcompat) | ~1.2.x | UI framework |
| **Bootstrap** (في WebView) | 4.5.3 | CSS framework |
| **jQuery** (في WebView) | 3.0.0 | JS framework |

---

## ملاحظات معمارية مهمة

1. **التطبيق ليس MVVM/MVP/MVI — هو "Activity-as-Controller"**
   كل شيء داخل Activity مباشرة. لا ViewModels، لا LiveData، لا StateFlow.

2. **لا Repository Pattern**
   شاشات تستدعي `c.b.a.f.c.b()` مباشرة بدون abstraction.

3. **لا Dependency Injection**
   كل dependency تُبنى يدوياً (`new c.b.a.f.c(activity)`).

4. **لا Caching layer**
   كل request للسيرفر مباشرةً، بدون Room/SQLite/WatermelonDB.

5. **State بدائي**
   فقط SharedPreferences لـ 6 keys رئيسية، بدون state management library.

6. **Bridge مشترك بين WebView و Native**
   `localStorage` في WebView يُستخدم لتمرير payload من قائمة إلى صفحة تفاصيل.

---

**التالي:** [`03_app_lifecycle.md`](03_app_lifecycle.md) — دورة حياة التطبيق من Splash لـ Logout.
