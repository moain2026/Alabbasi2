# AbbasiyCashiers_RE_Analysis — فهرس الملاحة الرئيسي

> **مشروع:** تحليل وهندسة عكسية شاملة لتطبيق `AbbasiyCashiers.apk` (الحزمة: `com.egy.webpaymentapp`)
> **الإصدار:** `Ecas v18.4` (versionCode=18)
> **تاريخ التحليل:** 2026-05-22
> **نوع التحليل:** Static Reverse Engineering + Code Review + PoC Verification
> **الحالة:** ✅ مكتمل

---

## 1. ملخص تنفيذي سريع (Executive Summary at a Glance)

تطبيق **AbbasiyCashiers** هو تطبيق نقاط بيع/مدفوعات (POS/Payment) أندرويد، تم تطويره من قِبَل جهة في **اليمن** (الموقّع: *Yahya Aljamal / United Power*، صنعاء). يعتمد التطبيق بشكل كبير على **WebView** و **JavaScript Bridge** للتفاعل مع خادم خلفي افتراضي على:

```
https://abbasiy.yedns.org:8057/payment
```

### نتائج التحليل المختصرة

| المعيار | النتيجة |
|---|---|
| إجمالي الثغرات المكتشفة | **20** ثغرة |
| 🔴 خطيرة جداً (Critical) | **6** |
| 🟠 خطيرة (High) | **5** |
| 🟡 متوسطة (Medium) | **7** |
| 🟢 منخفضة (Low) | **2** |
| آليات مكافحة الهندسة العكسية | ❌ **معدومة تماماً** (لا Root Detection / لا Anti-Debug / لا Obfuscation) |
| التحقق من SSL | ❌ معطّل بالكامل (TrustManager + HostnameVerifier + WebViewClient) |
| التشفير | ⚠️ مفتاح DESede مزروع في الكود (`m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##`) |
| Backdoor مكتشف | ⚠️ نعم — إدخال `1/1/1` كاسم مستخدم/كلمة مرور/كود يفتح شاشة الإعدادات |
| PoC قابل للتشغيل | ✅ `decrypt_ecas_poc.py` — تم التحقق منه |

> **⚠️ تنبيه أخلاقي:** هذه المخرجات بحثية/تعليمية بحتة لأغراض دفاعية (Defensive Security). جميع ثغرات SSL/التشفير/Backdoor المذكورة يتحمل **المسؤولية الكاملة** فيها مطوّرو التطبيق، ويجب إبلاغهم بها وفق مبادئ Coordinated Disclosure.

---

## 2. خريطة المجلدات (Folder Map)

```
AbbasiyCashiers_RE_Analysis/
│
├── README.md                          ← أنت هنا — فهرس الملاحة الرئيسي
│
├── 01_original_apk/                   ← الملف الخام (19 MB)
│   └── AbbasiyCashiers.apk            ← الـ APK الأصلي بعد التحميل
│
├── 02_apktool_output/                 ← مخرجات APKTool (87 MB)
│   └── AbbasiyCashiers/
│       ├── AndroidManifest.xml        ← Manifest مفكوك
│       ├── apktool.yml                ← Metadata
│       ├── smali/                     ← كود Smali للـ classes.dex
│       ├── smali_classes2..5/         ← Multi-DEX
│       ├── res/                       ← جميع موارد XML والصور
│       ├── assets/                    ← الأصول الخام
│       ├── lib/                       ← المكتبات الأصلية (.so)
│       │   ├── arm64-v8a/
│       │   ├── armeabi-v7a/
│       │   ├── x86/
│       │   └── x86_64/
│       └── original/                  ← META-INF (التوقيع)
│
├── 03_jadx_output/                    ← مخرجات JADX (26 MB)
│   └── sources/                       ← 2,406 ملف Java مفكوك (88% نظيف)
│       ├── com/egy/webpaymentapp/     ← كود التطبيق الفعلي
│       │   ├── Screens/               ← Activities (Login, Main, Operations, Webview...)
│       │   ├── webapi/                ← API Models & Services
│       │   └── ...
│       ├── android/support/v4/media/session/MediaSessionCompat.java
│       │                              ← ⚠️ class قياسي مُعدَّل بحقن دوال التشفير
│       └── c/b/a/                     ← الحزمة المُموَّهة (Volley wrapper + Auth)
│
├── 04_manifest_analysis/              ← تحليل Manifest المفصّل
│   ├── AndroidManifest.xml            ← نسخة للمراجعة
│   ├── apktool.yml                    ← نسخة للمراجعة
│   └── manifest_analysis.md           ← 📄 تحليل شامل (7.2 KB)
│
├── 05_static_analysis/                ← التحليل الساكن للكود
│   └── 01_critical_code_snippets.md   ← 📄 10 مقتطفات كود حرجة (10.5 KB)
│
├── 06_findings/                       ← الأدلة والمخرجات
│   ├── CERT.RSA                       ← شهادة التوقيع الرقمي
│   ├── certificate_info.txt           ← تفاصيل keytool
│   ├── file_hashes.txt                ← MD5 + SHA-256 للـ APK
│   ├── security_findings_summary.md   ← 📄 مصفوفة 20 ثغرة (7.6 KB)
│   └── decrypt_ecas_poc.py            ← 🐍 PoC عملي مُتَحقَّق منه (Python)
│
└── 07_report/                         ← التقرير النهائي
    └── FINAL_REPORT.md                ← 📕 التقرير الشامل (40.6 KB / 16 قسم)
```

