# 01.3 — دورة حياة التطبيق (App Lifecycle)

> من فتح المستخدم للتطبيق أول مرة، حتى الخروج. كل خطوة موثقة بـ Activity/Method المسؤولة.

---

## المسار العام (Happy Path)

```
1. تثبيت → اللانشر (Launcher)
              │
2. النقر على أيقونة Ecas
              │
              ▼
3. LoginActivity.onCreate()
              │
              ├─ يطلب الصلاحيات (BLUETOOTH, LOCATION, STORAGE, CAMERA, ...)
              │  عبر MediaSessionCompat.z(this)
              │
              ├─ if (Android >= 30 && !isExternalStorageManager)
              │   → يعرض Snackbar مع زر "Settings"
              │
              ├─ يضع نص الإصدار "Ver Ecas v18.4"
              │
              ├─ يحمّل المستخدم السابق إن وجد:
              │   user = MediaSessionCompat.C(this)  // من APP_USER_KEY
              │   editText.setText(user.f())   // user_no
              │   editText.setText(user.n())   // user_branch
              │
              ├─ يعالج deeplink (إن وجد):
              │   if (intent.data != null) {
              │     ip = decryptDeeplinkParam(intent)
              │     SharedPrefs["APP_SERVER_IP_KEY"] = "https://" + ip
              │   }
              │
              ├─ يحدّث BaseURL:
              │   if (APP_SERVER_IP_KEY != null)
              │     c.b.a.f.c.f1899b = APP_SERVER_IP_KEY
              │   else
              │     c.b.a.f.c.f1899b = "https://abbasiy.yedns.org:8057/payment"
              │
              └─ يطلب RSA Public Key مباشرة (silent, no UI):
                  POST /api/Users/getAppPK (no auth)
                  → APP_PK_KEY = response.apppk
              │
4. المستخدم يكتب (branch, username, password)
              │
              ├─ إذا (branch=1 AND username=1 AND password=1):
              │   → ينتقل لـ Settings (android.settings.APPLICATION_DETAILS_SETTINGS)
              │   → BACKDOOR! لا يتم تسجيل دخول
              │
              ├─ إذا APP_PK_KEY فارغة:
              │   → يعيد طلب getAppPK ثم يحاول
              │
              └─ يستدعي c.b.a.f.b.c(activity, branch, username, password, callback):
                  password_enc = RSA_encrypt(APP_PK_KEY, password)
                  mob_srl_enc  = RSA_encrypt(APP_PK_KEY, deviceId)
                  POST /api/Users/Login {
                    Username: username,
                    user_branch: branch,
                    Password: password_enc,
                    mob_srl: mob_srl_enc
                  }
                  ↓
                  Response: {GEN_API_ERR_NO:0, user:{...}, AreaList:[...]}
                  ↓
                  if (err == 0) {
                    SharedPrefs["APP_USER_KEY"] = JSON(user)
                    SharedPrefs["APP_AREADATALIST_KEY"] = JSON(AreaList)
                    → MainActivity
                  } else {
                    showAlert(err_msg)
                  }
              │
              ▼
5. MainActivity.onCreate()
              │
              ├─ يقرأ user = APP_USER_KEY
              ├─ يعرض اسم المستخدم: txt_name.setText(user.o())  // Username
              │
              ├─ يربط 7 أزرار + ينظّم رؤيتها بناءً على الصلاحيات:
              │
              │   Button btnpayment      visible if user.Cshr_AddWebPay      == "1"
              │   Button btnpaymentList  visible if user.Cshr_AddWebPay      == "1"
              │   Button btnReadingList  visible if user.Cshr_AddWebRead     == "1"
              │   Button btn_add_reading visible if user.Cshr_AddWebRead     == "1"
              │   Button btn_cust_loc    visible if user.Cshr_AddWebCstUpDate== "1"
              │   Button btnUserReports  visible if user.Cshr_AddWOtherOpr   == "1"
              │   Button btnchangepass   always visible
              │
              │   Click handlers: h, i, j, k, l, m, n inner classes.
              │
              └─ يضبط ActionBar (لا منيو ولا back)
              │
              ▼
6. المستخدم ينقر زراً
              │
   ┌──────────┼─────────────────────────────────────────────────────────────────────┐
   │          │                                                                     │
   ▼          ▼                                                                     ▼
btnpayment  btnpaymentList                                                   btnchangepass
   │          │                                                                     │
   │          │  WebviewActivity                                                    ▼
   │          │  ─────────────────────                                  ChangePassActivity
   │          │  page = file:///android_asset/myweb/paymentList.html      │
   │          │  OP_TYP = 1                                              ├─ يدخل old/new
   │          │  → Loads HTML in WebView                                 ├─ يستدعي:
   │          │  → On load: window.mobile.GetPaymentsRequest('')         │   c.b.a.f.b.a(...)
   │          │  → WebView.loadUrl("javascript:showpayList(JSON);")      │   password_enc = RSA(...)
   │          │  → User clicks row → vReport.html                        │   POST /api/Users/changePasswordRequest
   │          │                                                          │   → success → updates user
   │          │                                                          │
   ▼          ▼                                                                     
OprationsActivity (OP_TYP=1 → Payment)                                              
   │
   ├─ يقرأ User من APP_USER_KEY
   ├─ يضبط UI حسب OP_TYP (1=Payment, 2=Reading, 3=Location)
   │
   ├─ المستخدم يدخل رقم المشترك → onClick BtnAddCust:
   │   ├─ POST /api/Payment/GetCustomersData {c_no, op_typ, user_branch, user_no}
   │   ├─ Response: {customersList: [{c_no, c_name, c_bal, cst_address, cst_lastread, ...}]}
   │   └─ يملأ الحقول
   │
   ├─ المستخدم يدخل المبلغ → x_text_watcher يحدّث الرصيد المتبقي حياً
   │
   ├─ (اختياري) يضغط زر الكاميرا → DroidCameraXP يلتقط صورة العدّاد
   │   → يضغط الصورة لـ width=user.imgWdth (default 300px)
   │   → Base64 encoding → يخزّن في `M` field
   │
   ├─ يضغط حفظ (btn_save):
   │   ├─ تحقق U(this):
   │   │   - رقم المشترك مطلوب
   │   │   - الاسم مطلوب  
   │   │   - المبلغ مطلوب (إلا في OP_TYP=3)
   │   │   - صورة العدّاد مطلوبة إن (OP_TYP=2 && user.read_must_take_img == "1")
   │   │   - GPS مطلوب إن user.Ues_Gps > 0
   │   │
   │   └─ يعرض حوار تأكيد → onConfirm e0(this).onClick(yes):
   │       ├─ OP_TYP=1: POST /api/Payment/saveBillRequest
   │       │            {payinfo:{c_no, c_name, c_bal:newBalance, v_amt, c_note, user_gps_loc}}
   │       │
   │       ├─ OP_TYP=2: POST /api/Payment/saveReadingRequest
   │       │            {payinfo:{c_no, c_name, v_amt:reading, c_note, BRD_ImgName, BRD_ImgData}}
   │       │
   │       └─ OP_TYP=3: POST /api/Payment/saveCustLocation
   │                    {payinfo:{c_no, c_name, user_gps_loc}}
   │
   ├─ بعد الحفظ بنجاح:
   │   ├─ يعرض رقم السند (v_no)
   │   ├─ يطبع تلقائياً إن متصل بطابعة Bluetooth
   │   ├─ يظهر زر "طباعة" و "مشاركة" و "جديد"
   │
   └─ المستخدم يضغط "جديد" → P() reset كل الحقول
              │
              ▼
7. المستخدم يخرج (back press)
              │
              ├─ MainActivity:
              │   onBackPressed() → يعرض AlertDialog "هل تريد الخروج؟"
              │   → نعم → finishAffinity()
              │
              ├─ OprationsActivity:
              │   u() → finish() → يعود لـ MainActivity
              │
              └─ WebviewActivity:
                  onBackPressed():
                    if (webview.canGoBack()) → goBack()
                    else → finish()
```

