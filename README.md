# 🔍 AbbasiyCashiers Deep RE Analysis

> **التحليل العكسي العميق لتطبيق `AbbasiyCashiers` (Ecas v18.4)**
> توثيق هندسي شامل لكل جوانب التطبيق + Blueprint كامل لإعادة البناء بـ React Native.

[![Status](https://img.shields.io/badge/Status-100%25%20Complete-success)](Deep_Analysis/README.md)
[![Files](https://img.shields.io/badge/Files-52%2F52-blue)](Deep_Analysis/)
[![Size](https://img.shields.io/badge/Docs-~1.5MB-orange)](Deep_Analysis/)
[![PRs](https://img.shields.io/badge/PRs-6%20Merged-purple)](https://github.com/moain2026/Alabbasi2/pulls?q=is%3Apr+is%3Aclosed)

---

## 📌 ما هذا المستودع؟

هذا المستودع يحتوي على **تحليل عكسي (Reverse Engineering) هندسي عميق** لتطبيق دفع/تحصيل أندرويد يُسمى **AbbasiyCashiers** (داخلياً: Ecas v18.4، package: `com.egy.webpaymentapp`).

التحليل **محايد، علمي، موثَّق بمراجع وأكواد فعلية**، ومُصمَّم ليُستخدم كأساس لـ **إعادة بناء كاملة** للتطبيق بتقنيات حديثة.

### 🎯 الجمهور المستهدف

| المستخدم | كيف يستفيد |
|---|---|
| 👨‍💻 **مطور React Native** | يجد Blueprint كامل + TypeScript models جاهزة |
| 🏗️ **Architect / Tech Lead** | يجد مخططات معمارية + قرارات tech stack |
| 🛡️ **Security Auditor** | يجد تحليل كامل للتشفير + الثغرات + التوصيات |
| 💼 **Product Manager** | يجد priorities P0/P1/P2 + roadmap + cost estimates |
| 🤖 **AI Agent (Future)** | اقرأ [`AGENT_HANDOFF.md`](AGENT_HANDOFF.md) أولاً! |

---

## 🚀 ابدأ من هنا

### 1️⃣ إذا كنت **وكيل AI** يكمل العمل على هذا المشروع:
👉 اقرأ **[`AGENT_HANDOFF.md`](AGENT_HANDOFF.md)** — دليل شامل لكل التفاصيل، الاكتشافات، الـ Workflow، والـ Conventions.

### 2️⃣ إذا كنت تريد **فهم التطبيق الحالي**:
👉 ابدأ بـ **[`Deep_Analysis/README.md`](Deep_Analysis/README.md)** — الفهرس الكامل بـ 52 ملف.

### 3️⃣ إذا كنت تريد **بناء التطبيق من جديد**:
👉 اذهب مباشرة إلى **[`Deep_Analysis/10_rebuild_blueprint/`](Deep_Analysis/10_rebuild_blueprint/)** — Blueprint كامل.

### 4️⃣ إذا كنت تريد **النتائج الأمنية فقط**:
👉 اذهب إلى **[`Deep_Analysis/07_crypto_protocols/01_current_crypto_audit.md`](Deep_Analysis/07_crypto_protocols/01_current_crypto_audit.md)**.

---

## 📊 إحصائيات سريعة

| المؤشر | القيمة |
|---|---|
| **عدد ملفات التحليل** | **52 ملف** |
| **حجم التوثيق** | **~1.5 MB** نصوص |
| **عدد الأقسام** | **10 أقسام** (00-10) |
| **عدد الـ PRs المدموجة** | **6 PRs** ✅ |
| **عدد الجلسات التحليلية** | **5 جلسات** |
| **الاكتشافات الصادمة** | **52 اكتشاف (V1-V52)** |
| **الأخطاء البرمجية** | **39 خطأ موثَّق** |
| **المشاكل المالية** | **10 مشاكل** |
| **الكود الميت** | **~12.7 MB** (30% من APK) |

---

## 🗂️ هيكل المستودع

```
Alabbasi2/
│
├── README.md                          ← أنت هنا
├── AGENT_HANDOFF.md                   ← 🤖 دليل شامل لأي وكيل AI لاحق
├── .gitignore
│
├── AbbasiyCashiers_RE_Analysis/       ← نتائج الأدوات الخام
│   ├── 01_original_apk/               ← الـ APK الأصلي
│   ├── 02_apktool_output/             ← Smali + res + AndroidManifest (apktool)
│   ├── 03_jadx_output/                ← كود Java مُعاد بناؤه (jadx)
│   ├── 04_manifest_analysis/          ← تحليل AndroidManifest
│   ├── 05_static_analysis/            ← تحليل ساكن
│   ├── 06_findings/                   ← اكتشافات أولية
│   ├── 07_report/                     ← تقرير أولي
│   └── README.md
│
└── Deep_Analysis/                     ← 📚 التوثيق التحليلي الكامل (52 ملف)
    ├── README.md                      ← الفهرس الرئيسي للتحليل
    ├── _raw_extracted/                ← الـ HTML/JS بعد deobfuscation
    │
    ├── 01_overview/                   (3 ملفات)
    ├── 02_api_contract/               (6 ملفات)
    ├── 03_data_models/                (5 ملفات)
    ├── 04_screens_flow/               (6 ملفات)
    ├── 05_webview_bridge/             (7 ملفات)
    ├── 06_business_logic/             (7 ملفات)
    ├── 07_crypto_protocols/           (4 ملفات)
    ├── 08_native_libs/                (4 ملفات)
    ├── 09_assets_resources/           (6 ملفات)
    └── 10_rebuild_blueprint/          (8 ملفات)
```

---

## 🔥 الـ Top 5 اكتشافات صادمة

| # | الاكتشاف | الخطورة | المرجع |
|---|---|---|---|
| **V51** | 🔴🔴🔴 انتهاك ترخيص خط Helvetica Neue (Monotype 2012 commercial) — MD5 verified | قانوني | [09_assets_resources/06](Deep_Analysis/09_assets_resources/06_colors_themes_styles.md) |
| **V1** | 🔴🔴🔴 `usesCleartextTraffic="true"` — بيانات الدفع عبر HTTP عادي | أمني | [07_crypto_protocols/01](Deep_Analysis/07_crypto_protocols/01_current_crypto_audit.md) |
| **V4** | 🔴🔴🔴 SQL strings مدمجة في URLs (SQL injection vector) | أمني | [02_api_contract/03](Deep_Analysis/02_api_contract/03_payments_endpoints.md) |
| **V5** | 🔴🔴 `Integer.parseInt` للطرح + `Double` لـ currency = فقدان دقة مالية | مالي | [06_business_logic/07](Deep_Analysis/06_business_logic/07_currency_handling.md) |
| **V14** | 🟠 OpenCV 2.4.13.6 (2018, EOL) = **10MB كود ميت** + 9,095 JNI export | حجم | [08_native_libs/04](Deep_Analysis/08_native_libs/04_libopencv_java.md) |

> القائمة الكاملة (V1-V52) في [`AGENT_HANDOFF.md`](AGENT_HANDOFF.md#%EF%B8%8F-52-اكتشاف-صادم-v1-v52).

---

## 💰 التكلفة المقدّرة لإعادة البناء

| السيناريو | المدة | التكلفة | المخرجات |
|---|---|---|---|
| **MVP (P0 فقط)** | 4 شهور | ~$80,000 USD | تطبيق آمن، قانوني، دقيق مالياً |
| **🏆 الموصى به** | 12 شهر | ~$350,000 USD | كامل: P0+P1+P2، modernization كاملة |
| **Premium (سرعة)** | 6 شهور | ~$300,000 USD | فريق مضاعف، نفس الـ scope |
| **Outsourcing** | 12 شهر | ~$140,000-$180,000 USD | فريق من بلدان منخفضة التكلفة |

تفاصيل كاملة في [`Deep_Analysis/10_rebuild_blueprint/07_migration_path.md`](Deep_Analysis/10_rebuild_blueprint/07_migration_path.md).

---

## 🛠️ التقنيات والأدوات المستخدمة في التحليل

| الفئة | الأداة | الاستخدام |
|---|---|---|
| **APK Reverse Engineering** | `apktool` | فك تشفير APK → Smali + resources |
| | `jadx` | DEX → Java source code |
| | `dex2jar` | DEX → JAR |
| **Native Analysis** | `readelf` | ELF headers + sections |
| | `nm -D` | Dynamic symbols (JNI exports) |
| | `strings` | استخراج النصوص من binaries |
| | `file` | تحديد نوع الملف |
| **File Verification** | `md5sum`, `sha256sum` | كشف الملفات المكررة + التزوير |
| **JS Deobfuscation** | Python regex | فك string-array obfuscation |
| **Git Workflow** | `git`, `gh` CLI | atomic commits + PRs + squash merge |

---

## 🎯 الـ Tech Stack الموصى به للإعادة بناء

```typescript
{
  framework:    "React Native 0.74+ (New Architecture / Fabric)",
  language:     "TypeScript (strict mode)",
  navigation:   "React Navigation 7 (or Expo Router)",
  state:        "Zustand + TanStack Query",
  forms:        "React Hook Form + Zod",
  i18n:         "react-i18next (مع 6 صيغ Arabic plurals)",
  ui:           "react-native-paper (Material 3) أو Tamagui",
  fonts:        "Cairo (Google Fonts, SIL OFL - مجاني!)",
  icons:        "react-native-vector-icons / Lucide",
  webview:      "react-native-webview (للـ vReport فقط)",
  pdf:          "react-native-pdf + react-native-blob-util",
  printer:      "react-native-thermal-receipt-printer-image-qr",
  bluetooth:    "react-native-bluetooth-classic",
  http:         "axios + retry + interceptors",
  storage:      "react-native-mmkv (مشفّر) + react-native-keychain",
  crypto:       "react-native-aes-crypto + tweetnacl (للـ E2EE)",
  money:        "bignumber.js (BigDecimal arithmetic)",
  testing:      "Jest + Detox",
  ci:           "GitHub Actions + EAS Build"
}
```

---

## 📜 سجل الـ Pull Requests

| PR # | العنوان | الأقسام | الحالة |
|---|---|---|---|
| [#1](https://github.com/moain2026/Alabbasi2/pull/1) | Comprehensive RE analysis (foundations) | 00-05 | ✅ MERGED |
| [#2](https://github.com/moain2026/Alabbasi2/pull/2) | Complete 10_rebuild_blueprint (8/8) | 10 | ✅ MERGED |
| [#3](https://github.com/moain2026/Alabbasi2/pull/3) | Add 07_crypto_protocols section | 07 | ✅ MERGED |
| [#4](https://github.com/moain2026/Alabbasi2/pull/4) | Complete 06_business_logic | 06 | ✅ MERGED |
| [#5](https://github.com/moain2026/Alabbasi2/pull/5) | Complete 08_native_libs | 08 | ✅ MERGED |
| [#6](https://github.com/moain2026/Alabbasi2/pull/6) | Complete 09_assets_resources — 100% DONE | 09 | ✅ MERGED |

---

## ⚖️ ترخيص هذا التحليل

هذا التحليل **توثيقي/تعليمي** لأغراض إعادة البناء الشرعية. لا تتم إعادة توزيع أي جزء من الكود المملوك لـ AbbasiyCashier، بل **تحليل سلوكي** فقط (RE for interoperability).

---

## 🤝 المساهمة

⚠️ المشروع **مكتمل 100%** ولا يقبل تغييرات جديدة بدون مناقشة. للأسئلة، افتح issue.

---

## 🔗 روابط مهمة

- 🌐 **المستودع:** https://github.com/moain2026/Alabbasi2
- 📚 **فهرس التحليل:** [`Deep_Analysis/README.md`](Deep_Analysis/README.md)
- 🤖 **دليل الـ AI Agents:** [`AGENT_HANDOFF.md`](AGENT_HANDOFF.md)
- 📋 **كل الـ PRs:** https://github.com/moain2026/Alabbasi2/pulls?q=is%3Apr

---

**Last Updated:** 2026-05-22 • **Status:** ✅ 100% Complete • **Files:** 52/52
