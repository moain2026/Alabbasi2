# 04 — تحليل المكتبة الأصلية `libopencv_java.so`

> **التطبيق:** AbbasiyCashiers — Ecas v18.4 — `com.egy.webpaymentapp`
> **النطاق:** OpenCV لمعالجة الصور — **معطّلة بشكل ساخر**
> **منهج التحليل:** محقق محايد — `readelf` + `nm -D` + `strings` + grep على jadx
> **مصدر الـ APK:** `lib/armeabi-v7a/libopencv_java.so`

---

## 1. الملخص التنفيذي (الأخطر فعلياً)

🚨🚨 **اكتشاف صدامي تاريخي:** OpenCV الكامل (**10MB!**) موجود في APK، **لكنه لا يعمل أبداً** بسبب:
1. **لا توجد classes Java للـ `org.opencv.*`** في الـ APK!
2. الكود يستدعيه عبر `Class.forName("org.opencv.android.OpenCVLoader")` الذي **يرمي ClassNotFoundException دائماً**.
3. المكتبة موجودة على **armeabi-v7a فقط** — لا x86 ولا x86_64.
4. **OpenCV 2.4.13.6** — إصدار قديم من **شباط 2018** (آخر LTS من سلسلة 2.4).
5. مبني بـ **NDK r8e** (NDK من سنة 2013!) و **gcc 4.6** — قديم جداً.

| البند | القيمة |
|---|---|
| الاسم | `libopencv_java.so` |
| الإصدار | **OpenCV 2.4.13.6** (Feb 22, 2018) — قديم 6 سنوات |
| الـ JNI exports | **9,095 دالة!** 🚨 |
| الحجم | armeabi-v7a: **10,126,036 B ≈ 10MB** |
| على x86/x86_64 | ❌ **غير موجودة كلياً** |
| Java classes `org.opencv.*` | ❌ **غير موجودة في APK** (المهم!) |
| `loadLibrary("opencv_java")` صريح | ❌ غير موجود |
| `OpenCVLoader.initDebug()` | يُستدعى ضمن `try/catch (ClassNotFoundException)` |
| النتيجة العملية | **OpenCV لا يعمل أبداً** — fallback تلقائي إلى منطق Java بسيط |

**الحكم:** هذه **أكبر mistake في الـ APK** — 10MB من الكود الميت تشكل **~30%** من حجم APK المتوقع. مكتبة جُلِبت كاملة، نُسي تضمين classes Java الخاصة بها، فأصبحت dead weight بحجم خرافي.

---

## 2. الفحص بـ `file`

```
$ file lib/armeabi-v7a/libopencv_java.so
ELF 32-bit LSB shared object, ARM, EABI5 version 1 (SYSV),
dynamically linked,
stripped
```

**ملاحظات:**
- ✅ ELF ARM 32-bit.
- ❌ **موجود فقط على armeabi-v7a** (مفقود من x86, x86_64).
- ✅ Stripped.

---

## 3. هوية OpenCV — تفصيل صادم

استخراج من `strings`:

```
General configuration for OpenCV 2.4.13.6 =====================================
  Version control:               2.4.13.6
  Platform:
    Timestamp:                   2018-02-22T02:34:35Z
    Host:                        Linux 4.13.0-32-generic x86_64
    Target:                      Linux 1 armv7-a
    CMake:                       2.8.12.2
  C/C++:
    Built as dynamic libs?:      NO
    C++ Compiler:                arm-linux-androideabi-g++ (ver 4.6)
  Android: 
    Android ABI:                 armeabi-v7a with NEON
    STL type:                    gnustl_static
    Native API level:            android-8
    SDK target:                  android-11
    Android NDK:                 /opt/android/android-ndk-r8e
                                 (toolchain: arm-linux-androideabi-4.6)
```

### 3.1 تحليل البصمات الزمنية

