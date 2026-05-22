# 03 — تحليل المكتبة الأصلية `libcomm_serial_port.so`

> **التطبيق:** AbbasiyCashiers — Ecas v18.4 — `com.egy.webpaymentapp`
> **النطاق:** مكتبة Serial Port (UART/TTY) — لـ PDA صيني، **غير مُستخدمة**
> **منهج التحليل:** محقق محايد — `readelf` + `nm -D` + `strings` + grep على jadx
> **مصدر الـ APK:** `lib/{armeabi-v7a,x86,x86_64}/libcomm_serial_port.so`

---

## 1. الملخص التنفيذي (Dead Code ثاني!)

🚨 **اكتشاف صدامي:** مكتبة **dead code أخرى!** بعد `libJoinImage.so` (المكتبة الأولى dead code)، هذه ثاني مكتبة في الـ APK **غير مُستدعاة في الكود**.

| البند | القيمة |
|---|---|
| الاسم | `libcomm_serial_port.so` |
| الـ package المستهدف | `cn.pda.serialport.SerialPort` |
| عدد الـ JNI exports | **6 دوال** فقط |
| الحجم لكل معمارية | armeabi-v7a: 18,044 B ≈ **18KB** • x86: 9,692 B • x86_64: 10,280 B |
| **مُستدعاة في كود Java؟** | ❌ **لا — صفر مرجع** |
| `System.loadLibrary("comm_serial_port")` | ❌ **غير موجود** |
| `import cn.pda.serialport.SerialPort` | ❌ **غير موجود** |
| الوظيفة المعلنة | فتح/قراءة/كتابة منفذ Serial + كتابة Wiegand |
| الفائدة الفعلية | **صفر** — يمكن حذفها بدون أي تأثير |
| تأثيرها على حجم APK | +38KB لثلاث معماريات |

**الحكم:** مثل `libJoinImage.so` تماماً — مكتبة من **SDK لجهاز PDA صيني** مُجهَّز بـ:
- منفذ Serial داخلي (لطابعة حرارية مدمجة أو ماسح باركود).
- قارئ بطاقات Wiegand (لمراقبة الدخول).

التطبيق لا يحتاج أياً من هذه — Bixolon SPP-R310 تتصل عبر **Bluetooth Classic**، لا عبر Serial Port.

---

## 2. الفحص بـ `file`

```
$ file lib/armeabi-v7a/libcomm_serial_port.so
ELF 32-bit LSB shared object, ARM, EABI5 version 1 (SYSV),
dynamically linked,
BuildID[sha1]=d51b98a6e7abf7cb3cb360bf4e944018cbee7d74,
stripped
```

**ملاحظات:**
- ✅ ELF 32-bit ARM — صحيح.
- ✅ Stripped — رموز debug محذوفة.
- ✅ BuildID مميز للمطابقة.

---

## 3. التبعيات الديناميكية

```
NEEDED libdl.so
NEEDED liblog.so      ← Android __android_log_print
NEEDED libc.so
NEEDED libm.so
NEEDED libstdc++.so   ← قديم
SONAME libcomm_serial_port.so
```

**ملاحظات:**
- ❌ **لا يوجد `libjnigraphics.so`** — لا تتعامل مع Bitmap (منطقي — Serial فقط).
- 🟡 `libstdc++.so` بدلاً من `libc++_shared.so` → باني قديم (NDK r10 أو أقل).

---

## 4. الـ JNI Exports — 6 دوال فقط

استخراج كامل عبر `nm -D --defined-only`:

| الدالة JNI | الدلالة |
|---|---|
| `Java_cn_pda_serialport_SerialPort_openSerialPort` | فتح منفذ Serial (يُمرَّر path: `/dev/ttyXX`) |
| `Java_cn_pda_serialport_SerialPort_closeSerialPort` | إغلاق المنفذ |
| `Java_cn_pda_serialport_SerialPort_readSerialPort` | قراءة بيانات من المنفذ |
| `Java_cn_pda_serialport_SerialPort_writeSerialPort` | كتابة بيانات على المنفذ |
| `Java_cn_pda_serialport_SerialPort_getFileDescriptor` | الحصول على FD (للاستخدام النظامي) |
| `Java_cn_pda_serialport_SerialPort_writeWiegand` | **كتابة بروتوكول Wiegand!** |

> **استنتاج تقني:**
> 1. الـ 5 الأولى = wrapper بسيط حول POSIX `open()`, `close()`, `read()`, `write()` لمنفذ TTY.
> 2. **`writeWiegand`** = دالة خاصة جداً لبروتوكول **Wiegand** المُستخدم في **قارئات البطاقات والبصمات** (للتحكم في الدخول).
> 3. حضور `writeWiegand` يكشف أن المكتبة جُلِبت من **جهاز PDA متكامل** يحوي ماسح بطاقات Wiegand (مثل Chainway, UROVO).

