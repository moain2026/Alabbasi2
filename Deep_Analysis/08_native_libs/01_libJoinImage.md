# 01 — تحليل المكتبة الأصلية `libJoinImage.so`

> **التطبيق:** AbbasiyCashiers — Ecas v18.4 — `com.egy.webpaymentapp`
> **النطاق:** مكتبة أصلية (.so) — معالجة الصور للـ OCR/CID
> **منهج التحليل:** محقق محايد — `readelf` + `nm -D` + `strings` + `file` + grep على jadx
> **مصدر الـ APK:** `AbbasiyCashiers_RE_Analysis/02_apktool_output/AbbasiyCashiers/lib/`

---

## 1. الملخص التنفيذي (الخلاصة الصادمة قبل التفاصيل)

🚨 **اكتشاف صدامي:** هذه المكتبة **dead weight** — موجودة في APK لكن **غير مُستدعاة في أي مكان** في الكود.

| البند | القيمة |
|---|---|
| الاسم | `libJoinImage.so` |
| الـ package المستهدف في JNI | `cn.pda.serialport.JoinImage` |
| عدد الـ JNI exports | **18 دالة** (`analyseImg`, `binarization`, `dilation`, `erosion`, `filling`, `getSplitImg`, إلخ) |
| الحجم لكل معمارية | armeabi-v7a: 30,364 B ≈ **30KB** • x86: 30,252 B • x86_64: 34,960 B |
| **مُستدعاة في كود Java؟** | ❌ **لا — صفر مرجع** |
| `System.loadLibrary("JoinImage")` | ❌ **غير موجود** |
| `import cn.pda.serialport.JoinImage` | ❌ **غير موجود** |
| `Class.forName(...JoinImage)` | ❌ **غير موجود** |
| الفائدة الفعلية | **صفر** — يمكن حذفها بدون أي تأثير وظيفي |
| تأثيرها على حجم APK | +90KB لثلاث معماريات (~30KB لكل واحدة) |

**الحكم:** هذه مكتبة **مأخوذة من SDK لجهاز PDA صيني** (الاسم `cn.pda.*` يكشف ذلك) — وُضعت في المشروع ربما لاختبار سابق، ثم نُسيت في الـ APK النهائي. **يمكن وستجب إزالتها**.

---

## 2. الفحص بـ `file`

```
$ file lib/armeabi-v7a/libJoinImage.so
ELF 32-bit LSB shared object, ARM, EABI5 version 1 (SYSV),
dynamically linked,
BuildID[sha1]=f07b497c04e7c93b5effb668293554df39de4b9d,
stripped
```

**ملاحظات:**
- ✅ ELF 32-bit ARM — معمارية صحيحة لـ armeabi-v7a.
- ✅ **stripped** — لا توجد رموز debug → صعب reverse engineering.
- ✅ BuildID موجود → يمكن المطابقة مع أي مصدر مفتوح لو وُجد.
- ✅ Dynamic linking → يعتمد على libc/libm/libstdc++.

---

## 3. التبعيات الديناميكية (`readelf -d`)

```
NEEDED libdl.so          ← Dynamic loading
NEEDED liblog.so         ← Android __android_log_print
NEEDED libjnigraphics.so ← AndroidBitmap_* APIs (Android Bitmap NDK)
NEEDED libc.so           ← C standard library
NEEDED libm.so           ← Math library
NEEDED libstdc++.so      ← C++ ABI helpers
SONAME libJoinImage.so
```

**استنتاجات محايدة:**
- ✅ `libjnigraphics.so` → المكتبة تتعامل مباشرة مع Bitmap Android عبر NDK.
- 🟡 `libstdc++.so` (وليس `libc++_shared.so`) → ABI قديم — مكتبة قديمة الباني (NDK r10 وأقدم).
- ✅ Flags: `BIND_NOW` + `NOW` → eager binding (أمان أفضل ضد lazy resolver attacks).

---

## 4. الـ JNI Exports — 18 دالة لمعالجة الصور

استخراج كامل عبر `nm -D --defined-only`:

