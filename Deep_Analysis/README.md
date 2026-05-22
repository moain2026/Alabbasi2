# Deep Analysis — AbbasiyCashiers (Ecas v18.4)

> **التحليل الهندسي العميق لإعادة البناء** (Engineering-grade Deep Analysis for Rebuild)
>
> هذا المستودع هو **المصدر الموثوق الوحيد** لأي فريق يعمل على إعادة بناء تطبيق `AbbasiyCashiers` بأي تقنية حديثة.

---

## 🎯 الغرض من هذا المجلد

التحليل السابق في `../AbbasiyCashiers_RE_Analysis/` كان **تحليلاً أمنياً** (Security Audit). أما هذا المجلد فهو **تحليل هندسي شامل** (Engineering Spec) يجيب على السؤال:

> *"لو كان عليّ بناء هذا التطبيق من الصفر اليوم، ماذا أحتاج أن أعرف؟"*

كل تفصيلة موثَّقة هنا تكفي لأي مطوّر/فريق لإعادة البناء **بدون الحاجة للرجوع للكود الأصلي**.

---

## 📊 ملخص التطبيق

| المعيار | القيمة |
|---|---|
| **اسم التطبيق** | Ecas / AbbasiyCashiers |
| **الحزمة** | `com.egy.webpaymentapp` |
| **النوع** | تطبيق مدفوعات/تحصيل (Cashier / Payment Collection) |
| **اللغة الأم** | العربية (RTL) |
| **العملة** | الريال اليمني (YER) + فلس |
| **بنية التطبيق** | **WebView Wrapper** — قشرة Android حول صفحات ويب |
| **النمط المعماري** | Native Shell + HTML/JS UI + REST API + Bluetooth POS Printer |
| **الـ Backend** | `https://abbasiy.yedns.org:8057/payment` (HTTPS، شهادة self-signed) |
| **الطابعة المدعومة** | Bixolon (POS Thermal Printers) عبر JPOS framework |
| **معالجة الصور** | OpenCV + libJoinImage.so (احتمالاً لـ Bluetooth scanner) |
| **عدد الأنشطة (Activities)** | 6 |
| **عدد طرق JS Bridge** | 6 |
| **عدد API endpoints** | 9 (3 Users + 6 Payment) |
| **عدد Gson Models** | 7 (User, Payinfo, UserRoles + 4 inner: a/b/c/d) |
| **عدد ملفات HTML** | 4 (3 صفحات وظيفية + 1 خطأ) |
| **عدد ملفات JS** | 4 (paymentlist, readinglist, report, report_2) |

---

## 🗺️ خريطة الملف الشاملة (Top-level Map)

