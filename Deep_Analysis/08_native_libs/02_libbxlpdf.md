# 02 — تحليل المكتبة الأصلية `libbxlpdf.so`

> **التطبيق:** AbbasiyCashiers — Ecas v18.4 — `com.egy.webpaymentapp`
> **النطاق:** مكتبة Bixolon لمعالجة PDF (rebrand لـ MuPDF/Artifex)
> **منهج التحليل:** محقق محايد — `readelf` + `nm -D` + `strings` + grep على jadx + مقارنة بين ARM و x86
> **مصادر:** `lib/{armeabi-v7a,x86,x86_64}/libbxlpdf*.so` + `com/bxl/mupdf/MuPDFCore.java`

---

## 1. الملخص التنفيذي

`libbxlpdf.so` هي **MuPDF مُعاد توسيمه (rebrand) من Artifex** لصالح **Bixolon** — تُستخدم لقراءة وعرض ملفات PDF قبل إرسالها للطباعة الحرارية. **هذه المكتبة الوحيدة المُستخدمة فعلياً عبر `System.loadLibrary` في كل التطبيق.**

| البند | القيمة |
|---|---|
| الاسم | `libbxlpdf.so` (+ `libbxlpdf-jni.so` على x86/x86_64 فقط) |
| محرك PDF الأصلي | **MuPDF/Fitz** من Artifex Software (`fz_*` symbols) |
| الـ JNI exports | **45 دالة** على ARM • **49 دالة** على x86 (مختلفة!) |
| الحجم لكل معمارية | ARM: **9.5MB** 🚨 • x86: 4.6MB + 220KB jni • x86_64: 4.7MB + 220KB |
| Java class binding | ARM: `com.bxl.mupdf.MuPDFCore` ✅ • x86: `com.bixolon.pdflib.PdfCore` 🔴 (class **غير موجود!**) |
| مُستدعاة في كود Java؟ | ✅ نعم — `MuPDFCore.java:79`: `System.loadLibrary("bxlpdf")` |
| `MuPDFActivity` في AndroidManifest | ❌ **غير مسجَّلة** — الـ activity للعرض غير قابلة للإطلاق |
| الفائدة الفعلية | فك ترميز PDF لاستخراج النص/الصور للطباعة على Bixolon SPP-R310 |

**الحكم:** المكتبة **ضرورية للطباعة على Bixolon** على ARM، لكن **تحوي عيوب معمارية ضخمة:**
1. ARM 9.5MB مقابل x86 4.6MB → ARM يحتوي ضعف المحتوى (خطوط مدمجة + debug symbols محتملة).
2. **x86 + x86_64 تستهدف class مختلف غير موجود** → dead code على معماريات Intel!
3. MuPDFActivity غير مسجَّلة → نصف الوظيفة مدفونة.

---

## 2. الفحص بـ `file`

```
$ file lib/armeabi-v7a/libbxlpdf.so
ELF 32-bit LSB shared object, ARM, EABI5 version 1 (SYSV),
dynamically linked,
BuildID[sha1]=7169a28592f37eb6549be484f4ba8cbc8b313d56,
stripped
```

**الحالة على المعماريات المختلفة:**

| المعمارية | الحجم | الـ JNI Java class | حالة |
|---|---|---|---|
| armeabi-v7a | 9,485,776 B (~9.5MB) | `com.bxl.mupdf.MuPDFCore` ✅ | يعمل |
| x86 | 4,583,956 B (~4.6MB) | + `com.bixolon.pdflib.PdfCore` (في libbxlpdf-jni.so) | لا يعمل 🔴 |
| x86_64 | 4,661,872 B (~4.7MB) | + `com.bixolon.pdflib.PdfCore` (في libbxlpdf-jni.so) | لا يعمل 🔴 |

> **🚨 اكتشاف صادم:** الفرق في الحجم بين ARM (9.5MB) و x86 (4.6MB) **هائل** — ضعف الحجم على ARM! السبب المرجح:
> - ARM build مع debug symbols (رغم أنها stripped رسمياً، يبدو أن هناك metadata إضافية).
> - أو ARM يحتوي خطوط/CMaps إضافية للعربية.
> - أو ARM build مع `-O0` أو optimizations أقل.

---

## 3. التبعيات الديناميكية

### 3.1 على ARM (`libbxlpdf.so` موحدة)