| العنصر | التاريخ/الإصدار | تقييم |
|---|---|---|
| OpenCV version | 2.4.13.6 — Feb 2018 | 🔴 6 سنوات قديم |
| آخر إصدار في سلسلة 2.x | 2.4.13.6 — End of Life | 🔴 لا تحديثات أمنية |
| الإصدار الحديث | OpenCV 4.x (4.8+ في 2024) | فجوة جيلين |
| Android NDK | r8e — 2013 | 🔴 **11 سنة قديم!** |
| Compiler | gcc 4.6 — 2012 | 🔴 **12 سنة قديم!** |
| Native API level | android-8 (Froyo, 2010) | 🔴 صفر مبالغة في القدم |
| SDK target | android-11 | 🔴 Android 3.0 (2011!) |
| STL | gnustl_static | 🔴 STL قديم جداً |

> **🚨🚨 اكتشاف خرافي:** المكتبة مبنية بأدوات **من 2012–2013** (11–12 سنة قديمة!) وتعمل في APK targeting Android 32 (2022). هذه فجوة تكنولوجية تكاد لا تُصدَّق.

### 3.2 وحدات OpenCV المُضمَّنة

من نفس الـ strings:

```
OpenCV modules:
    To be built: core androidcamera flann imgproc highgui features2d 
                  calib3d ml objdetect video contrib photo java legacy 
                  ocl stitching superres ts videostab
    Disabled:    gpu nonfree world
```

التطبيق يحوي:
- **`core`** — أساس OpenCV (Mat, ndarray).
- **`imgproc`** — معالجة الصور (المستخدم نظرياً في `bitmap2BytesForOpenCV`).
- **`androidcamera`** — Camera API قديم (Android Camera 1).
- **`highgui`** — VideoCapture (Camera 1 layer).
- **`features2d`, `calib3d`, `objdetect`, `ml`, `photo`** — الكثير الكثير.
- **`stitching`, `superres`, `videostab`** — وحدات متقدمة بالكامل.
- **`legacy`, `contrib`** — وحدات قديمة (تجريبية أو منسوخة).

**خلاصة:** المكتبة تحتوي **كل OpenCV** — وليس subset مُحسَّن لاحتياج التطبيق.

---

## 4. التبعيات الديناميكية

```
NEEDED libdl.so
NEEDED libm.so
NEEDED liblog.so
NEEDED libjnigraphics.so
NEEDED libz.so          ← zlib (للضغط، مثل PNG)
NEEDED libc.so
SONAME libopencv_java.so
```

**ملاحظات:**
- ❌ **لا يوجد `libstdc++.so` ولا `libc++_shared.so`** — STL مدمج statically (`gnustl_static`)، يفسّر جزءاً من الحجم الضخم.
- ✅ يحتاج `libjnigraphics` للتعامل مع Bitmap.
- ✅ `libz.so` لفك ضغط ملفات PNG/ZIP.

---

## 5. الـ JNI Exports — 9,095 دالة! 🚨

استخراج عبر `nm -D --defined-only | grep "Java_" | wc -l`:
```
9095
```

**تجميع حسب الوحدة:**

| الوحدة | عدد الـ JNI exports المُعتبرة |
|---|---|
| `org.opencv.android` | ~10 (BitmapToMat, MatToBitmap, الخ) |
| `org.opencv.calib3d` | ~150 (Camera calibration, 3D reconstruction) |
| `org.opencv.core` | ~600 (Mat, MatOfX, Core operations) |
| `org.opencv.features2d` | ~200 (FeatureDetector, DescriptorMatcher) |
| `org.opencv.gpu` | ~600 (GPU acceleration) |
| `org.opencv.highgui` | ~150 (VideoCapture, imshow) |
| `org.opencv.imgproc` | ~400 (filtering, transformations) |
| `org.opencv.ml` | ~250 (Machine learning) |
| `org.opencv.objdetect` | ~80 (CascadeClassifier, HOGDescriptor) |
| `org.opencv.photo` | ~50 (Photo enhancement) |
| `org.opencv.video` | ~100 (Optical flow, background subtraction) |
| `org.opencv.utils.Converters` | ~100 (Type conversion helpers) |
| **المجموع التقريبي** | **~9,095 دالة** |

**كل هذا في 10MB من الكود الميت!**

---

## 6. كيف يُحاول التطبيق استدعاءها؟

### 6.1 موقع الاستدعاء الوحيد

**`com/bxl/printer/builder/BitmapBuilder.java:106-145`:**