```
Deep_Analysis/
│
├── README.md                          ← أنت هنا
│
├── _raw_extracted/                    ← المواد الخام بعد فك التموية
│   ├── html/                          ← 4 ملفات HTML بعد deobfuscation
│   ├── js/                            ← 4 ملفات JS بعد deobfuscation
│   └── css/                           ← ملفات CSS الأصلية
│
├── 01_overview/                       ← النظرة العامة + خريطة المشروع
│   ├── 01_executive_summary.md        ← ملخص تنفيذي للقائمين
│   ├── 02_architecture_diagram.md     ← مخطط البنية المعمارية
│   └── 03_app_lifecycle.md            ← دورة حياة التطبيق
│
├── 02_api_contract/                   ← عقد الـ API الكامل
│   ├── 01_endpoints_overview.md       ← قائمة كل الـ 9 endpoints
│   ├── 02_authentication.md           ← Login / ChangePass / GetAppPK
│   ├── 03_payments_endpoints.md       ← GetPayments / SavePayment / ...
│   ├── 04_readings_endpoints.md       ← GetReadings / SaveReading
│   ├── 05_error_codes.md              ← رموز الأخطاء + معانيها
│   └── 06_request_examples.md         ← أمثلة JSON كاملة
│
├── 03_data_models/                    ← نماذج البيانات
│   ├── 01_user_model.md               ← نموذج المستخدم بكل حقوله
│   ├── 02_payinfo_model.md            ← نموذج معلومات الدفع
│   ├── 03_userroles_model.md          ← نموذج صلاحيات المستخدم
│   ├── 04_payment_record.md           ← سجل الدفع (في WebView/JSON)
│   └── 05_reading_record.md           ← سجل القراءة (في WebView/JSON)
│
├── 04_screens_flow/                   ← الشاشات وتدفقها
│   ├── 01_login_screen.md             ← شاشة الدخول
│   ├── 02_change_password_screen.md   ← شاشة تغيير كلمة المرور
│   ├── 03_main_screen.md              ← الشاشة الرئيسية
│   ├── 04_operations_screen.md        ← شاشة العمليات (إيداع/سحب)
│   ├── 05_webview_screen.md           ← شاشة WebView (التقارير)
│   └── 06_settings_screen.md          ← شاشة إعدادات الطابعة
│
├── 05_webview_bridge/                 ← الجسر بين WebView و Android
│   ├── 01_bridge_overview.md          ← نظرة شاملة على الـ JS Bridge
│   ├── 02_GetPaymentsRequest.md       ← دالة سحب قائمة المدفوعات
│   ├── 03_GetReadingDataRequest.md    ← دالة سحب قائمة القراءات
│   ├── 04_ShareReport.md              ← مشاركة الإيصال
│   ├── 05_printPdfReport.md           ← طباعة الإيصال
│   ├── 06_sharexPdfReport.md          ← مشاركة بصيغة بديلة
│   └── 07_reloadWebPage.md            ← إعادة تحميل الصفحة
│
├── 06_business_logic/                 ← منطق الأعمال
│   ├── 01_login_flow.md               ← منطق تسجيل الدخول التفصيلي
│   ├── 02_deeplink_handler.md         ← التعامل مع روابط ecas.web.link
│   ├── 03_payment_collection.md       ← منطق تحصيل المدفوعات
│   ├── 04_meter_reading.md            ← منطق قراءة العداد
│   ├── 05_receipt_generation.md       ← توليد سند التحصيل
│   ├── 06_arabic_number_to_words.md   ← خوارزمية تحويل الرقم لكلمات
│   └── 07_currency_handling.md        ← التعامل مع العملة (YER)
│
├── 07_crypto_protocols/               ← بروتوكولات التشفير
│   ├── 01_rsa_password_encryption.md  ← تشفير كلمة المرور (RSA)
│   ├── 02_desede_deeplink.md          ← تشفير الـ deeplink (DESede)
│   ├── 03_hmac_sha1_signing.md        ← التوقيع (HMAC-SHA1) - dead code
│   └── 04_test_vectors.md             ← متجهات اختبار قابلة للتشغيل
│
├── 08_native_libs/                    ← المكتبات الأصلية (.so)
│   ├── 01_libJoinImage.md             ← مكتبة دمج الصور
│   ├── 02_libbxlpdf.md                ← Bixolon PDF generator
│   ├── 03_libcomm_serial_port.md      ← منفذ تسلسلي للطابعات
│   └── 04_libopencv_java.md           ← OpenCV
│
├── 09_assets_resources/               ← الأصول والموارد
│   ├── 01_html_pages.md               ← تحليل الـ 4 صفحات HTML
│   ├── 02_javascript_files.md         ← تحليل الـ 4 ملفات JS
│   ├── 03_strings_resources.md        ← string resources (192 string × 117 lang)
│   ├── 04_drawables.md                ← 485 drawable
│   ├── 05_layouts.md                  ← 131 layout XML
│   └── 06_color_palette.md            ← لوحة الألوان المستخدمة
│
└── 10_rebuild_blueprint/              ← مخطّط إعادة البناء
    ├── 01_tech_stack_options.md       ← مقارنة Tech Stacks (RN/Flutter/Native/PWA)
    ├── 02_recommended_architecture.md ← البنية المعمارية المُوصى بها
    ├── 03_data_models_typescript.md   ← TypeScript models جاهزة
    ├── 04_api_client_skeleton.md      ← هيكل HTTP client
    ├── 05_security_improvements.md    ← الإصلاحات الأمنية المطلوبة
    ├── 06_ui_modernization.md         ← تحديث الواجهة (Material/iOS)
    ├── 07_migration_path.md           ← خطة الانتقال للتطبيق الجديد
    └── 08_acceptance_criteria.md      ← معايير قبول النسخة الجديدة
```

---

## 🚀 من أين تبدأ القراءة؟

