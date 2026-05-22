# مخطط إعادة البناء — خيارات Tech Stack

> **الملف:** `10_rebuild_blueprint/01_tech_stack_options.md`
> **الغرض:** مقارنة موضوعية بين الخيارات التقنية لإعادة بناء AbbasiyCashiers، مع توصية نهائية مدعومة بالحجج.
> **القرار النهائي:** **React Native 0.74+ مع TypeScript + WatermelonDB** (راجع §7).

---

## 📋 جدول المحتويات

1. [القيود والمتطلبات](#1-القيود-والمتطلبات)
2. [الخيارات المرشحة](#2-الخيارات-المرشحة)
3. [مقارنة تفصيلية](#3-مقارنة-تفصيلية)
4. [تقييم لكل معيار](#4-تقييم-لكل-معيار)
5. [التكاليف والجهد](#5-التكاليف-والجهد)
6. [مخاطر كل خيار](#6-مخاطر-كل-خيار)
7. [التوصية النهائية](#7-التوصية-النهائية)
8. [خطة الإلغاء (Fallback)](#8-خطة-الإلغاء-fallback)

---

## 1. القيود والمتطلبات

### 1.1 متطلبات وظيفية (من التحليل العميق)

| # | المتطلب | المرجع |
|---|---------|---------|
| F1 | تسجيل دخول مع تشفير كلمة المرور | `06_business_logic/01_login_flow.md` |
| F2 | عمليات تحصيل (3 أوضاع: دفع، قراءة، موقع) | `04_screens_flow/04_operations_screen.md` |
| F3 | اتصال REST بـ ASP.NET Web API 2 | `02_api_contract/01_endpoints_overview.md` |
| F4 | عرض تقارير في WebView من السيرفر | `04_screens_flow/05_webview_screen.md` |
| F5 | طباعة على Bixolon Thermal Printers عبر Bluetooth | `04_screens_flow/06_settings_screen.md` |
| F6 | مشاركة تقارير PDF (WhatsApp/Email) | `05_webview_bridge/04_ShareReport.md` |
| F7 | تخزين بيانات المستخدم محلياً | `03_data_models/01_user_model.md` |
| F8 | معالجة Deeplinks لتغيير الخادم | `06_business_logic/02_deeplink_handler.md` |
| F9 | عرض LTR/RTL وأرقام عربية | (في القسم 09 المتبقي) |

### 1.2 متطلبات غير وظيفية (NFRs)

| # | المتطلب | الهدف |
|---|---------|------|
| NF1 | **العمل بدون إنترنت (Offline-first)** | يجب — الجباة في مناطق ضعيفة الاتصال |
| NF2 | **زمن الاستجابة** | < 200ms لكل عملية محلية |
| NF3 | **دعم Android 7+** (API 24+) | يمكن رفعه من Android 4.4+ الحالي |
| NF4 | **دعم iOS** | اختياري لكن مرغوب (للمشرفين) |
| NF5 | **حجم APK** | < 30 ميجابايت |
| NF6 | **استهلاك البطارية** | < 5%/ساعة في الاستخدام النشط |
| NF7 | **اللغة العربية بالكامل** | RTL إجباري + خطوط عربية |
| NF8 | **أمان** | استبدال جميع الـ 10 ثغرات الموثَّقة |
| NF9 | **قابلية التطوير** | فريق صغير (1-3 مطورين) يمكنه الصيانة |
| NF10 | **مكتبات نشطة** | لا مكتبات مهجورة (آخر تحديث > سنتين) |

### 1.3 الواقع البيئي

- 📱 **الأجهزة:** هواتف Android متوسطة الفئة (RAM 2-4 جيجا، شاشة 5-6 بوصة)
- 🌍 **المنطقة:** اليمن — كهرباء متقطعة، شبكة 3G/4G مع انقطاعات
- 👨‍💼 **المستخدمون:** جباة بمستوى تقني متوسط، عمر 25-55 سنة
- 🖨️ **الطابعات:** Bixolon SPP-R200III, SPP-R310 (Bluetooth)
- 💼 **الفريق:** افتراضياً 1-3 مطورين (حسب ما يبدو من ميزانية مشاريع مماثلة)

---

## 2. الخيارات المرشحة

| # | الخيار | الوصف المختصر |
|---|--------|---------------|
| A | **React Native + TypeScript** | إطار JS هجين شائع، يستهدف Android و iOS |
| B | **Flutter + Dart** | إطار Google، يرسم UI خاصاً به (لا يستخدم Native Views) |
| C | **Native Android (Kotlin)** | Android فقط، استخدام Jetpack Compose |
| D | **Kotlin Multiplatform (KMP)** | كود مشترك للمنطق + UI أصلي لكل منصة |
| E | **Progressive Web App (PWA)** | تطبيق ويب يمكن تثبيته كأنه Native |
| F | **WebView Wrapper المُحسَّن (تطوير تدريجي)** | الإبقاء على البنية الحالية مع إصلاحات |
| G | **Capacitor / Ionic** | تطبيق ويب داخل WebView (مماثل لـ Cordova) |

---

## 3. مقارنة تفصيلية

### 3.1 جدول المقارنة الرئيسي

| المعيار | A: RN+TS | B: Flutter | C: Native (Kotlin) | D: KMP | E: PWA | F: WebView | G: Capacitor |
|---------|---------|-----------|---------------------|--------|--------|------------|--------------|
| **iOS Support** | ✅ نعم | ✅ نعم | ❌ Android فقط | ✅ نعم | ✅ نعم | ❌ Android | ✅ نعم |
| **Offline-First** | ✅ WatermelonDB | ✅ Drift/Isar | ✅ Room | ✅ SQLDelight | ⚠️ IndexedDB محدود | ⚠️ صعب | ⚠️ IndexedDB |
| **Bluetooth Printer** | ✅ مكتبات ناضجة | ✅ مكتبات ناضجة | ✅ JPOS أصلي | ✅ ممكن | ❌ Web Bluetooth محدود | ✅ موجود حالياً | ⚠️ يحتاج plugins |
| **RTL/Arabic** | ✅ ممتاز | ✅ ممتاز | ✅ ممتاز | ✅ ممتاز | ✅ ممتاز | ⚠️ يحتاج CSS | ✅ جيد |
| **Hot Reload** | ✅ فوري | ✅ فوري | ⚠️ بطيء | ⚠️ بطيء | ✅ فوري | ✅ فوري | ✅ فوري |
| **حجم APK** | ~15-25 MB | ~20-30 MB | ~5-10 MB | ~10-15 MB | ~1 MB | ~10 MB | ~20-30 MB |
| **سرعة الأداء** | 🟢 جيدة | 🟢 ممتازة | 🟢 الأفضل | 🟢 ممتازة | 🟡 متوسطة | 🟡 متوسطة | 🟡 متوسطة |
| **منحنى التعلم** | 🟢 منخفض (JS) | 🟡 متوسط (Dart جديد) | 🟢 منخفض (Kotlin) | 🔴 عالٍ (KMP معقد) | 🟢 منخفض (Web) | 🟢 منخفض | 🟢 منخفض |
| **توفر المطورين** | 🟢 كثير | 🟡 متزايد | 🟢 كثير | 🔴 نادر | 🟢 كثير | 🟢 كثير | 🟢 كثير |
| **نضوج المكتبات** | 🟢 جداً ناضج | 🟢 ناضج | 🟢 الأنضج | 🟡 شاب | 🟢 ناضج | 🟢 ناضج | 🟡 متوسط |
| **دعم Old Android (5.0+)** | ✅ | ✅ | ✅ | ✅ | ⚠️ يعتمد | ✅ | ✅ |
| **توافق مع app1** | 🟢 **نفس Stack** | 🔴 إعادة كاملة | 🔴 إعادة كاملة | 🔴 إعادة كاملة | 🔴 مختلف تماماً | 🔴 مختلف | 🟡 جزئي |
| **الصيانة طويلة الأمد** | 🟢 سهلة | 🟢 سهلة | 🟢 سهلة | 🟡 معقدة | 🟢 سهلة | 🔴 صعبة | 🟡 متوسطة |

> **ملاحظة حرجة:** الخيار **F (WebView Wrapper)** هو ما عليه التطبيق الحالي. الاستمرار فيه يعني الإبقاء على معظم الثغرات والقيود (راجع `05_security_improvements.md`).

---

## 4. تقييم لكل معيار

### 4.1 الأداء (Performance)

| الخيار | تقدير | السبب |
|---------|------|------|
| React Native | ⭐⭐⭐⭐ | JS Bridge قد يكون عنق زجاجة، لكن مع **New Architecture (Fabric + TurboModules)** أصبح ممتازاً |
| Flutter | ⭐⭐⭐⭐⭐ | يُترجم لـ ARM native، يرسم UI مباشرة على Skia/Impeller |
| Native Kotlin | ⭐⭐⭐⭐⭐ | الأداء الأمثل بدون أي طبقة وسطى |
| KMP | ⭐⭐⭐⭐⭐ | UI أصلي = أداء أصلي |
| PWA | ⭐⭐⭐ | محدود بـ JS engine + Service Worker overhead |
| WebView | ⭐⭐ | بطيء، خصوصاً عند التنقل بين الصفحات |
| Capacitor | ⭐⭐⭐ | مماثل لـ WebView مع تحسينات |

### 4.2 سرعة التطوير (Time-to-Market)

| الخيار | تقدير | السبب |
|---------|------|------|
| React Native | ⭐⭐⭐⭐⭐ | Hot Reload فوري، JS سهل، نظام بيئي ضخم، **توافق مع app1** |
| Flutter | ⭐⭐⭐⭐ | Hot Reload فوري، لكن Dart يحتاج تعلّم |
| Native Kotlin | ⭐⭐⭐ | بطيء نسبياً (Gradle، إعادة بناء، Compose جديد نسبياً) |
| KMP | ⭐⭐ | شديد التعقيد، يتطلب 2x UI |
| PWA | ⭐⭐⭐⭐⭐ | الأسرع — لا تثبيت، نشر فوري |
| WebView | ⭐⭐ | الحالي معقد بسبب الـ JS Bridge |
| Capacitor | ⭐⭐⭐⭐ | سريع، خصوصاً إذا كان الفريق ويب |

### 4.3 الموثوقية للنطاق التجاري

| الخيار | تقدير | تطبيقات معروفة |
|---------|------|----------------|
| React Native | ⭐⭐⭐⭐⭐ | Facebook, Instagram, Shopify, Discord, Coinbase |
| Flutter | ⭐⭐⭐⭐⭐ | Google Pay, eBay Motors, BMW |
| Native Kotlin | ⭐⭐⭐⭐⭐ | كل تطبيقات Android تقريباً |
| KMP | ⭐⭐⭐⭐ | Netflix, Cash App |
| PWA | ⭐⭐⭐ | Twitter Lite, Starbucks (لكن مدفوعات؟) |
| WebView | ⭐⭐ | يستخدم لتطبيقات داخلية فقط |
| Capacitor | ⭐⭐⭐ | تطبيقات صغيرة-متوسطة |

### 4.4 جودة دعم الـ Bluetooth Printer (Bixolon)

| الخيار | تقدير | الحل |
|---------|------|------|
| React Native | ⭐⭐⭐⭐ | `react-native-bluetooth-escpos-printer`, `react-native-bixolon-printer`, custom TurboModule |
| Flutter | ⭐⭐⭐⭐ | `flutter_bluetooth_serial`, `bluetooth_thermal_printer` |
| Native Kotlin | ⭐⭐⭐⭐⭐ | JPOS SDK من Bixolon مباشرة |
| KMP | ⭐⭐⭐⭐⭐ | نفس Kotlin Native |
| PWA | ⭐ | Web Bluetooth محدود، لا يدعم Printer Profiles |
| WebView | ⭐⭐⭐⭐ | عبر JS Bridge للكود الأصلي (الحالي) |
| Capacitor | ⭐⭐⭐ | يحتاج Plugin مخصص |

> **مهم:** Bixolon توفر **JPOS SDK Android Native** أصلي. أي حل غير native يحتاج **bridge** إلى هذا الـ SDK. التطبيق الحالي يستخدم `d.a.a.*` كـ JPOS wrapper.

### 4.5 جودة دعم العربية و RTL

كل الخيارات الحديثة (A-D) تدعم RTL ممتازاً. التطبيق الحالي يستخدم خطوط Naskh + CSS `direction: rtl;` في HTML.

| الخيار | تقدير | ملاحظات |
|---------|------|----------|
| React Native | ⭐⭐⭐⭐⭐ | `I18nManager.forceRTL(true)` + خطوط مخصصة |
| Flutter | ⭐⭐⭐⭐⭐ | `TextDirection.rtl` + `Intl` package |
| Native Kotlin | ⭐⭐⭐⭐⭐ | `android:layoutDirection="rtl"` + AndroidX |
| KMP | ⭐⭐⭐⭐⭐ | يعتمد على المنصة |

---

## 5. التكاليف والجهد

### 5.1 تقدير الوقت (1-3 مطورين)

| الخيار | MVP (شاشات أساسية) | إصدار كامل | الصيانة سنوياً |
|---------|----------------------|------------|-----------------|
| React Native | **6-8 أسابيع** | **3-4 أشهر** | 200-300 ساعة |
| Flutter | 7-9 أسابيع | 3.5-4.5 أشهر | 250-350 ساعة |
| Native Kotlin (Android فقط) | 5-7 أسابيع | 3 أشهر | 150-250 ساعة |
| KMP | 10-14 أسبوع | 6+ أشهر | 400-500 ساعة |
| PWA | 4-6 أسابيع | 2-3 أشهر | 150-200 ساعة |
| WebView (تحديث الحالي) | 3-4 أسابيع (إصلاحات) | 2-3 أشهر | 300+ ساعة (دين تقني) |
| Capacitor | 5-7 أسابيع | 2.5-3.5 أشهر | 200-300 ساعة |

### 5.2 التكاليف غير المباشرة

| البند | A: RN | B: Flutter | C: Native | D: KMP |
|-------|-------|-----------|-----------|--------|
| **خادم CI/CD** | $20-50/شهر (EAS Build) | $0-50 (Codemagic) | $0-30 (GitHub Actions) | $30-50 |
| **خدمات Crash Reporting** | $0 (Sentry Free) | $0 | $0 | $0 |
| **خدمات Analytics** | $0 (Firebase Free) | $0 | $0 | $0 |
| **رسوم Apple Developer** (لو iOS) | $99/سنة | $99 | لا يوجد | $99 |
| **رسوم Google Play** | $25 مرة واحدة | $25 | $25 | $25 |

---

## 6. مخاطر كل خيار

### 6.1 React Native — المخاطر

| الخطر | الاحتمال | الأثر | التخفيف |
|-------|---------|------|---------|
| تعقيد JS Bridge عند طباعة سريعة | متوسط | متوسط | استخدم **TurboModules** (New Arch) |
| اختلاف سلوك بين Android و iOS | عالٍ | منخفض | اختبار على كلا المنصتين دورياً |
| كسر Breaking Changes بين الإصدارات | متوسط | متوسط | استخدم LTS branches (0.72, 0.74) |
| ضعف دعم بعض Native APIs | منخفض | متوسط | مكتبة `react-native-builder-bob` للـ TurboModules |

### 6.2 Flutter — المخاطر

| الخطر | الاحتمال | الأثر | التخفيف |
|-------|---------|------|---------|
| Dart غير منتشر في الفريق | عالٍ | عالٍ | تدريب 2-4 أسابيع |
| حجم APK كبير | عالٍ | متوسط | استخدم `--split-per-abi` |
| لا توافق مع `app1` (RN) | عالٍ | عالٍ | إعادة كاملة |

### 6.3 Native Kotlin — المخاطر

| الخطر | الاحتمال | الأثر | التخفيف |
|-------|---------|------|---------|
| فقدان دعم iOS مستقبلاً | حتمي | عالٍ | لا حل (أو إعادة بناء iOS لاحقاً) |
| Jetpack Compose جديد نسبياً | متوسط | متوسط | استخدم Views التقليدية كخطة بديلة |

### 6.4 KMP — المخاطر

| الخطر | الاحتمال | الأثر | التخفيف |
|-------|---------|------|---------|
| تعقيد البنية (3 طبقات) | حتمي | عالٍ | لا حل |
| ندرة المطورين | حتمي | عالٍ | لا حل |
| تكلفة UI مضاعفة | حتمي | عالٍ | لا حل |

### 6.5 PWA — المخاطر

| الخطر | الاحتمال | الأثر | التخفيف |
|-------|---------|------|---------|
| لا دعم لـ Bluetooth Printer | حتمي | **حرج** | **لا يمكن استخدام PWA** |

### 6.6 WebView (الحالي) — المخاطر

| الخطر | الاحتمال | الأثر | التخفيف |
|-------|---------|------|---------|
| الإبقاء على 10+ ثغرات أمنية | حتمي | **حرج** | لا تخفيف |
| دين تقني متراكم | حتمي | عالٍ | لا تخفيف |
| صعوبة إضافة ميزات | حتمي | عالٍ | لا تخفيف |

---

## 7. التوصية النهائية

### 🏆 الفائز: **React Native 0.74+ مع TypeScript + WatermelonDB**

### 7.1 الأسباب الرئيسية

#### ✅ السبب 1: **التوافق مع `app1`**
المستودع المرجعي `app1/` (الذي قدمته كمرجع) مبني على **React Native 0.74.5 + TypeScript + WatermelonDB**. استخدام نفس Stack يعني:
- نفس المطورين يمكنهم العمل على المشروعين
- مكتبات وحلول جاهزة مُختبَرة بالفعل
- توحيد البنية التحتية (CI/CD، Linting، Testing)
- إمكانية دمج التطبيقين لاحقاً

#### ✅ السبب 2: **WatermelonDB يحل مشكلة Offline-First بشكل مثالي**
- يدعم Sync تلقائي ثنائي الاتجاه مع REST API
- أداء ممتاز حتى مع 100,000+ سجل
- يحل **مشكلة فقدان المدفوعات** عند انقطاع الإنترنت (راجع `06_business_logic/03_payment_collection.md`)

#### ✅ السبب 3: **سرعة التطوير**
- Hot Reload فوري
- TypeScript = أخطاء أقل في وقت التشغيل
- نظام بيئي ضخم (npm) لكل احتياج

#### ✅ السبب 4: **دعم iOS لاحقاً**
- إذا أراد المشرفون iPad لاحقاً، يكفي build واحد إضافي
- لا حاجة لإعادة كتابة الكود

#### ✅ السبب 5: **مكتبات Bluetooth Printer ناضجة**
- `react-native-ble-plx` (Bluetooth Low Energy)
- `react-native-bluetooth-classic` (Classic SPP — لـ Bixolon)
- يمكن كتابة TurboModule مخصص يستخدم JPOS SDK مباشرة

### 7.2 Stack المُختار بالكامل

```typescript
// === Core ===
React Native     0.74.5+    // الإطار
TypeScript       5.x        // اللغة
Hermes           enabled    // JS Engine (الأسرع)

// === Navigation ===
@react-navigation/native        ~6.x
@react-navigation/native-stack
@react-navigation/bottom-tabs

// === State Management ===
Zustand          4.x        // بسيط، خفيف، TypeScript-first
React Query      5.x        // server state + caching
// (لا Redux — overkill لهذا الحجم)

// === Database (Offline-First) ===
WatermelonDB     0.27+      // SQLite + sync layer
// جداول: customers, payments, readings, settings

// === HTTP Client ===
axios            1.x        // REST client مع interceptors
// أو: ky (modern fetch wrapper)

// === Forms & Validation ===
react-hook-form  7.x
zod              3.x        // schema validation

// === UI Components ===
react-native-paper          // Material Design 3
// أو: tamagui / nativewind   // TailwindCSS-like
react-native-reanimated     // animations
react-native-gesture-handler

// === Bluetooth Printing ===
react-native-bluetooth-classic   // أو TurboModule مخصص
// + Bixolon JPOS SDK مغلَّف في TurboModule

// === Security ===
react-native-keychain        // تخزين آمن للـ tokens
react-native-ssl-pinning     // Certificate pinning
crypto-js / react-native-quick-crypto

// === Internationalization ===
react-i18next               // i18n
react-native-localize       // detection
// + ضبط I18nManager.forceRTL(true)

// === Quality ===
ESLint + Prettier
Jest + Detox (E2E)
Sentry (crash reporting)

// === Build & CI/CD ===
EAS Build (Expo) — اختياري
أو Bare RN + GitHub Actions

// === Code Generation ===
@hookform/resolvers    // zod + react-hook-form
react-native-codegen   // TurboModules
```

### 7.3 لماذا ليس باقي الخيارات؟

| الخيار | لماذا رُفض؟ |
|---------|------------|
| **Flutter** | جيد جداً، لكن لا يوجد توافق مع `app1`. اختياره يعني عدم استخدام أي مكتبات/كود من المرجع. |
| **Native Kotlin** | ممتاز للأداء، لكن يمنع iOS مستقبلاً ويُضاعف العمل لو احتجناه. |
| **KMP** | تعقيد مفرط لتطبيق تحصيل بسيط. مناسب لتطبيقات بحجم Cash App. |
| **PWA** | لا يدعم Bluetooth Printer = **مرفوض تماماً**. |
| **WebView (الحالي)** | الإبقاء على 10+ ثغرات + دين تقني = **مرفوض**. |
| **Capacitor** | مماثل لـ WebView في الأداء، يفقد ميزات Native كثيرة. |

---

## 8. خطة الإلغاء (Fallback)

### 8.1 إذا فشل React Native لسبب ما (احتمال < 5%)

**الترتيب الاحتياطي:**

1. **Plan B: Flutter** — إذا أثبتت React Native ضعفاً في الطباعة الـ Bluetooth أو حصلت مشاكل أداء حرجة. الانتقال يحتاج 2-3 أسابيع إضافية.

2. **Plan C: Native Android (Kotlin + Compose)** — إذا قرر العميل أن iOS غير مطلوب نهائياً وأن الأداء له الأولوية القصوى.

3. **Plan D: استمرار في الحالي مع إصلاحات** — **لا يُنصح به أبداً** إلا في حالة عدم توفر ميزانية للإعادة الكاملة. في هذه الحالة، راجع `05_security_improvements.md` للإصلاحات الأمنية الإجبارية.

### 8.2 معايير التفعيل (Triggers)

| إذا حصل... | فعّل... |
|------------|---------|
| فشل في بناء TurboModule للطباعة بعد 3 محاولات | Plan B (Flutter) |
| العميل اشترط Android-only صراحة | Plan C (Native Kotlin) |
| الميزانية انخفضت أقل من 30% | Plan D (إصلاحات على الحالي) |

---

## 9. الملخص في جدول واحد

| المعيار | React Native (المختار) | Flutter | Native | KMP |
|---------|------------------------|---------|--------|-----|
| iOS لاحقاً | ✅ | ✅ | ❌ | ✅ |
| Offline-First | ✅ | ✅ | ✅ | ✅ |
| Bluetooth Printer | ✅ | ✅ | ⭐ | ✅ |
| توافق app1 | ✅ ⭐ | ❌ | ❌ | ❌ |
| سرعة التطوير | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| تكلفة الصيانة | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **النتيجة النهائية** | **🏆 الأفضل** | 2 | 3 | 4 |

---

## 10. الخطوة التالية

اقرأ الملف التالي:
👉 **`02_recommended_architecture.md`** — البنية المعمارية التفصيلية للحل المُختار

---

## مراجع
- `01_overview/02_architecture_diagram.md` — البنية الحالية
- `06_business_logic/03_payment_collection.md` — مثال على الحاجة لـ Offline-First
- `app1/` المستودع المرجعي (React Native 0.74.5)

---

> *نهاية `10_rebuild_blueprint/01_tech_stack_options.md`*