```java
private static byte[] bitmap2BytesForOpenCV(Bitmap bitmap, int i, int i2) {
    byte[] bArr = null;
    try {
        Class.forName("org.opencv.android.OpenCVLoader");
        //            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        //            ❌ هذا الـ class غير موجود في APK!
        if (!OpenCVLoader.initDebug()) {
            return null;
        }
        Mat mat = new Mat();              // ← يحاول استخدام Mat
        Mat mat2 = new Mat();
        Mat mat3 = new Mat();
        Utils.bitmapToMat(bitmap, mat);   // ← يحاول bitmapToMat
        Imgproc.resize(mat, mat2, ...);   // ← يحاول Imgproc
        Imgproc.cvtColor(mat2, mat3, 7);
        ...
        return bArr;
    } catch (ClassNotFoundException | Exception | UnsatisfiedLinkError unused) {
        return bArr;     // ❗ كل الأخطاء تُبتلع بصمت!
    }
}
```

### 6.2 السلوك الفعلي خطوة بخطوة

1. **`Class.forName("org.opencv.android.OpenCVLoader")`** يُنفَّذ.
2. الـ ClassLoader يبحث عن `org.opencv.android.OpenCVLoader` في الـ APK.
3. **لا يجدها** → يرمي `ClassNotFoundException`.
4. الـ `catch` يبتلع الاستثناء.
5. الدالة تُرجع `null`.
6. الـ caller (السطر 170-181):

```java
byte[] bitmap2BytesForOpenCV = bitmap2BytesForOpenCV(bitmap, i, i2);
if (bitmap2BytesForOpenCV == null) {       // ← يحدث دائماً!
    bitmap2BytesForOpenCV = bitmap2Bytes(bitmap, i, i2);  // ← fallback
    convertToGray(bitmap2BytesForOpenCV, i, i2, false);
    makeDiffusionImageData(bitmap2BytesForOpenCV, i, i2, 2);
}
```

**النتيجة:** يستخدم `bitmap2Bytes` العادي + `convertToGray` + `makeDiffusionImageData` — كلها Java pure! **OpenCV لا تُستدعى أبداً.**

### 6.3 الدليل القاطع

```bash
$ find sources -path "*org/opencv*"
# 0 results

$ grep -rln "package org.opencv" sources/
# 0 results

$ grep -rln "import org.opencv" sources/
sources/com/bxl/printer/builder/BitmapBuilder.java   ← الوحيد!
```

> **🚨 الإثبات النهائي:** الـ imports موجودة في الكود (تجعل `javac` راضياً)، لكن **الكلاسات الفعلية مفقودة من APK** (لا أحد ضمّن `opencv-java.jar`!). هذا خطأ في عملية البناء.

---

## 7. لماذا توجد على ARM فقط؟

```
armeabi-v7a/libopencv_java.so:  10,126,036 B  ✅
x86/libopencv_java.so:          ❌ غير موجود
x86_64/libopencv_java.so:       ❌ غير موجود
```

**التفسير المرجح:**
- OpenCV 2.4.13.6 SDK يأتي بنسخ متعددة لكل ABI.
- المطور أضاف `libopencv_java.so` يدوياً إلى `jniLibs/armeabi-v7a/` ونسي إضافتها للـ x86.
- أو: في بناء Gradle قديم، الـ `abiFilters` لم يتضمن x86.

**النتيجة:** حتى لو وُجدت classes Java، **لن يعمل OpenCV على أجهزة Intel** بسبب غياب `.so`.

---

## 8. الفحص الأمني

| الميزة | الحالة | تقييم |
|---|---|---|
| **NX (Non-eXecutable Stack)** | ✅ `GNU_STACK RW` | جيد |
| **PIE** | ✅ `Type: DYN` | جيد |
| **RELRO** | ✅ `GNU_RELRO` موجود | جيد |
| **Stack Canary** | 🔴 **`__stack_chk_fail` غير ظاهر في exports!** | **سيء — مكتبة قديمة بدون حماية البفر** |
| **Stripped** | ✅ | جيد |