### 👔 إذا كنت **مدير المشروع / صاحب القرار**
1. اقرأ `01_overview/01_executive_summary.md` (5 دقائق)
2. ثم `10_rebuild_blueprint/01_tech_stack_options.md` (10 دقائق)
3. ثم `10_rebuild_blueprint/07_migration_path.md` (15 دقيقة)

### 👨‍💻 إذا كنت **مطوّر سيُعيد البناء**
1. ابدأ بـ `01_overview/02_architecture_diagram.md`
2. ثم اقرأ `02_api_contract/` بالترتيب (هذا الأهم!)
3. ثم `03_data_models/` كله
4. ثم `05_webview_bridge/` كاملاً
5. ثم `06_business_logic/` كاملاً
6. أخيراً `10_rebuild_blueprint/` للتنفيذ

### 🔐 إذا كنت **مهندس أمن**
1. اقرأ `07_crypto_protocols/` كاملاً
2. ثم راجع `../AbbasiyCashiers_RE_Analysis/07_report/FINAL_REPORT.md`
3. ثم `10_rebuild_blueprint/05_security_improvements.md`

### 🎨 إذا كنت **مصمم UI/UX**
1. اقرأ `04_screens_flow/` كاملاً
2. ثم `09_assets_resources/06_color_palette.md`
3. ثم `10_rebuild_blueprint/06_ui_modernization.md`

---

## 📈 حالة التوثيق

| القسم | الحالة | التفصيل |
|---|---|---|
| 01_overview | ✅ مكتمل | 3/3 ملفات — executive_summary, architecture_diagram, app_lifecycle |
| 02_api_contract | ✅ مكتمل | 6/6 ملفات — endpoints, auth, payments, readings, errors, examples |
| 03_data_models | ✅ مكتمل | 5/5 ملفات — User, Payinfo, UserRoles, payment_record, reading_record |
| 04_screens_flow | ✅ مكتمل | 6/6 ملفات — Login, ChangePass, Main, Operations, WebView, Settings |
| 05_webview_bridge | ✅ مكتمل | 7/7 ملفات — bridge_overview + 6 bridge methods |
| 06_business_logic | 🚧 جاري | 3/7 ملفات — login_flow ✅, deeplink_handler ✅, payment_collection ✅؛ المتبقي: meter_reading, receipt_generation, arabic_number_to_words, currency_handling |
| 07_crypto_protocols | ⏳ متبقي | 0/4 ملفات — rsa_password, desede_deeplink, hmac_sha1, test_vectors |
| 08_native_libs | ⏳ متبقي | 0/4 ملفات — libJoinImage, libbxlpdf, libcomm_serial_port, libopencv_java |
| 09_assets_resources | ⏳ متبقي | 0/6 ملفات — html, js, strings, drawables, layouts, colors |
| 10_rebuild_blueprint | ⏳ متبقي | 0/8 ملفات — tech_stack, architecture, ts_models, api_client, security, ui, migration, acceptance |

### 📊 إجمالي التقدم
- **مكتمل:** 30 ملف (من أصل ~52)
- **النسبة:** ~58%
- **حجم الوثائق:** ~580KB من النصوص التحليلية العميقة (مع رسومات ASCII، مخططات تسلسل، أمثلة كود، مصفوفات مخاطر)

> سيتم تحديث هذا الجدول مع تقدّم التوثيق. كل قسم سيُحدّث عند اكتمال جميع ملفاته.

---

## 🔑 المفاتيح الرئيسية المستخرجة (Quick Reference)

### نقاط النهاية (Endpoints) — الحقيقية كما هي في الكود

```
Base URL (default): https://abbasiy.yedns.org:8057/payment
Full URL pattern  : {Base}/api/{Controller}/{Action}

— Users Controller —
  POST  /api/Users/getAppPK                 ← جلب RSA public key (مرحلة pre-login)
  POST  /api/Users/Login                    ← تسجيل الدخول (كلمة المرور مشفّرة RSA)
  POST  /api/Users/changePasswordRequest    ← تغيير كلمة المرور

— Payment Controller —
  POST  /api/Payment/GetCustomersData       ← البحث عن مشترك / جلب بياناته
  POST  /api/Payment/saveBillRequest        ← حفظ دفعة جديدة (Payment Save)
  POST  /api/Payment/saveReadingRequest     ← حفظ قراءة عداد جديدة
  POST  /api/Payment/saveCustLocation       ← حفظ إحداثيات GPS للمشترك
  POST  /api/Payment/GetPaymentsReportData  ← قائمة المدفوعات (للـ WebView)
  POST  /api/Payment/GetReadingListData     ← قائمة القراءات (للـ WebView)
```