### 4.1 ما هو بروتوكول Wiegand؟
- بروتوكول قديم (1980s) لإرسال بيانات البطاقات/البصمات.
- يستخدم 26-bit أو 34-bit عادةً.
- يعتمد على خطين فقط (D0, D1) — تيار رقمي بسيط.
- شائع في أنظمة Access Control (المداخل والبوابات).

---

## 5. الـ strings المُكتشفة

```bash
$ strings libcomm_serial_port.so | head -20
libcomm_serial_port.so
Java_cn_pda_serialport_SerialPort_closeSerialPort
Java_cn_pda_serialport_SerialPort_getFileDescriptor
Java_cn_pda_serialport_SerialPort_openSerialPort
Java_cn_pda_serialport_SerialPort_readSerialPort
Java_cn_pda_serialport_SerialPort_writeSerialPort
Java_cn_pda_serialport_SerialPort_writeWiegand
error:SetupSerial 3
serial_port
Android (5058415 based on r339409) clang version 8.0.2 ...
```

**اكتشافات:**
- ✅ **معرف الباني:** `clang version 8.0.2` من Android NDK r17 (2018).
- 🟡 **رسالة خطأ هزيلة:** `"error:SetupSerial 3"` — رقم خطأ مبهم، لا تسجيل صحيح.
- ✅ لا توجد أسرار/مفاتيح/URLs مدمجة.

---

## 6. **الأهم: هل تُستخدم؟** (بحث grep)

### 6.1 بحث `loadLibrary`

```bash
$ grep -rn "loadLibrary.*serial\|loadLibrary.*comm" sources/
# 0 hits
```

### 6.2 بحث `import` / package

```bash
$ grep -rln "cn.pda.serialport\|SerialPort" sources/
# 0 hits
```

### 6.3 بحث `Class.forName`

```bash
$ grep -rn "cn.pda" sources/
# 0 hits
```

### 6.4 بحث AndroidManifest

```bash
$ grep -i "serial\|SerialPort" AndroidManifest.xml
# 0 hits
```

> **🚨 الخلاصة المؤكدة:** المكتبة **غير مُستدعاة من أي مكان**. تماماً مثل `libJoinImage.so`. **dead code يجب حذفها فوراً**.

---

## 7. السياق التاريخي

`cn.pda.serialport` هو الـ namespace القياسي في:
- **Chainway C71/C72** (PDA صيني للوجستيات).
- **UROVO i6310B** (PDA لقطاع البيع بالتجزئة).
- **Newland N7** (PDA لماسحات الباركود).
- **iData K1S** (PDA لقطاع المطاعم).

**حزم BSP** (Board Support Package) لهذه الأجهزة تأتي مع:
- `libcomm_serial_port.so` ← هذا.
- `libJoinImage.so` ← في الملف السابق.
- مكتبات أخرى لـ RFID, NFC, Barcode, Fingerprint.

**الأرجح:** التطبيق بُني أصلاً لجهاز PDA صيني، وتم نسخ كل مكتبات الـ BSP إلى مشروع Android Studio عشوائياً، ثم بقيت في الـ APK النهائي.

---

## 8. لو **استُخدمت** نظرياً — ماذا كانت ستفعل؟

سيناريو افتراضي:
```java
// لو احتاج التطبيق التواصل مع طابعة حرارية داخلية للـ PDA:
SerialPort sp = new SerialPort(new File("/dev/ttyHSL2"), 9600, 0);
OutputStream os = sp.getOutputStream();
os.write("ESC @ ...ESC/POS commands...".getBytes());
os.close();
sp.close();
```

**في AbbasiyCashiers هذا غير موجود.** الطباعة تتم عبر:
- **Bluetooth Classic** لـ Bixolon SPP-R310 (JposPOS API).
- **Bluetooth Classic** لـ Sewoo (PdfRenderer → Bitmap → byte[] → bluetooth socket).

---

## 9. الفحص الأمني

| الميزة | الحالة | تقييم |
|---|---|---|
| **NX (Non-eXecutable Stack)** | ✅ `GNU_STACK RW` | جيد |
| **PIE** | ✅ `Type: DYN` | جيد — ASLR |
| **RELRO** | ✅ `GNU_RELRO` موجود | جيد |
| **Stack Canary** | ✅ `__stack_chk_fail@LIBC` | جيد |
| **Stripped** | ✅ | جيد |