---

## دورة حياة كل شاشة (Activity Lifecycle)

### LoginActivity
```
onCreate
  └─ requestPermissions (if Android >= 23)
     └─ if all granted → A() = real init
        └─ resolve deeplink
        └─ fetch RSA public key (background)

onClick btn_login → either go to settings (backdoor) or call Login API
```

### MainActivity
```
onCreate
  └─ load user
  └─ bind 7 buttons, set visibility by roles
  └─ no permission re-request, no auto-refresh
  
onBackPressed → confirm exit
```

### OprationsActivity
```
onCreate
  └─ read OP_TYP from intent extras
  └─ initialize UI for that mode (1=Payment, 2=Reading, 3=Location)
  └─ if OP_TYP=1: create Bluetooth Printer manager
  └─ if user.Ues_Gps > 0: start location tracking (c.b.a.b.d)

onStart → printer.startScan
onStop  → printer.stopScan
onDestroy
  └─ stop location
  └─ disconnect printer
  └─ release Bluetooth resources

onActivityResult
  └─ if RC_CAMERA: process image, base64-encode
  └─ if RC_PRINTER_SETTINGS (299): refresh printer state
```

### WebviewActivity
```
onCreate
  └─ requestPermissions
     └─ y() = real init:
        ├─ getIntent extras: page=path, title=, OP_TYP=, authz=optional token
        ├─ create WebView with DANGEROUS settings:
        │   • setJavaScriptEnabled(true)
        │   • setAllowFileAccess(true)
        │   • setAllowUniversalAccessFromFileURLs(true)   ← XSS-to-Native!
        │   • setDomStorageEnabled(true)
        │   • setDatabaseEnabled(true)
        ├─ addJavascriptInterface(new i(...), "mobile")   ← Bridge
        ├─ setWebViewClient(new h(...))                   ← SSL bypass
        ├─ setWebChromeClient(new a())                    ← Alert/Confirm
        └─ webview.loadUrl(page) with optional Bearer header

onBackPressed
  └─ if webview.canGoBack() → goBack
  └─ else → finish

onDestroy → release printer resources
```