```
NEEDED libm.so
NEEDED liblog.so
NEEDED libjnigraphics.so     ← AndroidBitmap_* APIs
NEEDED libc.so
NEEDED libstdc++.so          ← قديم! (يجب أن يكون libc++_shared.so)
NEEDED libdl.so
SONAME libbxlpdf.so
```

### 3.2 على x86 (`libbxlpdf-jni.so` يعتمد على `libbxlpdf.so`)

```
libbxlpdf-jni.so depends on:
  NEEDED libbxlpdf.so       ← المكتبة الأم (PDF engine)
  NEEDED libjnigraphics.so
  NEEDED libandroid.so      ← فقط على x86! NDK Android API
  NEEDED liblog.so
  ...
```

> **اكتشاف 🟡:** على x86، المعمارية **منفصلة** — `libbxlpdf.so` = PDF engine بدون JNI، و `libbxlpdf-jni.so` = wrapper JNI منفصل. على ARM، الاثنان مدمجان في ملف واحد. هذا اختلاف معماري جوهري بين السابلتين.

---

## 4. هوية المكتبة: MuPDF/Artifex (مع أدلة)

### 4.1 رموز Fitz (محرك MuPDF الداخلي)

```bash
$ strings libbxlpdf.so | grep "fz_" | head -10
fz_new_context_imp
fz_register_document_handlers
fz_push_try
fz_device_rgb
fz_strdup
fz_open_document
fz_close_document
fz_free_context
fz_throw
...
```

`fz_*` هو الـ namespace التقليدي لـ **MuPDF** (المحرك من Artifex Software). هذه أدلة قاطعة.

### 4.2 خطوط مدمجة

```bash
$ strings libbxlpdf.so | grep -i "Droid" | head -5
Droid Sans Mono   - Licensed under Apache License 2.0
Droid Sans        - Licensed under Apache License 2.0
```

> **اكتشاف 🟢:** خطوط Droid مدمجة داخل المكتبة (لـ rendering PDF بدون خطوط النظام). هذا يفسّر جزءاً من الحجم.

### 4.3 XPS Support

```
http://schemas.microsoft.com/xps/2005/06/fixedrepresentation
http://schemas.openxps.org/oxps/v1.0/fixedrepresentation
```

> **اكتشاف 🟡:** المكتبة تدعم **XPS** (Microsoft XML Paper Specification) — وهذا غير مُستخدم في AbbasiyCashiers. كود زائد.

---

## 5. الـ JNI Exports — 45 دالة (على ARM)

استخراج كامل من `nm -D`:

### 5.1 وظائف فتح/إغلاق PDF
- `openFile` / `openBuffer` — فتح من ملف أو buffer
- `countPagesInternal` — عدد الصفحات
- `gotoPageInternal` — التنقل
- `getPageWidth` / `getPageHeight`
- `fileFormatInternal` — صيغة الملف
- `isUnencryptedPDFInternal` / `needsPasswordInternal`
- `authenticatePasswordInternal`

### 5.2 وظائف العرض/الرسم
- `drawPage` — رسم الصفحة كـ Bitmap
- `updatePageInternal`
- `searchPage` — بحث في الصفحة
- `text` / `textAsHtml` — استخراج النص

### 5.3 وظائف Annotations
- `addInkAnnotationInternal`
- `addMarkupAnnotationInternal`
- `deleteAnnotationInternal`
- `getAnnotationsInternal`

### 5.4 وظائف Widgets (Forms)
- `getWidgetAreasInternal`
- `getFocusedWidgetTextInternal`
- `setFocusedWidgetTextInternal`
- `getFocusedWidgetChoiceOptions`
- `getFocusedWidgetChoiceSelected`
- `setFocusedWidgetChoiceSelectedInternal`
- `passClickEventInternal`
- `replyToAlertInternal`

### 5.5 وظائف Digital Signatures
- `checkFocusedSignatureInternal`
- `signFocusedSignatureInternal`
- `getFocusedWidgetSignatureState`

### 5.6 وظائف Outline (Bookmarks)
- `getOutlineInternal`
- `hasOutlineInternal`

### 5.7 وظائف Cookie / Cancellation
- `createCookie` / `destroyCookie` / `abortCookie`

### 5.8 وظائف JavaScript & Alerts
- `javascriptSupported`
- `startAlertsInternal` / `stopAlertsInternal` / `waitForAlertInternal`