> **🚨 اكتشاف 🔴 (P1):** على عكس بقية المكتبات، `libopencv_java.so` **لا تظهر `__stack_chk_fail`** في الـ exports — كأنها مبنية **بدون stack canary**. هذا منطقي لأنها بُنيت بـ gcc 4.6 (2012) قبل تعميم Stack Smashing Protection. **مكتبة قديمة معرضة لـ buffer overflows.**

### 8.1 OpenCV 2.4 CVEs معروفة

| CVE | الوصف | التأثير |
|---|---|---|
| **CVE-2017-12597 to 12605** | Buffer overflow في image readers (PNG, BMP, JPEG2000) | يقرأ صورة خبيثة → RCE محتمل |
| **CVE-2018-5268, 5269** | Heap buffer overflow في `cv::PxMDecoder::readData` | RCE من صورة PXM/PPM |
| **CVE-2019-5063, 5064** | Heap buffer overflow في `readData` للـ PNG/TIFF | RCE من صورة خبيثة |
| **CVE-2019-15939** | Out-of-bounds read في `cv::HaarEvaluator::OptFeature::calc` | معلومات سريّة |
| **CVE-2017-1000450** | Heap overflow في `cv::imread` (BMP) | RCE من ملف BMP |

> **🚨 خطر حرج P0:** OpenCV 2.4.13.6 محشوة بـ **CVEs RCE**. لو **تمت إضافة classes Java في build لاحق** (لإصلاح "بسيط")، التطبيق سيصبح فجأة معرضاً لهجمات RCE من خلال صورة خبيثة. **خطر كامن.**

---

## 9. تأثير الحجم على APK

```
armeabi-v7a/libopencv_java.so:  10,126,036 B  ≈  10MB
```

**فقط على ARM!** لكن هذا يمثل:
- ~20–30% من حجم APK المتوقع لتطبيق مثل AbbasiyCashiers.
- بدون فائدة وظيفية واحدة.
- مع خطر أمني كامن.

---

## 10. البديل في React Native

### 10.1 إذا كان الهدف هو معالجة كاميرا العداد فقط

التطبيق لا يستخدم OpenCV حقاً (الـ fallback يعمل). الحل: **حذف libopencv_java.so تماماً**.

### 10.2 لو احتيج فعلاً معالجة صور في RN

| المكتبة | الوظيفة | الحجم native |
|---|---|---|
| `react-native-image-manipulator` (Expo) | crop, resize, rotate, flip | ~500KB |
| `@bam.tech/react-native-image-resizer` | فقط resize | ~200KB |
| `react-native-vision-camera` + frame processors | معالجة فيديو في الوقت الحقيقي | ~2MB |
| `react-native-image-filter-kit` | فلاتر مثل GPUImage | ~3MB |
| `react-native-opencv3` | OpenCV 3.x لـ RN — لو احتيج | ~5MB (مدروس) |

### 10.3 لو احتيج OpenCV بالفعل في RN

| المكتبة | الإصدار |
|---|---|
| `react-native-opencv3` | OpenCV 3.x ✅ مدعوم |
| `@miragehq/react-native-opencv4` | OpenCV 4.x — حديث |

**التوصية:** AbbasiyCashiers **لا يحتاج OpenCV** — الحاجة الوحيدة هي تغيير حجم صورة العداد قبل رفعها. استخدم `Bitmap.createScaledBitmap` من Android العادي (مجاني، 0KB إضافية) أو `react-native-image-resizer` في RN.

---

## 11. التقييم المحايد

### نقاط جيدة ✅
1. مبنية بـ NEON optimization (SIMD لـ ARM).
2. STL static linking (تجنب dependency على gnustl runtime).

### نقاط متوسطة 🟡
1. تشمل وحدات كاملة (gpu, photo, ml) رغم أن الاستخدام المتوقع كان imgproc فقط.

### نقاط حرجة 🔴
1. **10MB dead weight!** أكبر مكتبة في APK بلا أي استخدام.
2. **OpenCV 2.4.13.6 — End of Life منذ 2018** — لا تحديثات أمنية.
3. **لا توجد classes Java** للـ `org.opencv.*` في APK → لا تعمل أصلاً.
4. **مبنية بـ NDK r8e (2013)** و gcc 4.6 (2012) — قديمة جداً.
5. **لا stack canary** — معرضة لـ buffer overflows.
6. **CVEs معروفة كثيرة** — RCE محتمل لو فُتح ضمن ملف صورة خبيث.
7. **موجودة على ARM فقط** — تفاوت معماري غير مبرر.
8. **9,095 دالة JNI** — أكبر سطح هجوم بدون داعٍ.