**ملاحظات هامة:**
- جميع الـ endpoints **POST** (لا يوجد GET أبداً).
- جميعها تستقبل JSON عبر `Content-Type: application/json` وترجع JSON.
- الـ Authorization header: `Bearer {token}` (الـ token من حقل `User.Token` بعد Login).
- **خادم محتمل: ASP.NET Web API 2** (الـ pattern `/api/Controller/Action` نموذجي لـ Web API).

### JS Bridge Methods (`window.mobile.*`)
```javascript
window.mobile.GetPaymentsRequest(searchText)
window.mobile.GetReadingDataRequest(searchText)
window.mobile.printPdfReport(jsonString)
window.mobile.sharexPdfReport(jsonString)
window.mobile.ShareReport(jsonString)
window.mobile.reloadWebPage()
```

### حقول السجل المالي (Payment Record JSON)
```typescript
interface PaymentRecord {
  c_no: string;        // رقم المشترك (Customer Number)
  c_name: string;      // اسم المشترك (Customer Name)
  c_bal?: string;      // الرصيد الحالي
  v_no: string;        // رقم السند (Voucher Number)
  v_date: string;      // تاريخ السند
  v_amt: string;       // مبلغ التسديد (Voucher Amount)
  v_copy?: string;     // علامة (بدل فاقد)
  user_name?: string;  // اسم المتحصل
  comp_name?: string;  // اسم الشركة
  comp_add?: string;   // عنوان الشركة
  comp_tel?: string;   // هاتف الشركة
}
```

### التشفير المُكتشَف
| الخوارزمية | الاستخدام | المفتاح |
|---|---|---|
| **RSA/ECB/PKCS1PADDING** | تشفير كلمة المرور قبل الإرسال | يُجلب من `/GetAppPK` |
| **DESede (3DES)/ECB** | تشفير معامل `?ip=` في الـ deeplink | hardcoded: `m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##` |
| HMAC-SHA1 | dead code (موجود لكن لا يُستخدم) | - |
| SHA-256 | dead code | - |

### Deeplink Schema
```
https://ecas.web.link/?ip=<base64-encoded DESede ciphertext>
                              ↓
                       يفك للحصول على IP/host جديد للسيرفر
```

### Magic Backdoor (نقطة دخول مخفية)
```
Username: 1
Password: 1
Code:     1
                → يفتح شاشة الإعدادات بدون مصادقة
```

---

## ⚠️ تنبيهات أساسية للفريق

1. **التشفير يجب إعادة تصميمه** — المفاتيح المزروعة + تعطيل SSL = ثغرات حرجة
2. **WebView يجب إعادة تصميمه** — JS Bridge الحالي يحمل مخاطر XSS-to-Native
3. **بنية WebView+HTML قديمة** — يُوصى بـ Native UI أو React Native بدلاً عنها
4. **النسخة الحالية تعمل على Android 4.4+** — يمكن رفع الحد الأدنى لـ Android 7+
5. **الـ HTML الحالي مُموَّه بـ URL encoding** — هذا ليس أمناً، فقط تشويش بصري
6. **بعض حقول النصوص العربية بترميز ASMO 449 قديم** — يجب التحويل لـ UTF-8

---

## 📚 المراجع المُستخدمة

- مصدر الكود: `/home/user/webapp/AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/`
- مصدر الـ assets: `/home/user/webapp/AbbasiyCashiers_RE_Analysis/02_apktool_output/AbbasiyCashiers/assets/myweb/`
- التحليل الأمني السابق: `/home/user/webapp/AbbasiyCashiers_RE_Analysis/07_report/FINAL_REPORT.md`

---

**آخر تحديث:** 2026-05-22 | **محرّر:** GenSpark AI Developer | **حالة:** 30 ملف مكتمل (~58%) — يستكمل في الجلسات القادمة