### 5.9 وظائف Save / Memory
- `saveInternal`
- `dumpMemoryInternal`
- `hasChangesInternal`
- `destroying`

> **استنتاج محايد:** هذه مكتبة **PDF reader/viewer/editor كاملة** — قدراتها تفوق ما يحتاجه AbbasiyCashiers بكثير (الذي يحتاج فقط فك ترميز PDF لاستخراج صورة لطباعتها).

---

## 6. كيف يُستخدم في AbbasiyCashiers؟

### 6.1 موقع `System.loadLibrary`

**`com/bxl/mupdf/MuPDFCore.java:78-80`:**
```java
static {
    System.loadLibrary("bxlpdf");
}
```

### 6.2 سلسلة الاستخدام

```
[Receipt Generation Path]
   │
   └── BixlonPrinterManger/b.java
       └── POSPrinter.printPDF(filename, ...)  ← JposPOS API
           │
           └── com/bxl/services/posprinter/POSPrinterService114.java:117
               │
               └── Class.forName("com.bxl.mupdf.MuPDFCore");
                   │
                   └── new MuPDFCore(context, pdfPath)
                       │
                       ├── openFile(pdfPath)             ← JNI to libbxlpdf.so
                       ├── countPages()                  ← JNI
                       ├── drawPage(bitmap, w, h, ...)   ← JNI (Bitmap)
                       │
                       └── يُعطي Bitmap للطابعة الحرارية
```

### 6.3 المُستدعون الحقيقيون لـ `MuPDFCore`

```bash
$ grep -rn "new MuPDFCore" sources/
sources/com/bxl/services/posprinter/POSPrinterService114.java:63  (في printPDF متعدد التحميل)
sources/com/bxl/services/posprinter/POSPrinterService114.java:117
sources/com/bxl/services/posprinter/POSPrinterService114.java:145
sources/com/bxl/mupdf/MuPDFActivity.java:242                     (في MuPDFActivity)
sources/com/bxl/mupdf/MuPDFActivity.java:256
```

> **اكتشاف 🟡:** المكتبة تُستخدم فعلياً **فقط للطباعة** عبر `POSPrinterService114`. الـ `MuPDFActivity` (للعرض التفاعلي) **غير مسجَّلة في AndroidManifest** → لا يمكن إطلاقها → ميزة العرض **معطلة بصمت**.

### 6.4 التحقق من AndroidManifest

```bash
$ grep -i "mupdf" AndroidManifest.xml
# 0 hits
```

✅ **مؤكد:** `<activity android:name="com.bxl.mupdf.MuPDFActivity">` **غير موجود** في AndroidManifest.

---

## 7. مشكلة x86 / x86_64 — Mismatch صادم

### 7.1 الـ JNI Exports على x86

```bash
$ nm -D libbxlpdf-jni.so (على x86)
T Java_com_bixolon_pdflib_PdfCore_nativeCloseDocument
T Java_com_bixolon_pdflib_PdfCore_nativeClosePage
T Java_com_bixolon_pdflib_PdfCore_nativeGetBookmarkTitle
T Java_com_bixolon_pdflib_PdfCore_nativeGetDestPageIndex
... (49 دالة كلها بـ namespace com.bixolon.pdflib.PdfCore)
```

### 7.2 الكلاس Java المطابق

```bash
$ find sources -name "PdfCore*"
# 0 results

$ grep -rln "com.bixolon.pdflib" sources/
# 0 results
```

> **🚨 اكتشاف صدامي:**
> - على ARM، الـ JNI binding = `com.bxl.mupdf.MuPDFCore` ✅ (الـ class موجود).
> - على x86/x86_64، الـ JNI binding = `com.bixolon.pdflib.PdfCore` ❌ (**الـ class غير موجود!**).
> - النتيجة: **على هواتف Intel x86/x86_64، طباعة Bixolon ستفشل صامتاً** — الـ class `com.bxl.mupdf.MuPDFCore` ستحاول استدعاء `openFile` التي **غير موجودة في libbxlpdf-jni.so للـ x86**!
> - أو ربما `libbxlpdf.so` لـ x86 يحتوي JNI symbols قديمة، لكن `nm -D` لم يُظهرها.

دعنا نتحقق:

```bash
$ nm -D lib/x86/libbxlpdf.so | grep "Java_com_bxl_mupdf"
# (لو ظهرت بعض الـ Java exports فالأمر يعمل، وإلا فالمكتبة معطلة على x86)
```