---

## مفاتيح SharedPreferences (Persistence)

```
File: "USER_DETAILS_PREF" (default mode)

┌──────────────────────────┬───────────────────────────────────────────────────────────┐
│ Key                      │ Value                                                       │
├──────────────────────────┼───────────────────────────────────────────────────────────┤
│ APP_USER_KEY             │ JSON(User) — كل بيانات المستخدم + token + permissions     │
│ APP_PK_KEY               │ "modulus_b64&exponent_b64" — مفتاح RSA عمومي للسيرفر       │
│ APP_SERVER_IP_KEY        │ "https://abbasiy.yedns.org:8057/payment" أو من deeplink   │
│ APP_SERVER_CER_KEY       │ "" دائماً (يُمسح عند deeplink) — معلّق                      │
│ APP_USER_LOC_KEY         │ "lat,long" — آخر موقع GPS مُحدّث                            │
│ APP_AREADATALIST_KEY     │ JSON([Area]) — قائمة المناطق المسموح بها للمستخدم          │
└──────────────────────────┴───────────────────────────────────────────────────────────┘

ملاحظة: التطبيق يقرأ كذلك من PreferenceManager للـ printer settings:
File: "<package>_preferences" (default by PreferenceManager)
Key: "key_printer_name"   — قيمة من r310_bixlion / sewoo / ...
Key: "key_printer_address" — MAC address للطابعة المُختارة
```

---

## حالات الأخطاء (Error States)

```
Network error:
  • HTTP 401  → يعرض ProgressBar ثم يعيد الدخول (logout effect): new f0(activity).h()
  • HTTP 500  → "فشل الاتصال بالخادم" Toast
  • Timeout   → 10000ms × 1 retry (Volley default)
  • No network → AlertDialog "لايوجد إتصال بالشبكة" قبل المحاولة أصلاً

Backend error (GEN_API_ERR_NO != 0):
  • c.b.a.d.e(msg, activity) → AlertDialog مع الرسالة من السيرفر

Permission denied:
  • تطبيق ينهي نفسه: finish()
  • لا fallback، لا UI خاصة

WebView error:
  • يحمّل default_error_page.html
  • يعرض AlertDialog "لايوجد إتصال بالشبكة" إن مناسب

Printer connection failed:
  • Toast بسيط
  • لا retry تلقائي
```

---

## ملاحظات صحفية على دورة الحياة

1. **لا Splash screen حقيقي** — التطبيق يفتح مباشرة على Login.
2. **لا Auto-login** — كل فتح يحتاج إدخال كلمة المرور (حتى لو أُغلق التطبيق للتو).
3. **`MainActivity` لا تعيد تحميل بيانات المستخدم** — قد تكون قديمة جداً.
4. **`WebviewActivity` تحمّل صفحات Local + Remote** — هجين خطر.
5. **`OprationsActivity` تقوم بـ heavy lifting** — كاميرا، طابعة، GPS، API، Bluetooth، Bitmap.

---

**التالي:** [`../02_api_contract/01_endpoints_overview.md`](../02_api_contract/01_endpoints_overview.md)