**حكم محايد:** آمنة بشكل قياسي، لكن:

🚨 **خطر نظري:** لو **تمكن مهاجم محلي** من استدعاء هذه المكتبة عبر `System.load("/data/data/com.egy.webpaymentapp/.../libcomm_serial_port.so")` ثم `JNI binding`، يستطيع:
- فتح `/dev/tty*` (لو الجهاز PDA).
- **كتابة/قراءة Wiegand** — في جهاز Access Control يمكن انتحال بطاقات!

في الأجهزة العادية (هواتف Android عادية)، هذا الخطر **منعدم** لأنه لا توجد `/dev/tty*` متاحة بدون root. لكن **وجود المكتبة في APK بدون استخدام = surface attack** غير مبرر.

---

## 10. تأثير الحجم على APK

```
armeabi-v7a/libcomm_serial_port.so:  18,044 B  ≈  18KB
x86/libcomm_serial_port.so:           9,692 B  ≈  10KB
x86_64/libcomm_serial_port.so:       10,280 B  ≈  10KB
──────────────────────────────────────
المجموع:                           ≈ 38KB من حجم APK
```

> **اكتشاف 🟡:** تأثير ضئيل (~38KB)، لكن غير مبرر تماماً.

---

## 11. البديل في React Native

بما أن المكتبة **غير مُستخدمة**، لا حاجة لبديل. ✅ **احذفها فقط**.

**لو احتيج في المستقبل لـ Serial في RN:**

| المكتبة | الوظيفة | حالة الصيانة |
|---|---|---|
| `react-native-serial-port-android` | منفذ Serial USB OTG | ⚠️ موجودة، صيانة محدودة |
| `react-native-usb-serialport-for-android` | wrapper لـ usb-serial-for-android | جيدة |
| `react-native-bluetooth-serial-next` | Bluetooth Serial (SPP) | للطابعات الحرارية |

**التوصية:** **لا تضف serial port** — استخدم Bluetooth SPP أو USB OTG بمكتبة modern للطباعة.

---

## 12. التقييم المحايد

### نقاط جيدة ✅
1. مكتبة صغيرة جداً (~18KB).
2. مبنية بإعدادات أمان كاملة.
3. JNI signatures واضحة (`cn.pda.serialport.SerialPort`).

### نقاط متوسطة 🟡
1. لا يوجد `arm64-v8a` (مفقود في كل المكتبات الأصلية).
2. تضخم APK بـ ~38KB بلا داعٍ.

### نقاط حرجة 🔴
1. **dead code 100%** — صفر استخدام في Java.
2. `writeWiegand` يكشف عن أصلها (جهاز PDA صيني)، ووجودها في تطبيق دفع غير منطقي.
3. عدم نظافة عملية البناء.

---

## 13. أولويات الإصلاح

| الأولوية | الإجراء |
|---|---|
| **P0** | حذف `libcomm_serial_port.so` من كل المعماريات الثلاث |
| **P0** | تنظيف أي مرجع متبقي من dependencies (لو وُجد) |
| **P1** | إضافة سكربت CI للتحقق من dead native libs قبل البناء |

**سكربت CI للكشف عن dead native libs:**
```bash
#!/bin/bash
# detect_dead_native_libs.sh
for lib in app/build/intermediates/.../lib/armeabi-v7a/*.so; do
    libname=$(basename "$lib" .so | sed 's/^lib//')
    if ! grep -rq "loadLibrary(\"$libname\")\|loadLibrary0(\"$libname\")" app/src; then
        echo "DEAD LIB: $lib (not loaded anywhere)"
    fi
done
```

---

## 14. مصادر التحقق

| الادعاء | المصدر | الأمر |
|---|---|---|
| 6 JNI exports | `nm -D libcomm_serial_port.so` | عدّ السطور Java_ |
| dead code | `grep -rn "SerialPort\|cn.pda" sources/` | 0 hits |
| لا `loadLibrary` | `grep "loadLibrary" sources/` | فقط `bxlpdf` |
| الحجم الفعلي | `ls -l lib/*/libcomm_serial_port.so` | 18,044 B (ARM) |
| `writeWiegand` موجود | `nm -D` | `Java_cn_pda_serialport_SerialPort_writeWiegand` |
| Stripped | `file libcomm_serial_port.so` | "stripped" |
| باني clang 8.0.2 | `strings` | "Android ... clang version 8.0.2" |
| لا توجد ttytty refs | `strings \| grep "tty"` | 0 hits |

---

**انتهى تحليل `libcomm_serial_port.so` — مكتبة dead code ثانية يجب حذفها فوراً.**