---

## 3. كيف تقرأ هذا المستودع؟ (Reading Order)

اعتماداً على هدفك:

### 👔 إذا كنت **مدير/قائد فريق** (10 دقائق)
1. اقرأ هذا الـ README (3 دقائق)
2. اقرأ القسم 1 (Executive Summary) في [`07_report/FINAL_REPORT.md`](./07_report/FINAL_REPORT.md)
3. راجع مصفوفة الثغرات في [`06_findings/security_findings_summary.md`](./06_findings/security_findings_summary.md)

### 🛡️ إذا كنت **مهندس أمن** (45 دقيقة)
1. اقرأ **التقرير النهائي كاملاً**: [`07_report/FINAL_REPORT.md`](./07_report/FINAL_REPORT.md)
2. راجع مقتطفات الكود الحرجة: [`05_static_analysis/01_critical_code_snippets.md`](./05_static_analysis/01_critical_code_snippets.md)
3. شغّل PoC للتحقق: [`06_findings/decrypt_ecas_poc.py`](./06_findings/decrypt_ecas_poc.py)
4. راجع تحليل Manifest: [`04_manifest_analysis/manifest_analysis.md`](./04_manifest_analysis/manifest_analysis.md)

### 👨‍💻 إذا كنت **مطوِّر التطبيق** (يجب أن تقرأ كل شيء)
- ابدأ بالقسم 14 (التوصيات والإصلاحات) في `FINAL_REPORT.md`
- ثم اقرأ الثغرات Critical/High في `security_findings_summary.md`
- طبّق الإصلاحات بالترتيب: SSL → Crypto Key → Backdoor → WebView → Cleartext → Backup

### 🎓 إذا كنت **باحث أكاديمي/طالب**
- ابدأ من `FINAL_REPORT.md` كاملاً (يحتوي على المنهجية والمراجع)
- ادرس أنماط الكود في `01_critical_code_snippets.md`
- استكشف مخرجات JADX في `03_jadx_output/sources/` لفهم بنية تطبيقات أندرويد

---

## 4. أبرز 6 ثغرات خطيرة جداً (Top Critical Findings)

| # | الثغرة | الموقع في الكود | الأثر | OWASP MASVS |
|---|---|---|---|---|
| **F-01** | تعطيل كامل لـ TrustManager (يقبل أي شهادة) | `c/b/a/f/d.java` | MITM شامل لكل API | MSTG-NETWORK-3 |
| **F-02** | HostnameVerifier يرجع `true` دائماً | `c/b/a/f/c.java` | MITM شامل | MSTG-NETWORK-3 |
| **F-03** | WebViewClient يتجاوز جميع أخطاء SSL | `Screens/web/h.java` | MITM للويب | MSTG-NETWORK-3 |
| **F-04** | مفتاح DESede مزروع في الكود | `MediaSessionCompat.java:619` | فك تشفير جميع البيانات | MSTG-CRYPTO-1 |
| **F-05** | Backdoor: `1/1/1` يفتح الإعدادات | `Screens/LoginActivity.java:65` | تجاوز المصادقة | MSTG-AUTH-1 |
| **F-06** | `setAllowUniversalAccessFromFileURLs(true)` + JSBridge | `Screens/web/WebviewActivity.java:432` | XSS-to-Native RCE | MSTG-PLATFORM-7 |

> القائمة الكاملة (20 ثغرة) متوفرة في [`06_findings/security_findings_summary.md`](./06_findings/security_findings_summary.md)

---

## 5. الأدوات المستخدمة (Toolchain)

| الأداة | الإصدار | الاستخدام |
|---|---|---|
| **APKTool** | 2.7.0 | فك تجميع الموارد + Smali |
| **JADX** | 1.5.0 | فك تجميع DEX → Java |
| **keytool** | OpenJDK 17 | تحليل شهادة التوقيع |
| **openssl / md5sum** | system | التحقق من السلامة |
| **PyCryptodome** | latest | تنفيذ PoC للتشفير |
| **grep / find** | system | البحث في الكود |

---

## 6. كيفية إعادة إنتاج التحليل (Reproduction)

