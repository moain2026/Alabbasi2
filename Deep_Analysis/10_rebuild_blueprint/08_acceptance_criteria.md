# 10.08 — Acceptance Criteria (معايير القبول)

> **القسم:** `10_rebuild_blueprint/` — الملف 8 من 8 (الأخير في هذا القسم) ✅
> **الموضوع:** كيف نعرف بشكل قاطع وقابل للقياس أن إعادة البناء قد نجحت
> **المخاطبون:** Product Manager، QA Lead، الإدارة، صاحب المشروع
> **يعتمد على:** كل ملفات `Deep_Analysis/` (01-10)

---

## 📌 الفهرس

1. [المنهجية](#1-المنهجية)
2. [قائمة تكافؤ الميزات (Feature Parity)](#2-قائمة-تكافؤ-الميزات-feature-parity)
3. [قائمة الأمان (V1-V20)](#3-قائمة-الأمان-v1-v20)
4. [معايير الأداء (Performance Benchmarks)](#4-معايير-الأداء-performance-benchmarks)
5. [سيناريوهات UAT](#5-سيناريوهات-uat)
6. [اختبارات قابلية الاستخدام للكاشير](#6-اختبارات-قابلية-الاستخدام-للكاشير)
7. [اختبارات التوافق](#7-اختبارات-التوافق-compatibility)
8. [اختبارات قاعدة البيانات والمزامنة](#8-اختبارات-قاعدة-البيانات-والمزامنة)
9. [اختبارات الطابعة](#9-اختبارات-الطابعة)
10. [معايير قابلية الوصول (a11y)](#10-معايير-قابلية-الوصول-a11y)
11. [الجودة الفنية](#11-الجودة-الفنية)
12. [معايير الموافقة النهائية (Sign-off)](#12-معايير-الموافقة-النهائية-sign-off)

---

## 1) المنهجية

### 1.1 صيغة كل معيار

كل معيار قبول يجب أن يكون **SMART**:
- **S**pecific (محدد)
- **M**easurable (قابل للقياس)
- **A**chievable (قابل للتحقيق)
- **R**elevant (ذو صلة)
- **T**ime-bound (محدد زمنياً)

**الصيغة المستخدمة:**

```gherkin
AC-XXX: [العنوان]
  Given: [الحالة الابتدائية]
  When: [الإجراء]
  Then: [النتيجة المتوقعة]
  Verification: [كيف نتحقق]
  Status: [Pass | Fail | Blocked | Not Tested]
```

### 1.2 مستويات الأولوية

| الأولوية | الرمز | المعنى | تأثير الفشل |
|---|---|---|---|
| **P0 - Critical** | 🔴 | لا يمكن الإطلاق بدونها | يوقف الإطلاق |
| **P1 - High** | 🟠 | مهم لـ MVP | يؤخر الإطلاق |
| **P2 - Medium** | 🟡 | مهم للنسخة 1.0 | يُسجّل كـ bug |
| **P3 - Low** | 🟢 | NICE-TO-HAVE | يؤجل للنسخة التالية |

### 1.3 حالات الاختبار

| الحالة | الرمز | المعنى |
|---|---|---|
| ✅ Pass | اجتاز | عُمل عليه واجتاز |
| ❌ Fail | فشل | عُمل عليه وفشل (يحتاج إصلاح) |
| ⏸️ Blocked | محظور | لا يمكن اختباره الآن |
| ⏳ Not Tested | لم يُختبر | بانتظار |
| 🚫 N/A | غير منطبق | غير متاح في هذا الإصدار |

---

## 2) قائمة تكافؤ الميزات (Feature Parity)

> **القاعدة:** كل ميزة في `Ecas v18.4` يجب أن يكون لها مكافئ أو بديل أفضل في الجديد. أو يجب توثيق سبب الحذف.

### 2.1 المصادقة والمستخدمين

| # | الميزة الحالية (Ecas v18.4) | المعادل الجديد | الحالة | الأولوية |
|---|---|---|---|---|
| AUTH-01 | تسجيل دخول بـ username + password | تسجيل دخول بـ username + password (RSA encrypted) | ⏳ | 🔴 P0 |
| AUTH-02 | حفظ بيانات المستخدم في SharedPreferences | حفظ Token في Keychain (أكثر أماناً) | ⏳ | 🔴 P0 |
| AUTH-03 | تسجيل خروج يدوي | تسجيل خروج يدوي + تلقائي بعد فترة خمول | ⏳ | 🔴 P0 |
| AUTH-04 | **Magic Backdoor `1/1/1`** ❌ | **محذوف** — استُبدل بـ Dev Build فقط (V1) | ⏳ | 🔴 P0 |
| AUTH-05 | 4 booleans للصلاحيات (Cont, Coll, Read, GetReads) | object `UserPermissions` مع نفس الحقول + توسعة | ⏳ | 🟠 P1 |
| AUTH-06 | لا يوجد قفل بعد محاولات فاشلة | قفل لمدة 5 دقائق بعد 5 محاولات فاشلة | ⏳ | 🟠 P1 |
| AUTH-07 | لا يوجد Refresh Token | Refresh Token مع انتهاء صلاحية | ⏳ | 🟠 P1 |

### 2.2 إدارة العملاء

| # | الميزة الحالية | المعادل الجديد | الحالة | الأولوية |
|---|---|---|---|---|
| CUST-01 | جلب قائمة العملاء `/Customer/CustomersByCashId` | نفس الـ endpoint مع تحسين caching | ⏳ | 🔴 P0 |
| CUST-02 | بحث بالاسم/رقم الحساب/رقم العداد | بحث offline + online، normalization عربي | ⏳ | 🔴 P0 |
| CUST-03 | عرض تفاصيل العميل | تفاصيل + تاريخ المعاملات | ⏳ | 🔴 P0 |
| CUST-04 | تحديث بيانات العميل من Server | Delta Sync كل فترة + Pull-to-refresh | ⏳ | 🟠 P1 |
| CUST-05 | عرض الرصيد المستحق | + رسم بياني للتاريخ (تحسين) | ⏳ | 🟡 P2 |

### 2.3 الدفع (Payments)

| # | الميزة الحالية | المعادل الجديد | الحالة | الأولوية |
|---|---|---|---|---|
| PAY-01 | إنشاء دفعة لعميل | نفس + idempotency key | ⏳ | 🔴 P0 |
| PAY-02 | إدخال المبلغ يدوياً | + تحقق Zod + اقتراحات مبلغ | ⏳ | 🔴 P0 |
| PAY-03 | إضافة ملاحظة (اختياري) | نفس | ⏳ | 🟠 P1 |
| PAY-04 | **Bug: `Pay_amount = lastRead - amount`** 🐛 | **مُصلح:** `Pay_amount = amount` | ⏳ | 🔴 P0 |
| PAY-05 | حفظ في Server فقط | Offline-first في WatermelonDB + مزامنة | ⏳ | 🔴 P0 |
| PAY-06 | لا rollback في حالة فشل الطباعة | Transactional: نجح كلاهما أو لا شيء | ⏳ | 🔴 P0 |
| PAY-07 | لا confirmation dialog واضحة | dialog ثنائي التأكيد للمبالغ > 100,000 ريال | ⏳ | 🟠 P1 |
| PAY-08 | لا undo للمعاملات | Undo خلال 30 ثانية قبل الطباعة | ⏳ | 🟡 P2 |

### 2.4 قراءة العداد (Meter Reading)

| # | الميزة الحالية | المعادل الجديد | الحالة | الأولوية |
|---|---|---|---|---|
| READ-01 | إدخال قراءة جديدة | إدخال + تحقق ≥ القراءة السابقة | ⏳ | 🔴 P0 |
| READ-02 | التقاط صورة عداد | نفس + ضغط محلي < 200KB | ⏳ | 🔴 P0 |
| READ-03 | رفع الصورة للخادم | + Resume عند انقطاع الشبكة | ⏳ | 🔴 P0 |
| READ-04 | لا حساب تلقائي للاستهلاك | عرض الفرق (newReading - lastReading) | ⏳ | 🟠 P1 |
| READ-05 | لا تحذير من قفزات غير منطقية | تحذير إذا الاستهلاك > 200% من المتوسط | ⏳ | 🟡 P2 |
| READ-06 | لا OCR للقراءة | OCR لاقتراح قيمة من الصورة (نسخة 1.1) | 🚫 | 🟢 P3 |

### 2.5 الطباعة (Printing)

| # | الميزة الحالية | المعادل الجديد | الحالة | الأولوية |
|---|---|---|---|---|
| PRINT-01 | اتصال Bluetooth بطابعة POS | نفس عبر TurboModule | ⏳ | 🔴 P0 |
| PRINT-02 | طباعة إيصال دفع | نفس + تحسينات تصميم | ⏳ | 🔴 P0 |
| PRINT-03 | طباعة إيصال قراءة | نفس | ⏳ | 🟠 P1 |
| PRINT-04 | حفظ آخر طابعة مستخدمة | نفس | ⏳ | 🟠 P1 |
| PRINT-05 | لا QR في الإيصال | QR للتحقق من الإيصال online | ⏳ | 🟡 P2 |
| PRINT-06 | لا إعادة طباعة | إعادة طباعة آخر إيصال + من الأرشيف | ⏳ | 🟠 P1 |
| PRINT-07 | تحويل الأرقام إلى كلمات عربية | نفس + تحسينات (الجمع، المؤنث) | ⏳ | 🟠 P1 |

### 2.6 التقارير

| # | الميزة الحالية | المعادل الجديد | الحالة | الأولوية |
|---|---|---|---|---|
| RPT-01 | تقرير يومي في WebView | شاشة Native + إحصائيات بصرية | ⏳ | 🟠 P1 |
| RPT-02 | لا تصدير | تصدير PDF | ⏳ | 🟡 P2 |
| RPT-03 | لا فلترة بالتاريخ | فلترة بالتاريخ والمنطقة | ⏳ | 🟡 P2 |
| RPT-04 | لا رسوم بيانية | Charts بسيطة (مدفوعات/يوم) | ⏳ | 🟢 P3 |

### 2.7 الإعدادات والميزات النظامية

| # | الميزة الحالية | المعادل الجديد | الحالة | الأولوية |
|---|---|---|---|---|
| SYS-01 | Deeplink لإعداد API URL (DESede) | Deeplink مع JWT-signed config | ⏳ | 🔴 P0 |
| SYS-02 | WebView لكل الواجهات | استبدال 100% بـ Native | ⏳ | 🔴 P0 |
| SYS-03 | لا إعداد ثيم | فاتح / داكن / حسب النظام | ⏳ | 🟡 P2 |
| SYS-04 | لا تغيير حجم النص | يحترم إعدادات النظام | ⏳ | 🟡 P2 |
| SYS-05 | لا audit log | سجل أحداث محلي + رفع للخادم | ⏳ | 🟠 P1 |
| SYS-06 | لا About screen مفصل | شاشة About + Diagnostics | ⏳ | 🟢 P3 |
| SYS-07 | لا تحديث تلقائي | فحص تحديث + إشعار | ⏳ | 🟡 P2 |

### 2.8 ميزات نضيفها (جديدة)

| # | ميزة جديدة | المبرر | الأولوية |
|---|---|---|---|
| NEW-01 | شريط حالة الشبكة دائم | offline-first يتطلب شفافية | 🔴 P0 |
| NEW-02 | شريط حالة المزامنة | الكاشير يحتاج معرفة كم معاملة معلقة | 🔴 P0 |
| NEW-03 | Toast notifications للأحداث | UX أفضل من Alert dialogs | 🟠 P1 |
| NEW-04 | تنقل بـ Bottom Tabs | أسهل من Hamburger في WebView | 🔴 P0 |
| NEW-05 | Pull-to-refresh في القوائم | معيار حديث | 🟠 P1 |
| NEW-06 | Skeleton loading | UX أفضل من ActivityIndicator | 🟡 P2 |
| NEW-07 | Empty states واضحة | "لا توجد معاملات اليوم" | 🟡 P2 |
| NEW-08 | Animations بسيطة | يحس التطبيق "حياً" | 🟡 P2 |
| NEW-09 | Biometric login (بصمة) | راحة المستخدم | 🟢 P3 |
| NEW-10 | Multi-language (مستقبلاً) | لو توسعت الخدمة | 🚫 P3 |

### 2.9 الملخص

```
الإجمالي: 48 ميزة موثقة
  P0 (Critical):    19 ميزة  ━━━━━━━━━━━━━━━━━━━ 40%
  P1 (High):        15 ميزة  ━━━━━━━━━━━━━━━ 31%
  P2 (Medium):      10 ميزة  ━━━━━━━━━━ 21%
  P3 (Low):          4 ميزات ━━━━ 8%
```

**شرط الإطلاق:** 100% من P0 + 90%+ من P1 = MVP

---

## 3) قائمة الأمان (V1-V20)

> **المرجع:** ملف `05_security_improvements.md` يحوي التفاصيل التقنية. هنا فقط checklist للقبول.

### 3.1 جدول القبول الأمني

| # | الثغرة في القديم | الحل في الجديد | حالة الإصلاح | مرحلة التحقق |
|---|---|---|---|---|
| **V1** | Magic Backdoor `1/1/1` في LoginActivity:65 | محذوف. Debug screen فقط في `__DEV__` | ⏳ | M2 |
| **V2** | Empty X509TrustManager (TLS bypass) | SSL Pinning مع شهادتين (primary + backup) | ⏳ | M1 |
| **V3** | لا تحقق من Certificate Chain | تحقق كامل + Pinning | ⏳ | M1 |
| **V4** | Hardcoded DESede key | مفاتيح من Keystore، لا تشفير في الكود | ⏳ | M1 |
| **V5** | Deeplink Hijacking — أي URL مقبول | JWT-signed config + allow-list نطاقات | ⏳ | M2 |
| **V6** | WebView: JavaScript enabled + File access | لا WebView في النهاية (M6) | ⏳ | M6 |
| **V7** | WebView: loadUrl لأي URL خارجي | N/A — مزال | ⏳ | M6 |
| **V8** | Tokens في SharedPreferences (clear-text) | Keychain (hardware-backed) | ⏳ | M2 |
| **V9** | لا Network Security Config | NSC + Cleartext traffic disabled | ⏳ | M1 |
| **V10** | لا Root Detection | jail-monkey + Custom checks | ⏳ | M7 |
| **V11** | لا Code Obfuscation (ProGuard معطل) | ProGuard + R8 + Hermes bytecode | ⏳ | M8 |
| **V12** | Logs verbose في Production | `console.log` يُحذف في Release build | ⏳ | M8 |
| **V13** | كلمات مرور قابلة للقراءة في الذاكرة | استخدام Keychain فقط، secure strings | ⏳ | M2 |
| **V14** | لا CSP في WebView | N/A — لا WebView | ⏳ | M6 |
| **V15** | لا Audit Log للأحداث الحساسة | تسجيل: login، payment، deeplink، etc. | ⏳ | M5 |
| **V16** | RSA Private Key مضمّن في APK | RSA فقط للعمومي. الخاص في الخادم | ⏳ | M2 |
| **V17** | HMAC Key مكشوف | HMAC في الخادم فقط، التطبيق يستهلك توكنات | ⏳ | M2 |
| **V18** | الـ JS Interface يعرض كل الـ class | TurboModule مع TypeScript types مقيدة | ⏳ | M4 |
| **V19** | `r(s(ip)) == ip` — تشفير عديم الفائدة | لا حاجة، البيانات مرسلة مباشرة عبر HTTPS | ⏳ | M2 |
| **V20** | Debug build مع `usesCleartextTraffic="true"` | NSC منفصل لـ Debug/Release | ⏳ | M1 |

### 3.2 اختبار قبول لكل ثغرة

#### AC-SEC-001: حذف Magic Backdoor

```gherkin
Given: التطبيق في وضع Production
When: المستخدم يدخل username=1 password=1
Then: يحصل على رسالة "بيانات تسجيل دخول خاطئة"
And: لا توجد شاشة إعدادات مخفية يمكن الوصول إليها
Verification:
  1. تثبيت Release APK
  2. محاولة 1/1/1
  3. منع التحويل التلقائي
  4. مراجعة الكود: grep "1/1/1" → لا نتائج
Status: ⏳
```

#### AC-SEC-002: SSL Pinning

```gherkin
Given: المستخدم يستخدم التطبيق على شبكة بها MITM (Burp Suite)
When: التطبيق يحاول الاتصال بالخادم
Then: الاتصال يفشل مع رسالة "خطأ في التحقق من الخادم"
And: لا تُكشف بيانات حساسة في proxy
Verification:
  1. تشغيل Burp Suite كـ proxy
  2. تثبيت Burp CA كنظام
  3. محاولة فتح التطبيق
  4. التحقق من عدم وصول طلبات إلى Burp
Status: ⏳
```

#### AC-SEC-003: Keychain للـ Tokens

```gherkin
Given: المستخدم سجل دخول بنجاح
When: نفحص ذاكرة التطبيق ووحدة التخزين
Then: لا يوجد Token قابل للقراءة في clear-text
And: Token موجود فقط في Android Keystore / iOS Keychain
Verification:
  1. تسجيل دخول
  2. تشغيل: adb shell run-as com.abbasiy.cashiers cat shared_prefs/*.xml
  3. التحقق: لا token هناك
  4. Frida script: محاولة قراءة Keychain → تتطلب biometric/PIN
Status: ⏳
```

### 3.3 اختبارات الأمان الشاملة

#### Penetration Testing

```
أداة: MobSF (Mobile Security Framework) + Frida + Burp Suite
المسؤول: Security Consultant خارجي
التوقيت: قبل أسبوعين من الإطلاق (M7)
النطاق:
  - Static Analysis (APK decompilation)
  - Dynamic Analysis (runtime)
  - Network Analysis (MITM, replay)
  - Storage Analysis (cleartext data)
  - Authentication (brute force, session)
  - Authorization (privilege escalation)
معايير القبول:
  - 0 ثغرات Critical/High
  - 0 ثغرات Medium في paths الحساسة
  - أقل من 5 ثغرات Low (مقبولة بإذن الإدارة)
```

#### قائمة OWASP Mobile Top 10

| # | الفئة | حالة التغطية |
|---|---|---|
| M1 | Improper Platform Usage | ⏳ |
| M2 | Insecure Data Storage | ⏳ (Keychain) |
| M3 | Insecure Communication | ⏳ (SSL Pinning) |
| M4 | Insecure Authentication | ⏳ (Token + Refresh) |
| M5 | Insufficient Cryptography | ⏳ (إزالة DESede) |
| M6 | Insecure Authorization | ⏳ (RBAC) |
| M7 | Client Code Quality | ⏳ (TS strict + ESLint) |
| M8 | Code Tampering | ⏳ (ProGuard + Root detection) |
| M9 | Reverse Engineering | ⏳ (Hermes bytecode) |
| M10 | Extraneous Functionality | ⏳ (لا Magic Backdoor) |

---

## 4) معايير الأداء (Performance Benchmarks)

### 4.1 جدول المقاييس

> **الأجهزة المرجعية:**
> - Low-end: Samsung Galaxy A12 (4GB RAM, Android 11)
> - Mid-range: Samsung Galaxy A52 (6GB RAM, Android 12)
> - High-end: Samsung Galaxy S22 (8GB RAM, Android 13)

| # | المقياس | الجهاز | الحالي (تقدير) | الهدف الجديد | كيف نقيس | الحالة |
|---|---|---|---|---|---|---|
| PERF-01 | Cold Start (إقلاق بارد) | Low-end | ~3000ms | < 1500ms | Firebase Performance | ⏳ |
| PERF-02 | Cold Start | Mid-range | ~2000ms | < 1000ms | نفس | ⏳ |
| PERF-03 | Warm Start (إقلاع دافئ) | Low-end | ~1500ms | < 500ms | نفس | ⏳ |
| PERF-04 | Login → Home | Low-end | ~5000ms | < 2000ms | Sentry transaction | ⏳ |
| PERF-05 | بحث في 10,000 عميل | Low-end | ~2000ms | < 500ms | Custom metric | ⏳ |
| PERF-06 | فتح تفاصيل عميل | كل الأجهزة | ~800ms | < 200ms | نفس | ⏳ |
| PERF-07 | حفظ دفعة محلياً | Low-end | N/A | < 100ms | WatermelonDB metric | ⏳ |
| PERF-08 | إرسال دفعة للخادم | كل الأجهزة | ~3000ms | < 1500ms | Network timing | ⏳ |
| PERF-09 | طباعة إيصال (Bluetooth) | كل الأجهزة | ~5000ms | < 3000ms | Native timing | ⏳ |
| PERF-10 | التقاط + ضغط صورة | Low-end | ~3000ms | < 1500ms | نفس | ⏳ |
| PERF-11 | رفع صورة 200KB (4G) | كل الأجهزة | ~4000ms | < 2000ms | Network timing | ⏳ |
| PERF-12 | فتح تقرير يومي | كل الأجهزة | ~3000ms | < 800ms | نفس | ⏳ |
| PERF-13 | مزامنة 100 معاملة | كل الأجهزة | N/A | < 30000ms | Sync timing | ⏳ |
| PERF-14 | حجم APK | — | ~15MB | < 25MB (مع Hermes) | gradle assembleRelease | ⏳ |
| PERF-15 | استهلاك RAM (idle) | كل الأجهزة | ~150MB | < 200MB | Android Studio Profiler | ⏳ |
| PERF-16 | استهلاك RAM (active) | كل الأجهزة | ~250MB | < 350MB | نفس | ⏳ |
| PERF-17 | استهلاك البطارية (يوم عمل) | Mid-range | ~25% | < 15% | Battery Historian | ⏳ |
| PERF-18 | حجم DB لـ 50,000 عميل | كل الأجهزة | N/A | < 50MB | du -sh on device | ⏳ |
| PERF-19 | FPS أثناء scroll | كل الأجهزة | ~45fps | ≥ 58fps | Flipper Perf | ⏳ |
| PERF-20 | Time to Interactive (TTI) | Low-end | ~4000ms | < 2000ms | RUM | ⏳ |

### 4.2 اختبارات الإجهاد (Stress Tests)

```typescript
// __tests__/stress/payments.stress.test.ts

describe('Payment Stress Tests', () => {
  it('handles 1000 offline payments without data loss', async () => {
    // 1. قطع الشبكة
    await NetInfo.configure({ reachabilityShouldRun: false });

    // 2. إنشاء 1000 دفعة
    const start = Date.now();
    for (let i = 0; i < 1000; i++) {
      await createPayment({
        customerId: `cust-${i % 100}`,
        amount: Math.random() * 50000,
      });
    }
    const elapsed = Date.now() - start;

    // 3. تحقق
    const count = await database.get('payments').query().fetchCount();
    expect(count).toBe(1000);
    expect(elapsed).toBeLessThan(60000); // < دقيقة لـ 1000

    // 4. تشغيل الشبكة
    await NetInfo.configure({ reachabilityShouldRun: true });

    // 5. تحقق المزامنة
    await syncQueue.processPending();
    const synced = await database.get('payments')
      .query(Q.where('sync_status', 'synced')).fetchCount();
    expect(synced).toBe(1000);
  }, 120000); // timeout 2 دقيقة
});
```

### 4.3 اختبارات الذاكرة

```bash
# قياس memory leaks باستخدام Android Studio Profiler

# 1. فتح التطبيق وإجراء عمليات لمدة 30 دقيقة:
#    - تسجيل دخول
#    - بحث عن 50 عميل
#    - تنفيذ 20 دفعة
#    - فتح/إغلاق 30 شاشة

# 2. التحقق من:
#    - عدم وجود memory leak (الذاكرة تعود لمستواها بعد GC)
#    - أقصى استهلاك < 350MB
#    - عدم وجود ANR (Application Not Responding)
```

---

## 5) سيناريوهات UAT

> **UAT = User Acceptance Testing**
> الكاشيرون الحقيقيون يختبرون التطبيق في بيئة شبيهة بالحقيقة.

### 5.1 سيناريو: يوم عمل كامل

```gherkin
SCENARIO: UAT-DAY-01 — يوم عمل عادي لكاشير ميداني

Actor: كاشير ميداني (مستخدم حقيقي)
Setup:
  - جهاز Android مع التطبيق مثبت
  - طابعة Bluetooth مُهيأة
  - 100 عميل في قائمة المتعاقدين

Steps:
  1. الكاشير يصل لأول عميل
     - يفتح التطبيق (يجب < 1.5s)
     - يسجل دخول (يجب < 2s)
     - يظهر Home مع آخر إحصائيات

  2. البحث عن العميل بالاسم
     - يكتب جزء من الاسم
     - يظهر العميل في < 500ms
     - يضغط على العميل

  3. تنفيذ الدفع
     - يضغط "دفع جديد"
     - يدخل المبلغ: 25,000
     - يضغط "تأكيد"
     - تظهر شاشة تأكيد
     - يضغط "نعم"

  4. الطباعة
     - يضغط "طباعة"
     - الإيصال يُطبع خلال 3 ثوانٍ
     - يعطي الإيصال للعميل

  5. الكاشير يتابع لـ 50 عميل بنفس الطريقة في يوم واحد

  6. في نهاية اليوم:
     - يرى التقرير اليومي
     - إجمالي 50 معاملة
     - المبلغ الكلي = مجموع المبالغ

Expected Result:
  - 50/50 معاملة تمت بنجاح
  - 50/50 إيصال طُبع
  - 50/50 معاملة مُزامنة على الخادم
  - 0 crashes
  - البطارية متبقي > 60%

Pass Criteria:
  - 0 معاملات مفقودة
  - 0 إيصالات فاشلة (إذا الطابعة تعمل)
  - وقت متوسط لكل عميل < 90 ثانية
```

### 5.2 سيناريو: انقطاع الشبكة

```gherkin
SCENARIO: UAT-NETWORK-01 — العمل بدون شبكة

Actor: كاشير في منطقة نائية
Setup:
  - WiFi مغلق، 4G ضعيف جداً
  - 10 عملاء معروفون (مزامنة مسبقاً)

Steps:
  1. فتح التطبيق
     - يجب يفتح بدون مشاكل
     - يظهر شارة "غير متصل" في الأعلى

  2. البحث عن عميل
     - يجد العميل (من cache المحلي)

  3. تنفيذ دفع
     - تظهر رسالة: "تم الحفظ. سيُرسل عند توفر الشبكة"
     - الإيصال يُطبع

  4. تكرار لـ 20 عميل

  5. الكاشير يعود لمنطقة بها شبكة
     - يفتح التطبيق
     - شارة "جاري المزامنة... (20)" تظهر
     - بعد دقيقة: "كل العمليات محفوظة"

  6. فحص الخادم
     - كل الـ 20 معاملة موجودة
     - بنفس التواريخ الأصلية (وقت الحفظ المحلي)

Expected Result:
  - 20/20 معاملة محفوظة محلياً
  - 20/20 إيصال مطبوع
  - 20/20 معاملة مُزامنة عند عودة الشبكة
  - 0 ازدواجية (idempotency)
  - 0 فقدان بيانات

Pass Criteria:
  - عدم القدرة على إنشاء معاملات في الخادم بدون idempotency check
  - الفاصل الزمني بين الحفظ المحلي والمزامنة محفوظ بدقة
```

### 5.3 سيناريو: تبديل المستخدمين

```gherkin
SCENARIO: UAT-USER-SWITCH-01 — كاشير يعطي الجهاز لآخر

Actor: كاشير A، ثم كاشير B
Setup: جهاز واحد

Steps:
  1. كاشير A يسجل دخول، ينفذ 10 معاملات
  2. كاشير A يضغط "تسجيل خروج"
  3. التطبيق يعود لشاشة Login
  4. التحقق:
     - لا يمكن رؤية معاملات كاشير A
     - Cache المعاملات لا يزال موجوداً (في DB، لكن غير مرئي)
  5. كاشير B يسجل دخول
  6. كاشير B يرى فقط بياناته (ليس بيانات A)
  7. كاشير B ينفذ معاملات

Expected Result:
  - الفصل التام بين بيانات الكاشيرين
  - لا تسريب معلومات
  - كل كاشير له audit log منفصل

Pass Criteria:
  - فحص DB: payments تربط بالـ cashier_id الصحيح
  - الخروج يمسح Keychain (token) لكن ليس قواعد البيانات (لا فقدان للـ pending payments)
```

### 5.4 سيناريو: استرداد الجلسة

```gherkin
SCENARIO: UAT-RESUME-01 — التطبيق يُغلق فجأة

Actor: كاشير
Setup: جهاز ببطارية ضعيفة

Steps:
  1. الكاشير يبدأ ملء استمارة دفع
  2. أدخل: العميل، المبلغ
  3. لم يضغط "تأكيد" بعد
  4. الجهاز يطفئ فجأة (انتهت البطارية)
  5. الكاشير يشحن ويعيد فتح التطبيق

Expected Result:
  - التطبيق يفتح في آخر شاشة كان فيها
  - الاستمارة محفوظة (Draft)
  - يظهر: "هل تريد استكمال الدفعة المحفوظة؟"

Pass Criteria:
  - Auto-save للنماذج كل 5 ثوانٍ
  - استعادة Draft عند الفتح
  - الكاشير له خيار: استكمال أو إلغاء
```

### 5.5 سيناريو: حالات الخطأ

```gherkin
SCENARIO: UAT-ERROR-01 — معالجة أخطاء الخادم

Actor: كاشير
Setup: الخادم يرجع أخطاء متنوعة

Steps:
  1. كاشير يحاول دفعة، الخادم يرجع 500
     Expected: رسالة واضحة "خطأ في الخادم. تم حفظ المعاملة، سيتم إعادة المحاولة"

  2. كاشير يحاول دفعة، الخادم يرجع 401
     Expected: تسجيل خروج تلقائي + رسالة "انتهت الجلسة"

  3. كاشير يحاول دفعة، الخادم يرجع 400 (validation error)
     Expected: رسالة محددة من الخادم بالعربية

  4. كاشير يحاول دفعة، timeout
     Expected: إعادة محاولة تلقائية 3 مرات، ثم حفظ محلي

Pass Criteria:
  - لا crashes في أي حالة خطأ
  - رسائل خطأ بالعربية ومفهومة
  - retry logic يعمل بشكل صحيح
```

---

## 6) اختبارات قابلية الاستخدام للكاشير

### 6.1 منهجية الاختبار

```yaml
المنهجية: Moderated Usability Testing
المشاركون: 5-7 كاشيرين (variety: junior, senior, age range)
المكان: مكتب مع طاولة + هاتف Android
المدة: 60 دقيقة لكل جلسة
المسؤول: UX Researcher
التسجيل:
  - Screen recording
  - Audio (مع موافقة المشارك)
  - Notes by researcher
```

### 6.2 المهام (Tasks)

#### Task 1: تسجيل الدخول

```
السياق: "هذا تطبيق جديد للجباية. سجل دخولك بهذا الحساب:
        Username: cashier_test
        Password: Test@123"

ملاحظات للمراقب:
  - هل وجد حقل اسم المستخدم بسرعة؟
  - هل عرف أن "*" تعني الحقل إجباري؟
  - كم محاولة احتاج؟

معايير النجاح:
  - أنهى المهمة في < 60 ثانية
  - بدون مساعدة
```

#### Task 2: البحث عن عميل وتنفيذ دفع

```
السياق: "العميل أحمد محمد جاء ليدفع 30,000 ريال. ابحث عنه ونفذ الدفع."

ملاحظات:
  - هل بحث بالاسم أم برقم الحساب؟
  - هل وجد زر "دفع جديد" بسهولة؟
  - هل أُربك بأي حقل؟
  - متى ضغط "تأكيد"؟

معايير النجاح:
  - أنهى المهمة في < 90 ثانية
  - بدون أخطاء (مبلغ صحيح، عميل صحيح)
```

#### Task 3: التعامل مع خطأ شبكة

```
السياق: "أوقف الشبكة من إعدادات الجهاز. الآن نفذ دفعة جديدة."

ملاحظات:
  - هل لاحظ شارة "غير متصل"؟
  - هل ارتبك أم أكمل بثقة؟
  - هل فهم رسالة "محفوظ محلياً"؟

معايير النجاح:
  - فهم أن العملية لم تُلغَ
  - أكمل المهمة بثقة
```

#### Task 4: مراجعة تقرير اليوم

```
السياق: "كم عدد المعاملات اليوم؟ وما إجمالي المبلغ؟"

ملاحظات:
  - هل وجد قسم التقارير بسهولة؟
  - هل قرأ الأرقام بشكل صحيح؟ (عربية/لاتينية)

معايير النجاح:
  - أنهى المهمة في < 30 ثانية
```

### 6.3 SUS Score (System Usability Scale)

```
بعد كل جلسة، المشارك يجيب على 10 أسئلة (1-5 likert):

1. أود استخدام هذا التطبيق بانتظام
2. التطبيق معقد بدون داعٍ
3. التطبيق سهل الاستخدام
4. أحتاج دعم تقني للتعامل معه
5. الميزات مدمجة بشكل جيد
6. هناك تضارب في التطبيق
7. معظم الناس سيتعلمونه بسرعة
8. التطبيق مرهق
9. أشعر بالثقة وأنا أستخدمه
10. أحتاج تعلم كثير قبل البدء

النتيجة: SUS Score
  >= 80: ممتاز
  68-79: جيد
  51-67: مقبول
  < 51: غير مقبول
```

**معيار القبول:** SUS Score >= 75

### 6.4 Net Promoter Score (NPS)

```
السؤال: "على مقياس 0-10، ما مدى احتمالية أن توصي
        زميلك بهذا التطبيق؟"

التحليل:
  - Promoters (9-10): يحبون التطبيق
  - Passives (7-8): محايدون
  - Detractors (0-6): يكرهون

NPS = % Promoters - % Detractors

معيار القبول: NPS >= +30 (جيد)
هدف الإطلاق: NPS >= +50 (ممتاز)
```

---

## 7) اختبارات التوافق (Compatibility)

### 7.1 مصفوفة الأجهزة

| الجهاز | OS | RAM | Test Priority | الحالة |
|---|---|---|---|---|
| Samsung Galaxy A03 | Android 11 | 3GB | 🔴 P0 | ⏳ |
| Samsung Galaxy A12 | Android 11/12 | 4GB | 🔴 P0 | ⏳ |
| Samsung Galaxy A22 | Android 12 | 4GB | 🔴 P0 | ⏳ |
| Samsung Galaxy A52 | Android 12/13 | 6GB | 🟠 P1 | ⏳ |
| Xiaomi Redmi 9A | Android 10 | 2GB | 🟠 P1 | ⏳ |
| Xiaomi Redmi Note 10 | Android 11 | 4GB | 🟠 P1 | ⏳ |
| Huawei Y6p | Android 10 (EMUI، لا Google) | 3GB | 🟡 P2 | ⏳ |
| Tecno Camon 17 | Android 11 | 4GB | 🟡 P2 | ⏳ |
| Infinix Hot 11 | Android 11 | 4GB | 🟡 P2 | ⏳ |
| Samsung Tab A7 | Android 11 | 3GB | 🟡 P2 (Tablet) | ⏳ |

### 7.2 إصدارات Android

```yaml
minSdkVersion: 24  # Android 7.0 Nougat
targetSdkVersion: 34  # Android 14
compileSdkVersion: 34

التغطية:
  Android 7 (24-25):  ~3%  - يجب أن يعمل
  Android 8 (26-27): ~6%  - يجب أن يعمل
  Android 9 (28):    ~12% - يجب أن يعمل ممتاز
  Android 10 (29):   ~18% - يجب أن يعمل ممتاز
  Android 11 (30):   ~25% - target الرئيسي
  Android 12 (31-32): ~20% - target الرئيسي
  Android 13 (33):   ~12% - target الرئيسي
  Android 14 (34):   ~4%  - يجب أن يعمل
```

### 7.3 اختبار Huawei (بدون Google Services)

> **مهم:** أجهزة Huawei الحديثة لا تحتوي على Google Play Services.

```typescript
// التحقق من توفر GMS
import { isGooglePlayServicesAvailable } from '@react-native-firebase/app';

if (!isGooglePlayServicesAvailable()) {
  // Fallback:
  //  - بدلاً من Firebase Analytics → Custom analytics
  //  - بدلاً من Crashlytics → Sentry
  //  - بدلاً من FCM Push → SMS notifications
}
```

**معيار القبول:** التطبيق يفتح ويعمل بكل وظائفه الأساسية على Huawei بدون GMS.

### 7.4 توافق الـ APIs

```bash
# اختبار توافق مع نسختين من Backend:
# - النسخة الحالية (التي يستخدمها التطبيق القديم)
# - النسخة الجديدة (مع تحسينات)

# يجب أن يعمل التطبيق مع كلا النسختين في فترة الانتقال
```

---

## 8) اختبارات قاعدة البيانات والمزامنة

### 8.1 سيناريوهات المزامنة

#### AC-SYNC-001: مزامنة أولية

```gherkin
Given: مستخدم جديد، أول login
When: يكتمل تسجيل الدخول
Then: تبدأ مزامنة العملاء
And: شريط تقدم يظهر
And: العدد المتزايد من العملاء يظهر
And: تكتمل في < 60 ثانية لـ 10,000 عميل
Verification:
  - عدد سجلات `customers` في DB يساوي عدد على الخادم
  - `last_synced_at` محدثة
Status: ⏳
```

#### AC-SYNC-002: Delta Sync

```gherkin
Given: مزامنة أولية مكتملة
When: المستخدم يسحب لتحديث (pull-to-refresh)
Then: تتم مزامنة دلتا (فقط التغييرات منذ آخر مزامنة)
And: تكتمل في < 5 ثوانٍ لـ 100 تغيير
And: التغييرات المحلية (pending payments) لا تُحذف
Verification:
  - HTTP request يحتوي على `since` parameter
  - فقط السجلات الجديدة/المحدثة تأتي
Status: ⏳
```

#### AC-SYNC-003: مزامنة المعاملات المعلقة

```gherkin
Given: 50 معاملة بحالة 'pending' في DB
When: الشبكة تعود وتبدأ المزامنة
Then: المعاملات تُرسل واحدة تلو الأخرى
And: كل معاملة لها idempotency key فريد
And: الحالة تتحول من 'pending' → 'syncing' → 'synced'
And: في حالة فشل، تتحول إلى 'failed' مع reason
And: محاولات الإعادة تتم بـ exponential backoff
Verification:
  - مراقبة DB logs
  - فحص الخادم: 50 معاملة موجودة بـ idempotency keys مختلفة
  - عدم وجود ازدواجية حتى لو أُعيد إرسال نفس المعاملة
Status: ⏳
```

### 8.2 اختبارات قاعدة البيانات

```typescript
// __tests__/db/integrity.test.ts

describe('Database Integrity', () => {
  it('enforces foreign key constraints', async () => {
    // محاولة إضافة دفعة لعميل غير موجود
    await expect(
      database.write(async () => {
        return database.get('payments').create((p) => {
          p.customerId = 'NON_EXISTENT';
          p.amount = 1000;
        });
      })
    ).rejects.toThrow();
  });

  it('handles large datasets efficiently', async () => {
    // إضافة 50,000 عميل
    const start = Date.now();
    await database.write(async () => {
      const customers = [];
      for (let i = 0; i < 50000; i++) {
        customers.push(database.get('customers').prepareCreate((c) => {
          c.serverId = `srv-${i}`;
          c.name = `عميل ${i}`;
          c.accountNumber = String(100000 + i);
        }));
      }
      await database.batch(...customers);
    });
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(10000); // < 10 ثوانٍ
  });

  it('survives app crash mid-transaction', async () => {
    // محاكاة crash أثناء write
    // إعادة الفتح يجب أن يستعيد الحالة الصحيحة
  });
});
```

### 8.3 اختبارات الـ Migrations

```typescript
// __tests__/db/migrations.test.ts

describe('Database Migrations', () => {
  it('migrates from v1 to v2 without data loss', async () => {
    // إنشاء DB بنسخة v1 مع بيانات
    await createDatabaseAt(version: 1, withData: testData);

    // تشغيل migration
    await runMigration({ from: 1, to: 2 });

    // التحقق من سلامة البيانات
    const customers = await database.get('customers').query().fetch();
    expect(customers.length).toBe(testData.customers.length);

    // التحقق من الأعمدة الجديدة موجودة بقيم افتراضية
    customers.forEach((c) => {
      expect(c.metadataNewColumn).toBeDefined();
    });
  });
});
```

---

## 9) اختبارات الطابعة

### 9.1 سيناريوهات الطباعة

| # | السيناريو | النتيجة المتوقعة | الحالة |
|---|---|---|---|
| PRINT-T-01 | الاتصال الأول بطابعة جديدة | جلسة pairing تنجح في < 30s | ⏳ |
| PRINT-T-02 | إعادة الاتصال بطابعة محفوظة | اتصال تلقائي في < 5s | ⏳ |
| PRINT-T-03 | طباعة إيصال عادي | يطبع بدون أخطاء، خط واضح | ⏳ |
| PRINT-T-04 | طباعة QR code | QR يُقرأ بهاتف آخر | ⏳ |
| PRINT-T-05 | طباعة نص عربي (RTL) | الكلمات بالاتجاه الصحيح | ⏳ |
| PRINT-T-06 | طباعة الأرقام الكبيرة | بدون قطع، formatting صحيح | ⏳ |
| PRINT-T-07 | الطابعة بدون ورق | رسالة خطأ واضحة، عدم crash | ⏳ |
| PRINT-T-08 | البطارية ضعيفة في الطابعة | إنذار قبل الطباعة | ⏳ |
| PRINT-T-09 | الجهاز خارج النطاق | timeout بعد 10s + رسالة | ⏳ |
| PRINT-T-10 | طباعة 10 إيصالات متتالية | لا توقف، لا أخطاء | ⏳ |
| PRINT-T-11 | تبديل الطابعة | تحديث الإعدادات + اتصال جديد | ⏳ |
| PRINT-T-12 | إعادة طباعة آخر إيصال | يطبع نسخة طبق الأصل + ختم "نسخة" | ⏳ |

### 9.2 الطابعات المدعومة

> **يجب اختبار كل طابعة من القائمة:**

| الطابعة | البروتوكول | الحالة |
|---|---|---|
| Bixolon SPP-R200III | ESC/POS via Bluetooth | ⏳ |
| Bixolon SPP-R310 | ESC/POS via Bluetooth | ⏳ |
| Bixolon SPP-R410 | ESC/POS via Bluetooth | ⏳ |
| Citizen CMP-30II | ESC/POS via Bluetooth | ⏳ |
| Star Micronics SM-T300i | ESC/POS via Bluetooth | ⏳ |

### 9.3 معايير قبول الطباعة

```yaml
الجودة البصرية:
  - الخط واضح ومقروء على بُعد 30cm
  - لا تشويش أو تداخل في الحروف
  - الأرقام بالحجم الصحيح (يكفي للتدقيق)

التنسيق:
  - الجداول مرتبة (key على اليمين، value على اليسار)
  - الإجمالي بارز (Bold + كبير)
  - QR code يُقرأ من 90% من الأجهزة

السرعة:
  - من ضغط "طباعة" إلى انتهاء التمزيق: < 3 ثوانٍ
  - في حالة Bluetooth عادي: < 5 ثوانٍ
```

---

## 10) معايير قابلية الوصول (a11y)

### 10.1 قائمة فحص a11y

| # | المعيار | المعيار التقني | الحالة |
|---|---|---|---|
| A11Y-01 | كل الأزرار لها `accessibilityLabel` | grep في الكود + اختبار يدوي | ⏳ |
| A11Y-02 | كل النماذج تعمل مع TalkBack | اختبار يدوي + automated | ⏳ |
| A11Y-03 | حجم النص يحترم نظام التشغيل | اختبار مع font scale = 1.3x | ⏳ |
| A11Y-04 | التباين WCAG AA (4.5:1 minimum) | فحص بـ Color Contrast Analyzer | ⏳ |
| A11Y-05 | حجم اللمس >= 48dp | فحص يدوي + automated | ⏳ |
| A11Y-06 | لا اعتماد على اللون فقط | أيقونة + نص + لون معاً | ⏳ |
| A11Y-07 | رسائل الخطأ مرتبطة بحقولها | `accessibilityErrorMessage` | ⏳ |
| A11Y-08 | الترتيب المنطقي للتركيز | اختبار keyboard navigation | ⏳ |
| A11Y-09 | الحركات < 200ms أو يمكن إيقافها | احترام `reduceMotion` | ⏳ |
| A11Y-10 | يعمل في Landscape و Portrait | اختبار يدوي | ⏳ |

### 10.2 اختبار TalkBack

```yaml
المنهجية: قائمة مهام تنفذ بـ TalkBack فقط (شاشة مغطاة)
المشارك: شخص ضعيف بصر متطوع
المهام:
  1. تسجيل الدخول
  2. البحث عن عميل
  3. تنفيذ دفع
  4. طباعة الإيصال
  5. مراجعة تقرير اليوم

معيار النجاح:
  - أنهى 5/5 مهام
  - بدون مساعدة بصرية
  - بدون أخطاء حرجة
```

---

## 11) الجودة الفنية

### 11.1 معايير الكود

| # | المعيار | الأداة | الهدف | الحالة |
|---|---|---|---|---|
| CODE-01 | تغطية الاختبارات | Jest coverage | >= 70% | ⏳ |
| CODE-02 | تغطية اختبارات الميزات الحرجة | Jest coverage | >= 90% (auth, payment) | ⏳ |
| CODE-03 | TypeScript strict mode | tsc --strict | 0 errors | ⏳ |
| CODE-04 | ESLint | eslint . | 0 errors, < 10 warnings | ⏳ |
| CODE-05 | لا `any` types | grep | < 5 occurrences | ⏳ |
| CODE-06 | لا `console.log` في production | grep + lint rule | 0 occurrences | ⏳ |
| CODE-07 | Code complexity | SonarCloud | Cognitive complexity < 15 per function | ⏳ |
| CODE-08 | Code duplication | SonarCloud | < 3% | ⏳ |
| CODE-09 | Technical debt | SonarCloud | < 1 day | ⏳ |
| CODE-10 | تبعيات معروفة الثغرات | npm audit / snyk | 0 high/critical | ⏳ |

### 11.2 معايير التوثيق

| # | المعيار | الحالة |
|---|---|---|
| DOC-01 | README مع setup instructions | ⏳ |
| DOC-02 | Architecture diagram محدث | ⏳ |
| DOC-03 | API documentation (OpenAPI) | ⏳ |
| DOC-04 | Component storybook | ⏳ |
| DOC-05 | ADR (Architecture Decision Records) | ⏳ |
| DOC-06 | Runbook للعمليات الشائعة | ⏳ |
| DOC-07 | Troubleshooting guide | ⏳ |
| DOC-08 | دليل المستخدم بالعربية | ⏳ |
| DOC-09 | دليل التدريب للكاشيرين | ⏳ |

### 11.3 معايير CI/CD

| # | المعيار | الحالة |
|---|---|---|
| CI-01 | CI يعمل على كل PR | ⏳ |
| CI-02 | الاختبارات تُشغل تلقائياً | ⏳ |
| CI-03 | E2E tests تُشغل قبل merge | ⏳ |
| CI-04 | Auto-deploy للـ Internal track | ⏳ |
| CI-05 | Auto-deploy للـ Production track يدوي | ⏳ |
| CI-06 | Release notes تُولد تلقائياً | ⏳ |
| CI-07 | Sentry source maps تُرفع | ⏳ |
| CI-08 | App bundle موقّع | ⏳ |

---

## 12) معايير الموافقة النهائية (Sign-off)

### 12.1 قائمة التحقق النهائية

#### قبل الإطلاق (Pre-Launch)

```markdown
## التطوير
- [ ] كل P0 من Feature Parity مكتمل (19/19)
- [ ] >= 90% من P1 مكتمل (>= 14/15)
- [ ] كل اختبارات unit/integration تمر
- [ ] تغطية الاختبارات >= 70%

## الأمان
- [ ] كل V1-V20 مُعالجة ومُتحقق منها
- [ ] Penetration test مكتمل ولا ثغرات Critical/High
- [ ] OWASP Mobile Top 10 مُغطى
- [ ] Security review من مستشار خارجي

## الأداء
- [ ] كل PERF benchmarks تفي بالهدف
- [ ] حجم APK < 25MB
- [ ] استهلاك RAM ضمن الحدود

## UAT
- [ ] 5+ كاشيرين أكملوا UAT بنجاح
- [ ] SUS Score >= 75
- [ ] NPS >= +30
- [ ] لا blocker bugs مفتوحة

## التوافق
- [ ] العمل على 10+ أجهزة من المصفوفة
- [ ] العمل على Android 7-14
- [ ] العمل على Huawei بدون GMS
- [ ] العمل في landscape + portrait

## a11y
- [ ] WCAG AA مغطاة
- [ ] TalkBack test ناجح
- [ ] حجم اللمس >= 48dp

## DB & Sync
- [ ] AC-SYNC-001/002/003 ناجحة
- [ ] لا فقدان بيانات في 1000+ معاملة test
- [ ] Migrations تعمل بدون فقدان

## الطباعة
- [ ] 5+ طابعات مختبرة
- [ ] لا crashes في حالات الخطأ

## التوثيق
- [ ] README + Architecture + Runbook
- [ ] دليل التدريب بالعربية
- [ ] دليل المستخدم بالعربية

## CI/CD
- [ ] Pipeline يعمل
- [ ] Auto-deploy للـ Internal جاهز
- [ ] Sentry monitoring مفعّل

## التشغيل
- [ ] فريق الدعم مدرّب
- [ ] Runbook للعمليات الشائعة
- [ ] خطة rollback موثقة ومُجربة
- [ ] خطة هجرة البيانات محددة
- [ ] الكاشيرين مدرّبين
```

### 12.2 أصحاب القرار (Approvers)

| الدور | المسؤولية | اسم |
|---|---|---|
| **Product Owner** | الموافقة النهائية على الميزات | _________ |
| **Tech Lead** | الموافقة على الجودة الفنية | _________ |
| **QA Lead** | الموافقة على الاختبارات | _________ |
| **Security Officer** | الموافقة الأمنية | _________ |
| **Operations Manager** | الموافقة على التشغيل | _________ |
| **CEO / Executive Sponsor** | القرار النهائي للإطلاق | _________ |

### 12.3 وثيقة Sign-off

```markdown
# AbbasiyCashiers v2.0 — Release Sign-off

التاريخ: __________
الإصدار: 2.0.0 (Build #_____)

## التأكيد

نحن الموقعون أدناه نؤكد:

1. كل معايير القبول في `08_acceptance_criteria.md` قد تمت
   مراجعتها واستيفاؤها (P0: 100%, P1: ≥90%).

2. لا توجد bugs بمستوى Critical أو High مفتوحة.

3. خطة التراجع موثقة ومُجربة.

4. فريق الدعم والكاشيرين مدربون.

5. الموافقة على الإطلاق الرسمي.

## التوقيعات

Product Owner: __________________ التاريخ: __________
Tech Lead: __________________ التاريخ: __________
QA Lead: __________________ التاريخ: __________
Security: __________________ التاريخ: __________
Operations: __________________ التاريخ: __________
CEO: __________________ التاريخ: __________
```

### 12.4 ما بعد الإطلاق (Post-Launch Monitoring)

```yaml
الأسبوع 1 بعد الإطلاق:
  - مراقبة 24/7 من Sentry/Crashlytics
  - تقرير يومي للإدارة
  - استجابة < 1 ساعة لأي bug حرج

المعايير اليومية:
  - Crash-free users >= 99.5%
  - Crash-free sessions >= 99.7%
  - API success rate >= 98%
  - Payment success rate >= 99.5%
  - Median app start < 2s

في حالة الفشل:
  - تفعيل خطة Rollback المحددة في `07_migration_path.md`
```

---

## 13) ملخص قائمة التحقق الكاملة

### 13.1 الإحصائيات

```
المجموع الإجمالي للمعايير: ~250 معيار قبول

التوزيع:
  Feature Parity:      48 معيار
  Security (V1-V20):   20 معيار
  Performance:         20 معيار
  UAT Scenarios:       15 سيناريو (~75 معيار فرعي)
  Usability:           ~20 معيار
  Compatibility:       10 أجهزة × ~10 معايير = 100 نقطة
  DB & Sync:           ~15 معيار
  Printing:            12 سيناريو
  a11y:                10 معايير
  Code Quality:        10 معايير
  Documentation:       9 معايير
  CI/CD:               8 معايير

الأولويات:
  🔴 P0 Critical:  ~85 معيار (يجب 100%)
  🟠 P1 High:      ~80 معيار (يجب >= 90%)
  🟡 P2 Medium:    ~60 معيار (يجب >= 70%)
  🟢 P3 Low:       ~25 معيار (يجب >= 50%)
```

### 13.2 شعار النجاح

> **"التطبيق الجديد ليس مجرد بديل — إنه ترقية"**
>
> ✅ كل ما يعمله القديم، الجديد يعمله بشكل أفضل
> ✅ كل ثغرة موجودة، مُغلقة في الجديد
> ✅ كل bug معروف، مُصلح ومُغطى باختبار
> ✅ تجربة المستخدم محسّنة بشكل ملموس
> ✅ الأداء أسرع بشكل ملموس
> ✅ الكود قابل للصيانة والتوسعة

---

## 🔗 الترابط مع باقي القسم

- **01_tech_stack_options.md:** التقنيات التي ستُختبر
- **02_recommended_architecture.md:** ما نعتبره "صحيح معمارياً"
- **03_data_models_typescript.md:** schemas نختبر صحتها
- **04_api_client_skeleton.md:** API contracts نختبر التزامها
- **05_security_improvements.md:** V1-V20 نتحقق من إغلاقها
- **06_ui_modernization.md:** تصميم نتحقق من اتباعه
- **07_migration_path.md:** كل phase له milestone في AC

---

## 📚 مراجع

1. **OWASP Mobile Top 10:** https://owasp.org/www-project-mobile-top-10/
2. **WCAG 2.1 Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
3. **System Usability Scale (SUS):** https://www.usability.gov/how-to-and-tools/methods/system-usability-scale.html
4. **Net Promoter Score:** https://www.netpromoter.com/
5. **Google Play Quality Guidelines:** https://developer.android.com/quality
6. **Mobile App Testing Strategy (Atlassian):** https://www.atlassian.com/devops/devops-tools/mobile-app-testing
7. **MobSF (Mobile Security Framework):** https://mobsf.github.io/docs/

---

## 🎯 خاتمة القسم `10_rebuild_blueprint/`

هذا الملف هو **الخاتمة العملية** لـ 8 ملفات في قسم `10_rebuild_blueprint/`:

| # | الملف | المحتوى |
|---|---|---|
| 01 | tech_stack_options.md | اختيار التقنيات (RN+TS+WatermelonDB) |
| 02 | recommended_architecture.md | البنية الـ 4 طبقات |
| 03 | data_models_typescript.md | نماذج Domain/DTO/DB |
| 04 | api_client_skeleton.md | Axios + interceptors + SSL Pinning |
| 05 | security_improvements.md | حل V1-V20 |
| 06 | ui_modernization.md | M3 + Cairo + RTL + a11y |
| 07 | migration_path.md | 8 مراحل في 20 أسبوع |
| **08** | **acceptance_criteria.md** | **كيف نعرف أننا نجحنا** ✅ |

**القسم الآن مكتمل 8/8 = 100% ✅**

> **الخلاصة:** ليس لدينا فقط خطة. لدينا خطة قابلة للقياس والتحقق.
> كل قرار موثق. كل مخاطرة محسوبة. كل ميزة لها معيار قبول.
> هذا ما يعنيه **Engineering-Grade Analysis**. 🎯
