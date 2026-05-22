# 01.1 — الملخص التنفيذي (Executive Summary)

> **الجمهور:** مدير المنتج، صاحب القرار التقني، المهندس المعماري.
> **زمن القراءة:** ~7 دقائق.

---

## ما هو هذا التطبيق؟

`AbbasiyCashiers` (الاسم الفني الداخلي: **Ecas v18.4**) هو تطبيق Android خاص يُستخدم من قِبَل **محصّلي ميدان** في اليمن لـ:

1. **تحصيل المدفوعات النقدية** من المشتركين (كهرباء/مياه/خدمة عامة) في الموقع.
2. **قراءة عدّادات الخدمة** (مع تصوير العدّاد).
3. **تحديث الموقع الجغرافي للمشترك** (GPS).
4. **طباعة سند تحصيل حراري** فوري عبر طابعة Bluetooth (Bixolon).
5. **مشاركة السند** كـ PDF عبر تطبيقات أخرى (WhatsApp/البريد/…).

التطبيق يخدم نموذج العمل الكلاسيكي للمكاتب الفرعية في اليمن: محصّل يطوف على الزبائن، يجمع، يطبع إيصالاً، ويرفع الإيصال إلى السيرفر المركزي.

---

## لماذا نعيد بناءه؟

النسخة الحالية تعاني من **ست مشكلات حرجة** تجعل صيانتها وتطويرها مكلِفاً وغير آمن:

### 1. بنية معمارية قديمة (WebView Wrapper من 2016 تقريباً)
- التطبيق ليس تطبيقاً Native حقيقياً ولا React Native ولا Flutter.
- هو قشرة Android رفيعة (~6 شاشات Native) تعرض **صفحات HTML/JS مُموَّهة** عبر `WebView`.
- صفحات HTML تستخدم Bootstrap 4.5.3 + jQuery 3.0.0 (إصدارات قديمة جداً).
- الـ JS مكتوب بنمط **string-array obfuscation** (مثل `_$_fNNN = ["\x68\x65\x6c\x6c\x6f"]`) — صعب التعديل، سهل الكسر.

### 2. ثغرات أمنية واضحة (مذكورة في `../AbbasiyCashiers_RE_Analysis/07_report/FINAL_REPORT.md`)
- **شهادة SSL self-signed مع `TrustManager` فارغ** ⇒ MITM ممكن.
- **HostnameVerifier يُعيد `true` دائماً** ⇒ أي خادم يقبل بأنه `abbasiy.yedns.org`.
- **مفتاح DESede مزروع بالكود** (`m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##`) ⇒ يستطيع أي مهاجم تشفير/فك deeplinks.
- **WebView يفعّل `setAllowUniversalAccessFromFileURLs(true)`** ⇒ خطر XSS-to-Native.
- **JS Bridge مكشوف** ⇒ أي صفحة HTML تستطيع استدعاء `window.mobile.*`.
- **Magic Backdoor** ⇒ اسم=`1`, كلمة=`1`, كود=`1` ⇒ يفتح إعدادات النظام بدون مصادقة.

### 3. الواجهة قديمة وغير متجاوبة
- التصميم بـ Bootstrap 4 + jQuery — لا يدعم Dark Mode، RTL ضعيف.
- لا توجد Animations حديثة، لا Skeleton screens، لا Pull-to-refresh ناعم.
- خطوط ASMO 449 قديمة في بعض الترويسات (`B'&E) 'DB1'!* …`) بدلاً من UTF-8.

### 4. الكود مُموَّه ولا يمكن صيانته
- الـ Java مُعاد التسمية (`a.java`, `b.java`, `c0.java`, …) — بمجموع 62 ملف.
- الـ HTML/JS مشفّرة بـ `unescape('%XX...')` — لا أحد يستطيع تعديلها بسهولة.

### 5. التبعيات قديمة
- `volley` للـ HTTP (Google توقّفت عن دعمه منذ 2017).
- `Gson` بدلاً من Kotlinx Serialization / Moshi.
- `Bixolon` SDK قديم مدمج في الـ APK كـ unknownFiles.
- `OpenCV` مدمج لكنه (احتمالاً) لا يُستخدم فعلياً.