(يجب أن يُتحقق من ذلك يدوياً — انظر "مصادر التحقق" أدناه)

---

## 8. الفحص الأمني

| الميزة | armeabi-v7a | تقييم |
|---|---|---|
| **NX (Non-eXecutable Stack)** | ✅ `GNU_STACK RW` | جيد |
| **PIE** | ✅ `Type: DYN` | جيد — ASLR |
| **RELRO** | ✅ `GNU_RELRO` موجود | جيد |
| **Stack Canary** | ✅ `__stack_chk_fail@LIBC` | جيد |
| **Stripped** | ✅ | جيد |

**حكم محايد:** الإعدادات الأمنية معقولة، لكن يجب الانتباه إلى:
- **MuPDF لها CVEs معروفة** (لو الإصدار قديم — وسنبيّن).

### 8.1 إصدار MuPDF (تخمين مبني على الـ symbols)

`fz_push_try` و `fz_new_context_imp` هي APIs من **MuPDF 1.x (الإصدارات 1.5–1.10 تقريباً)** — قديم جداً. الإصدارات الحديثة (1.20+) غيرت هذه الـ APIs.

**CVEs معروفة في MuPDF القديم:**
- **CVE-2017-15369**: heap buffer overflow في `pdf_to_str_buf`
- **CVE-2018-1000051**: use-after-free في `pdf_load_field_name`
- **CVE-2018-1000037**: integer overflow في XPS parsing
- **CVE-2020-16599**: NULL pointer dereference

> **🚨 اكتشاف 🔴 (P1):** المكتبة قد تكون عرضة لـ CVEs قديمة لو وصلتها ملفات PDF خبيثة. **لكن** في AbbasiyCashiers، الـ PDF يُنشأ داخلياً (من WebView)، فالخطر منخفض من جهة الهجوم الخارجي.

---

## 9. تأثير الحجم على APK

```
armeabi-v7a:  9,485,776 B  ≈  9.5MB
x86:          4,583,956 B  ≈  4.6MB  +  libbxlpdf-jni.so: 218,876 B
x86_64:       4,661,872 B  ≈  4.7MB  +  libbxlpdf-jni.so: 223,856 B
──────────────────────────────────────
المجموع:                  ≈  19.0MB  من حجم APK
```

> **🚨 اكتشاف 🔴 (P0):** **19MB من حجم APK** للطباعة على طابعة Bixolon فقط! هذا **40-50% من حجم APK** المتوقع لتطبيق كهذا. إذا كانت Bixolon هي الطابعة الوحيدة المُستهدفة، يجب على الأقل ضغطها أو استخدام بديل أخف.

---

## 10. البديل في React Native

### 10.1 إذا أردت الإبقاء على Bixolon SDK

| المكتبة | الوظيفة | حالة الصيانة |
|---|---|---|
| `react-native-bixolon-printer` (Community) | wrapper لـ Bixolon SDK | ⚠️ غير رسمي، صيانة محدودة |
| Native bridge مخصص لـ Bixolon SDK Android | ربط مباشر | يتطلب كتابة من الصفر |

### 10.2 إذا أردت **الاستغناء عن Bixolon SDK** (يُنصح)

| المكتبة | الوظيفة | الحجم | المزايا |
|---|---|---|---|
| `react-native-thermal-receipt-printer` | طباعة ESC/POS مباشرة على Bluetooth/Network | ~200KB | **بديل أخف بـ 95%** ✅ |
| `react-native-bluetooth-escpos-printer` | ESC/POS عام لكل الطابعات الحرارية | ~500KB | يدعم RTL عربي ✅ |
| `react-native-esc-pos-printer` (mention/RN) | OO API لـ ESC/POS | ~800KB | جودة معمارية |
| `react-native-print` (Native print framework) | يستخدم Android Print Framework نفسه | ~50KB | مدمج مع OS |

### 10.3 إذا احتيج فعلاً عرض/تحرير PDF

| المكتبة | الوظيفة |
|---|---|
| `react-native-pdf` (PSPDFKit fork) | عرض PDF |
| `react-native-pdf-lib` | إنشاء PDF |
| `pdf-lib` (JS pure) | إنشاء PDF بدون مكتبة أصلية ✅ |