| الدالة JNI | الدلالة المُحتملة |
|---|---|
| `Java_cn_pda_serialport_JoinImage_analyseImg` | تحليل الصورة بالكامل |
| `Java_cn_pda_serialport_JoinImage_binarization` | تحويل الصورة إلى ثنائية (أبيض/أسود) |
| `Java_cn_pda_serialport_JoinImage_binarization2` | نسخة ثانية من التحويل الثنائي |
| `Java_cn_pda_serialport_JoinImage_binaryCid` | تحويل ثنائي لـ CID (China Citizen ID?) |
| `Java_cn_pda_serialport_JoinImage_dilation` | عملية Dilation (توسعة) — Morphology |
| `Java_cn_pda_serialport_JoinImage_erosion` | عملية Erosion (تآكل) — Morphology |
| `Java_cn_pda_serialport_JoinImage_filling` | ملء الفراغات في الصورة |
| `Java_cn_pda_serialport_JoinImage_getSplitImg` | الحصول على صورة مُجزَّأة |
| `Java_cn_pda_serialport_JoinImage_getSplitImgH` | ارتفاع الجزء |
| `Java_cn_pda_serialport_JoinImage_getSplitImgW` | عرض الجزء |
| `Java_cn_pda_serialport_JoinImage_getSplitNum` | عدد الأجزاء |
| `Java_cn_pda_serialport_JoinImage_imgToGray` | تحويل لصورة رمادية |
| `Java_cn_pda_serialport_JoinImage_locateCid` | تحديد موقع CID في الصورة |
| `Java_cn_pda_serialport_JoinImage_parseBitmap` | تحليل Bitmap |
| `Java_cn_pda_serialport_JoinImage_split` | تجزئة الصورة |
| `Java_cn_pda_serialport_JoinImage_stretch` | تمديد/تطبيع الصورة |
| `Java_cn_pda_serialport_JoinImage_thinning` | عملية Thinning (تنحيف) — Skeletonization |
| `Java_cn_pda_serialport_JoinImage_thinning2` | نسخة ثانية من التنحيف |
| `ARGB` | دالة مساعدة لمعالجة ألوان ARGB |

**استنتاج تقني:** هذه مكتبة **OCR كاملة لقراءة بطاقة الهوية الصينية (CID)** — وظيفتها استخراج النص من صورة بطاقة هوية:
1. `imgToGray` → تحويل إلى رمادي.
2. `binarization` → تحويل إلى ثنائي.
3. `erosion` / `dilation` / `filling` / `thinning` → معالجة Morphology.
4. `locateCid` / `binaryCid` → تحديد منطقة رقم الهوية.
5. `split` / `getSplitImg` → تجزئة كل رقم في صورة مستقلة.
6. `analyseImg` / `parseBitmap` → التحليل النهائي.

---

## 5. **الأهم: هل تُستخدم؟** (بحث grep)

### 5.1 بحث `loadLibrary`

```bash
$ grep -rn "loadLibrary" com/egy/webpaymentapp/ com/
```

**نتيجة:**
```
sources/com/bxl/mupdf/MuPDFCore.java:79:    System.loadLibrary("bxlpdf");
```

**فقط `bxlpdf` يتم تحميله!** `libJoinImage` غير محمَّل أبداً.

### 5.2 بحث `import` / package

```bash
$ grep -rln "cn.pda\|cn/pda\|JoinImage" sources/
```

**نتيجة:** ❌ **0 hits** — لا مرجع واحد في الـ jadx output.

### 5.3 بحث `Class.forName`

```bash
$ grep -rn "Class.forName" sources/com/egy/
```

**نتيجة:** لا مرجع لـ JoinImage.

> **🚨 الخلاصة المؤكدة:** المكتبة موجودة في APK لكن **لا أحد يحملها ولا يستخدمها**. حتى لو حُمِّلت يدوياً عبر `System.loadLibrary("JoinImage")`، **لا يوجد class Java بإسم `cn.pda.serialport.JoinImage`** في الـ APK لتربطها بـ JNI signatures.

---

## 6. الفحص الأمني

| الميزة | الحالة | التقييم |
|---|---|---|
| **NX (Non-eXecutable Stack)** | ✅ `GNU_STACK RW` | جيد — Stack غير قابل للتنفيذ |
| **PIE (Position Independent Executable)** | ✅ `Type: DYN` | جيد — ASLR مدعوم |
| **RELRO** | ✅ `GNU_RELRO` موجود | جيد |
| **Stack Canary** | ✅ `__stack_chk_fail@LIBC` | جيد — حماية ضد buffer overflow |
| **Stripped** | ✅ Stripped | جيد للحماية من RE |
| **BIND_NOW** | ✅ موجود | جيد — full RELRO ممكن |

**حكم محايد:** المكتبة مبنية بإعدادات أمان معقولة. **هذا لا يُعفي من حقيقة أنها dead code يجب حذفها**.

---

## 7. تأثير الحجم على APK

```
armeabi-v7a/libJoinImage.so:   30,364 bytes (≈ 30KB)
x86/libJoinImage.so:           30,252 bytes (≈ 30KB)
x86_64/libJoinImage.so:        34,960 bytes (≈ 34KB)
─────────────────────────────────────
المجموع:                       ≈ 95KB من حجم APK
```