```bash
# 1. تحميل الـ APK
wget -O AbbasiyCashiers.apk \
  "https://files.manuscdn.com/user_upload_by_module/session_file/310519663652154187/TiRnOPtnNaKPCTIY.apk"

# 2. التحقق من البصمة
sha256sum AbbasiyCashiers.apk
# (قارن مع 06_findings/file_hashes.txt)

# 3. APKTool decompile
apktool d -f -o apktool_out AbbasiyCashiers.apk

# 4. JADX decompile
jadx --no-res --show-bad-code -d jadx_out AbbasiyCashiers.apk

# 5. تحقق من شهادة التوقيع
unzip -p AbbasiyCashiers.apk META-INF/CERT.RSA | \
  keytool -printcert

# 6. تشغيل PoC للتأكد من المفتاح المزروع
pip install pycryptodome
python3 06_findings/decrypt_ecas_poc.py test
# يجب أن ترى: "Self-test: ALL PASS ✓"
```

---

## 7. ملاحظات حول التحليل الديناميكي (Dynamic Analysis)

التحليل الديناميكي **لم يُنفَّذ** لأن بيئة الـ Sandbox الحالية (Linux) لا تحتوي على محاكي Android أو جهاز حقيقي. ومع ذلك:

- تم توثيق **سيناريوهات Frida المقترحة** بالكامل في القسم **13** من `FINAL_REPORT.md`
- جميع نقاط الـ Hook المقترحة مُحدَّدة بدقة (أسماء classes/methods الفعلية بعد deobfuscation)
- يمكن لمحلل أمن لديه جهاز Android حقيقي + Frida تنفيذ السيناريوهات بسهولة بناءً على المراجع المُقدَّمة

---

## 8. حقائق رئيسية عن التطبيق (Quick Facts)

| الحقل | القيمة |
|---|---|
| اسم الحزمة | `com.egy.webpaymentapp` |
| اسم التطبيق | Ecas (AbbasiyCashiers) |
| الإصدار | v18.4 (versionCode 18) |
| Min SDK | 19 (Android 4.4 KitKat) |
| Target SDK | 32 (Android 12L) |
| حجم الـ APK | ~19 MB |
| عدد الـ Activities | 6 |
| عدد الأذونات | 29 (3 منها بأسماء خاطئة) |
| MD5 | راجع `06_findings/file_hashes.txt` |
| SHA-256 | راجع `06_findings/file_hashes.txt` |
| موقّع بـ | Yahya Aljamal — United Power — Sanaa, Yemen |
| صلاحية الشهادة | 2021 → 2046 (25 سنة، Self-Signed) |
| الخادم الافتراضي | `https://abbasiy.yedns.org:8057/payment` |
| Deeplink | `https://ecas.web.link/...?ip=<encrypted>` |

---

## 9. الترخيص والإخلاء (License & Disclaimer)

هذا التحليل هو **عمل بحثي/أكاديمي/أمن دفاعي** بحت. الكاتب:

- ❌ **لم يقم** بمهاجمة أي خادم حي
- ❌ **لم يستخرج** أي بيانات مستخدمين حقيقية
- ❌ **لا يشجّع** على إساءة استخدام النتائج
- ✅ **يدعو** مطوّري التطبيق للاطلاع على هذا التحليل وإصلاح الثغرات
- ✅ **ينصح** المستخدمين بعدم استعمال التطبيق حتى يتم إصلاح ثغرة SSL على الأقل

> جميع التحاليل أُجريت على ملف APK مُحمَّل علناً، باستخدام أدوات مفتوحة المصدر متاحة قانونياً، في بيئة معزولة (Sandbox)، دون أي اتصال بالخادم الحي.

---

## 10. روابط سريعة (Quick Links)

- 📕 **التقرير النهائي الكامل**: [`07_report/FINAL_REPORT.md`](./07_report/FINAL_REPORT.md)
- 🔬 **مقتطفات الكود الحرجة**: [`05_static_analysis/01_critical_code_snippets.md`](./05_static_analysis/01_critical_code_snippets.md)
- 📊 **مصفوفة الثغرات (20 ثغرة)**: [`06_findings/security_findings_summary.md`](./06_findings/security_findings_summary.md)
- 🔐 **PoC مُتَحقَّق منه**: [`06_findings/decrypt_ecas_poc.py`](./06_findings/decrypt_ecas_poc.py)
- 📜 **شهادة التوقيع**: [`06_findings/certificate_info.txt`](./06_findings/certificate_info.txt)
- 🔍 **تحليل Manifest**: [`04_manifest_analysis/manifest_analysis.md`](./04_manifest_analysis/manifest_analysis.md)

---

**نهاية الفهرس** | للتفاصيل الكاملة، يُرجى مراجعة `07_report/FINAL_REPORT.md`