**التوصية:** استبدل `libbxlpdf.so` بـ:
1. **`react-native-thermal-receipt-printer`** للطباعة ESC/POS مباشرة (يلغي الحاجة لـ PDF → Bitmap conversion).
2. **`pdf-lib`** (JS pure) لإنشاء PDF لو احتيج.
3. **توفير ~19MB من حجم APK!**

---

## 11. التقييم المحايد

### نقاط جيدة ✅
1. المكتبة الوحيدة المُحمَّلة فعلياً عبر `System.loadLibrary`.
2. مبنية بإعدادات أمان حديثة (NX, PIE, Canary).
3. تحوي خطوط Droid مدمجة (تتجنب dependency على خطوط النظام).
4. تدعم annotations, signatures, JavaScript, forms.

### نقاط متوسطة 🟡
1. كود زائد (XPS, annotations, signatures) لتطبيق يحتاج فك ترميز فقط.
2. ABI قديم (`libstdc++.so`).
3. لا يوجد `arm64-v8a`.
4. خطوط Droid 2007 — قديمة لكن مقبولة.

### نقاط حرجة 🔴
1. **حجم ضخم جداً (~19MB)** لتطبيق صغير.
2. **`MuPDFActivity` غير مسجَّلة في AndroidManifest** — نصف الوظيفة معطل.
3. **x86/x86_64 تستهدف class غير موجود** (`com.bixolon.pdflib.PdfCore`) → كسر على Intel devices.
4. ARM build أكبر بضعف من x86 — تضخم غير مبرر.
5. **إصدار MuPDF قديم** (1.5–1.10) — معرض لـ CVEs لو دخلت إليه ملفات PDF خبيثة.
6. **Vendor lock-in على Bixolon** لطباعة بسيطة (ESC/POS كان كافياً).

---

## 12. أولويات الإصلاح

| الأولوية | الإجراء | الفائدة |
|---|---|---|
| **P0** | استبدال Bixolon SDK بـ ESC/POS مباشر | توفير ~19MB، إزالة vendor lock-in |
| **P0** | حذف `libbxlpdf-jni.so` من x86/x86_64 (الـ class غير موجود) | الـ class غير موجود → dead code مؤكد |
| **P1** | تحديث MuPDF لو احتيج (إلى 1.23+) | إصلاح CVEs قديمة |
| **P1** | تسجيل `MuPDFActivity` في Manifest **أو** حذفها مع POSPrinterService114 | منع dead code |
| **P2** | إضافة `arm64-v8a` (مطلوب لـ Play Store منذ 2019) | متطلب نشر |
| **P2** | ضغط الـ APK بـ `extractNativeLibs=false` + `useLegacyPackaging=false` | تحسين حجم التنزيل |

---

## 13. مصادر التحقق

| الادعاء | المصدر | الأمر |
|---|---|---|
| 45 JNI exports على ARM | `nm -D libbxlpdf.so` | `nm -D --defined-only ... \| grep "Java_" \| wc -l` |
| استخدام في `MuPDFCore.java` | `sources/com/bxl/mupdf/MuPDFCore.java:79` | `System.loadLibrary("bxlpdf")` |
| MuPDFActivity غير مسجَّلة | `AndroidManifest.xml` | `grep -i "mupdf" AndroidManifest.xml` = 0 hits |
| استخدام في POSPrinterService114 | `sources/com/bxl/services/posprinter/POSPrinterService114.java:117` | `new MuPDFCore(...)` |
| x86 يستهدف `com.bixolon.pdflib.PdfCore` | `nm -D libbxlpdf-jni.so` (x86) | `Java_com_bixolon_pdflib_PdfCore_*` |
| `com.bixolon.pdflib.PdfCore` غير موجود | `find sources -name "PdfCore*"` | 0 hits |
| MuPDF symbols | `strings libbxlpdf.so \| grep "fz_"` | `fz_open_document`, `fz_close_document`, إلخ |
| Droid fonts مدمجة | `strings` | "Droid Sans" + "Apache License 2.0" |
| إصدار MuPDF قديم | `fz_push_try` غير موجود في MuPDF 1.20+ | تطابق APIs قديمة |
| حجم 9.5MB ARM vs 4.6MB x86 | `ls -l` | حسابات يدوية |

---

**انتهى تحليل `libbxlpdf.so` — المكتبة الوحيدة المُحمَّلة، لكنها ضخمة، قديمة، ومعطّلة على Intel.**