### 6. لا يوجد اختبار آلي ولا CI/CD
- ولا اختبار Unit ولا Instrumented.
- البناء يدوي عبر `apktool` للتغييرات السريعة.

---

## ماذا يعمل التطبيق حالياً؟ (ما يجب الحفاظ عليه)

رغم العيوب، **القيمة الجوهرية** للتطبيق واضحة:

| الوظيفة | الحالة | يجب الحفاظ عليها؟ |
|---|---|---|
| تسجيل دخول بـ (فرع + اسم + كلمة) | تعمل | ✅ نعم — نموذج عمل |
| 3 صلاحيات أساسية (دفع/قراءة/موقع) | تعمل | ✅ نعم |
| طباعة إيصال حراري Bluetooth | تعمل | ✅ نعم — أساسي |
| سند تحصيل بصيغة العربية + تحويل الرقم لكلمات | تعمل | ✅ نعم — جوهر |
| دعم العملة (ريال + فلس) | تعمل | ✅ نعم |
| تصوير العدّاد ورفعه Base64 | تعمل | ✅ نعم |
| GPS لتحديث الموقع | تعمل | ✅ نعم |
| Deeplink لتغيير IP الخادم | تعمل | ⚠️ نعم لكن بأمان |
| مشاركة الإيصال كـ PDF | تعمل | ✅ نعم |
| البحث في القائمة | تعمل | ✅ نعم |

**الخلاصة:** كل الوظائف يجب الحفاظ عليها. ما يحتاج إعادة هو **البنية، الأمان، الواجهة، والـ Stack التقني**.

---

## أرقام رئيسية

| المعيار | الرقم |
|---|---|
| إصدار التطبيق | Ecas v18.4 (versionCode=18) |
| الحد الأدنى لـ Android | API 19 (Android 4.4 KitKat) — قديم جداً |
| الحد المستهدف | API 32 (Android 12) |
| حجم APK تقريباً | ~10-15 MB |
| المعمارية الأصلية | armeabi-v7a, x86, x86_64 |
| اللغة الأصلية للكود | Java (مُموَّه بواسطة ProGuard) |
| Activities Native | 6 (Login, Main, Operations, ChangePass, WebView, ScanPrinter) |
| Activities + Settings_Printer | 7 |
| Anonymous helper classes | ~50 (a.java حتى h0.java) |
| API endpoints | 9 |
| JS Bridge methods | 6 |
| Gson Models | 7 (3 named + 4 inner) |
| HTML pages | 4 (3 functional + 1 error page) |
| JS files (deobfuscated) | 4 |
| CSS files | 3 |
| String resources | 192 string × 117 lang variant |
| Layout XML files | 131 |
| Drawable assets | 485 |
| Permissions في Manifest | 30+ (مبالغة، تشمل ACCESS_SUPERUSER!) |

---

## التوصية المختصرة

| البديل | الحُكم |
|---|---|
| 🟢 **React Native + TypeScript + Expo (Bare)** | **مُوصى به بقوة** — يطابق Stack الفريق (app1) ويوفر تشاركاً معرفياً |
| 🟢 Flutter + Dart | ممكن، لكن يُجبر فريقاً جديداً |
| 🟡 Kotlin Native + Jetpack Compose | ممكن لو الفريق Android فقط |
| 🔴 إصلاح النسخة الحالية | غير مُجدٍ — التموية + الأمان + الـ Stack القديم تجعله أغلى من إعادة البناء |

**خطة بناء مُقترحة:** Phase 1 (6 أسابيع) لشاشة Login + Main + Operations + API client + Printer + Receipt. Phase 2 (3 أسابيع) لـ WebView replacement + Deeplink آمن. Phase 3 (2 أسبوع) للاختبار الميداني.

> **التفاصيل الكاملة لخطة إعادة البناء في:** [`10_rebuild_blueprint/`](../10_rebuild_blueprint/)

---

**التالي:** [`02_architecture_diagram.md`](02_architecture_diagram.md) — مخطط البنية المعمارية الحالية.