> **اكتشاف 🟡:** الإضافة بسيطة (~95KB) لكنها **بلا فائدة وظيفية**. APK الإجمالي ~50MB، لذا التأثير النسبي ~0.2% — لكن المبدأ خاطئ.

---

## 8. أصل المكتبة (تخمين مبني على أدلة)

`cn.pda.serialport` هو الـ package الشائع في **SDKs لأجهزة PDA الصينية** (مثل Chainway, UROVO, Newland). هذه الأجهزة تأتي مع:
- قارئ بطاقات هوية مدمج.
- قارئ Wiegand.
- ماسح باركود.
- منفذ Serial.

**الأرجح:** هذا الجهاز المُستهدف الأصلي كان **PDA صيني** مُجهَّز لقراءة بطاقات هوية. لكن في AbbasiyCashiers، التطبيق يعمل على أجهزة Android عادية بكاميرا فقط — لا قراءة CID مدمجة.

**عنوان GitHub مطابق محتمل:** `https://github.com/HelloVass/JoinImage` — مكتبة C++ لمعالجة الصور لـ OCR (مفتوحة المصدر).

---

## 9. البديل في React Native

بما أن المكتبة **غير مُستخدمة**، لا حاجة لبديل. ✅ **احذفها فقط**.

**لو احتيج في المستقبل لـ OCR في RN:**

| المكتبة | الوظيفة | الحجم |
|---|---|---|
| `react-native-text-recognition` | OCR عام (يستخدم Vision/MLKit) | < 1MB native |
| `@react-native-ml-kit/text-recognition` | Google ML Kit — مجاني، offline | ~5MB (ML Kit) |
| `react-native-tesseract-ocr` | Tesseract OCR — متعدد اللغات | ~10MB |
| `react-native-vision-camera` + `vision-camera-ocr` | كاميرا + OCR في pipeline واحد | ~3MB |

**التوصية:** `@react-native-ml-kit/text-recognition` — مجاني، offline، يدعم العربية ✅، أسرع تطوير، صيانة Google.

---

## 10. التقييم المحايد

### نقاط جيدة ✅
1. مبنية بإعدادات أمان حديثة (NX, PIE, Canary, RELRO).
2. حجمها معقول (~30KB لكل arch).
3. الـ JNI exports واضحة (`cn.pda.serialport.JoinImage`) تكشف الـ binding المتوقع.

### نقاط متوسطة 🟡
1. ABI قديم (`libstdc++.so` بدلاً من `libc++_shared.so`) — يدل على باني قديم.
2. لا يوجد `arm64-v8a` — معمارية مفقودة (الأهم اليوم).
3. تضخم APK بـ ~95KB بلا داعٍ.

### نقاط حرجة 🔴
1. **المكتبة dead code تماماً** — صفر استخدام في Java.
2. لا يوجد `System.loadLibrary("JoinImage")` في كل الكود.
3. لا يوجد class Java مُطابق لـ JNI signatures.
4. تكشف عن **عدم نظافة عملية البناء** — تبقّى من نسخة سابقة على PDA صيني.

---

## 11. أولويات الإصلاح

| الأولوية | الإجراء | السبب |
|---|---|---|
| **P0** | حذف `libJoinImage.so` من كل المعماريات الثلاث في build.gradle | dead code، صفر استخدام، 95KB ضائعة |
| **P0** | تنظيف dependencies في `app/build.gradle` لاستبعاد المصدر الذي يجلبها | تجنّب إعادة تضمينها في builds مستقبلية |
| **P1** | إضافة `arm64-v8a` لو احتيجت مكتبات أصلية أخرى في المستقبل | 64-bit إلزامي على Play Store منذ 2019 |

**سكربت bash للتحقق بعد الإصلاح:**
```bash
unzip -l app.apk | grep -E "\.so$" | awk '{print $4}' | sort -u
# يجب ألا تظهر libJoinImage.so
```

---

## 12. مصادر التحقق

| الادعاء | المصدر | التحقق |
|---|---|---|
| 18 JNI export | `nm -D libJoinImage.so` | عدّ يدوي للسطور التي تبدأ بـ `Java_cn_pda_` |
| dead code | `grep -rn "JoinImage" sources/` | 0 hits |
| لا `loadLibrary("JoinImage")` | `grep "loadLibrary" sources/` | فقط bxlpdf |
| الحجم الفعلي | `ls -l lib/armeabi-v7a/libJoinImage.so` | 30,364 bytes |
| Stripped | `file libJoinImage.so` | الكلمة "stripped" |
| تبعيات libstdc++ | `readelf -d` | NEEDED libstdc++.so |
| Stack canary | `nm -D libJoinImage.so` | `__stack_chk_fail@LIBC` |

---

**انتهى تحليل `libJoinImage.so` — مكتبة dead code يجب حذفها فوراً.**