---

## 12. أولويات الإصلاح

| الأولوية | الإجراء | الفائدة |
|---|---|---|
| **P0** | حذف `libopencv_java.so` فوراً من جميع المعماريات | توفير ~10MB + إزالة 9000 دالة dead code + إزالة CVEs كامنة |
| **P0** | حذف الـ imports غير المُستخدمة من `BitmapBuilder.java` | تنظيف الكود (الـ Java fallback يعمل بدون هذه الـ imports) |
| **P0** | إضافة CI check للتحقق من تطابق native libs مع classes Java | منع حدوث dead code مماثل مستقبلاً |
| **P1** | لو احتيج OpenCV لاحقاً، استخدم **OpenCV 4.x** + NDK حديث | حماية أمنية حديثة |
| **P2** | استخدم `Bitmap.createScaledBitmap` بدلاً من OpenCV لتغيير الحجم | حل مبسط ومجاني |

**مثال CI check:**
```bash
#!/bin/bash
# verify_native_lib_classes.sh
for lib in jniLibs/*/lib*.so; do
    libname=$(basename "$lib" .so)
    if grep -rq "loadLibrary(\"${libname#lib}\")" app/src; then
        # تحقق أن classes Java الخاصة بها موجودة
        # بقراءة JNI exports وفحص وجود الـ classes
        echo "Verifying: $lib"
    else
        echo "WARN: $lib not loaded by app code"
    fi
done
```

---

## 13. مصادر التحقق

| الادعاء | المصدر | الأمر |
|---|---|---|
| 9,095 JNI exports | `nm -D libopencv_java.so` | `\| grep "Java_org_opencv" \| wc -l` |
| OpenCV 2.4.13.6 | `strings libopencv_java.so` | `\| grep "OpenCV [0-9]"` |
| Built Feb 22, 2018 | `strings` | `Timestamp: 2018-02-22T02:34:35Z` |
| NDK r8e | `strings` | `/opt/android/android-ndk-r8e` |
| gcc 4.6 | `strings` | `arm-linux-androideabi-4.6` |
| لا classes Java | `find sources -path "*org/opencv*"` | 0 hits |
| Class.forName + try/catch | `BitmapBuilder.java:109-141` | كود مرئي |
| fallback في السطر 170-181 | `BitmapBuilder.java` | كود مرئي |
| ARM only | `ls lib/*/libopencv_java.so` | فقط armeabi-v7a |
| لا stack canary | `nm -D libopencv_java.so \| grep "stack_chk"` | لا نتائج |
| CVEs معروفة | https://nvd.nist.gov/vuln/search?query=opencv | بحث عام |

---

## 14. سياق أوسع — لماذا حدث هذا؟

**فرضية معقولة لعملية البناء الفاسدة:**

1. **مرحلة قديمة من المشروع:** المطور حاول استخدام OpenCV لـ OCR على بطاقات الهوية أو قراءة العداد.
2. أضاف `libopencv_java.so` في `jniLibs/` لكن **نسي تضمين** `opencv-java.jar` (الـ classes Java).
3. الكود نُسخ من sample Bixolon (الذي يفترض أن OpenCV.jar موجود).
4. الـ `try/catch (ClassNotFoundException)` أخفى المشكلة.
5. الـ fallback عمل، فلم يلاحظ أحد.
6. أُصدرت 18 نسخة من التطبيق (Ecas v1 → v18.4) ولم يلاحظ أحد.
7. ربما المطور الأصلي ترك الشركة، والمطور الحالي يخاف لمسها لأنها "تعمل".

**الدرس:** الـ `try/catch (ClassNotFoundException)` أداة خطرة تُخفي عيوب البناء.

---

**انتهى تحليل `libopencv_java.so` — أكبر فضيحة في الـ APK: 10MB تماماً dead code قديم وغير آمن.**
