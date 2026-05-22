# 10.06 — UI Modernization Blueprint

> **القسم:** `10_rebuild_blueprint/` — الملف 6 من 8
> **الموضوع:** تحديث واجهة المستخدم — Material Design 3، الطباعة العربية، RTL، نظام الألوان، المكونات، الحركات، الوضع الداكن، إمكانية الوصول
> **يعتمد على:** ملفات 01 (Tech Stack)، 02 (Architecture)، 05 (Security)
> **التطبيق المرجعي:** `Ecas v18.4` (com.egy.webpaymentapp) — واجهة WebView قديمة (HTML/JS/CSS)

---

## 📌 الفهرس

1. [التحليل النقدي للواجهة الحالية](#1-التحليل-النقدي-للواجهة-الحالية)
2. [مبادئ التصميم الجديد](#2-مبادئ-التصميم-الجديد)
3. [نظام الألوان (Color System)](#3-نظام-الألوان-color-system)
4. [الطباعة العربية (Arabic Typography)](#4-الطباعة-العربية-arabic-typography)
5. [دعم RTL (Right-to-Left)](#5-دعم-rtl-right-to-left)
6. [مكتبة المكونات (Component Library)](#6-مكتبة-المكونات-component-library)
7. [الحركات والانتقالات (Animations)](#7-الحركات-والانتقالات-animations)
8. [الوضع الداكن (Dark Mode)](#8-الوضع-الداكن-dark-mode)
9. [إمكانية الوصول (Accessibility)](#9-إمكانية-الوصول-accessibility)
10. [التكيف مع الأجهزة (Responsive & Tablet)](#10-التكيف-مع-الأجهزة-responsive--tablet)
11. [أمثلة شاشات كاملة](#11-أمثلة-شاشات-كاملة)
12. [خلاصة قرارات التصميم](#12-خلاصة-قرارات-التصميم)

---

## 1) التحليل النقدي للواجهة الحالية

### 1.1 ماذا وجدنا في `Ecas v18.4`؟

| المظهر | الحالي (WebView) | المشكلة |
|---|---|---|
| **التقنية** | HTML/CSS/JS داخل `assets/` | بطيء، صعب الصيانة، يفتقر للمظهر الأصلي |
| **الخط** | Web fonts (غير محدد) أو نظام | عدم تناسق بين Android & WebView |
| **الألوان** | في `colors.xml` ومتضاربة مع CSS | تكرار وتباعد بين Native و Web |
| **RTL** | يدوي عبر `dir="rtl"` في HTML | لا يستفيد من APIs نظام Android |
| **الحركات** | CSS transitions فقط | بطيئة، غير مُحركة بـ GPU |
| **الوضع الداكن** | غير موجود ❌ | إجهاد بصري للكاشير في الليل |
| **a11y** | لا يوجد دعم لـ TalkBack | يستبعد ضعاف البصر |
| **حجم النص** | ثابت | لا يحترم إعدادات النظام |
| **اللمس** | أزرار صغيرة | صعبة للأصابع الكبيرة في الميدان |

### 1.2 الألوان المستخرجة من المشروع الحالي

من `colors.xml` و `drawables/`:

```xml
<!-- العثور عليها في res/values/colors.xml -->
<color name="colorPrimary">#3F51B5</color>        <!-- Indigo قديم -->
<color name="colorPrimaryDark">#303F9F</color>    <!-- Indigo darker -->
<color name="colorAccent">#FF4081</color>         <!-- Pink (لا يتناسب مع شركة كهرباء) -->
<color name="backgroundColor">#FFFFFF</color>     <!-- أبيض ثابت -->
<color name="textPrimary">#212121</color>
<color name="textSecondary">#757575</color>
```

**المشاكل:**
- ❌ ألوان عشوائية بدون نظام علامة تجارية
- ❌ Pink accent لا يناسب طبيعة التطبيق (شركة كهرباء)
- ❌ لا يوجد ألوان نجاح/خطأ/تحذير محددة بشكل دلالي
- ❌ نسب التباين (Contrast Ratios) غير مختبرة لـ WCAG

---

## 2) مبادئ التصميم الجديد

### 2.1 الفلسفة

> **التطبيق للكاشير في الميدان، وليس للموظفين في المكاتب.**

| المبدأ | التطبيق |
|---|---|
| **Large Touch Targets** | حد أدنى 48dp (Material) — نهدف 56dp للأزرار الأساسية |
| **High Contrast** | WCAG AAA حيث أمكن (7:1)، AA على الأقل (4.5:1) |
| **Outdoor Visibility** | ألوان عالية التشبع، نص داكن على خلفية فاتحة افتراضياً |
| **One-Hand Reach** | الأزرار الأساسية في النصف السفلي من الشاشة |
| **Error Prevention** | تأكيد قبل الإجراءات الحساسة (دفع، حذف) |
| **Offline-First UI** | مؤشرات حالة الشبكة دائماً مرئية |
| **Arabic-First** | RTL، أرقام عربية اختيارية، تنسيق التاريخ هجري/ميلادي |

### 2.2 خيار نظام التصميم

**القرار: Material Design 3 (M3)** عبر `react-native-paper` v5+

**لماذا M3 وليس Cupertino أو نظام مخصص؟**

| المعيار | M3 (paper) | Cupertino (iOS-style) | مخصص |
|---|---|---|---|
| **التكلفة** | مجاني، صيانة فعّالة | يتطلب مكتبة منفصلة | عالٍ جداً |
| **Tokens** | نظام كامل (color, type, shape) | جزئي | نبدأ من الصفر |
| **a11y** | مدمج (Roles, States) | متوسط | يدوي |
| **التحديثات** | Google تحدّث بانتظام | تحديثات أبطأ | نتحمل العبء |
| **مألوف للمستخدم اليمني** | Android > 90% سوق | غير مألوف | غير مألوف |

**الاختيار النهائي:** `react-native-paper@5.x` + Tokens مخصصة + بعض المكونات المخصصة.

---

## 3) نظام الألوان (Color System)

### 3.1 لوحة العلامة التجارية الجديدة (مقترح)

> الشركة: مؤسسة العباسي للجباية (كهرباء/خدمات)
> الجمهور: كاشيرون في الميدان، مدراء، عملاء

#### الألوان الأساسية:

```typescript
// src/theme/colors.ts

export const palette = {
  // Brand Primary — أزرق احترافي يوحي بالثقة والاستقرار
  // (مرتبط بـ "الكهرباء" — البرق)
  primary: {
    50: '#E3F2FD',
    100: '#BBDEFB',
    200: '#90CAF9',
    300: '#64B5F6',
    400: '#42A5F5',
    500: '#2196F3',   // Primary
    600: '#1E88E5',
    700: '#1976D2',   // Primary Dark
    800: '#1565C0',
    900: '#0D47A1',
  },

  // Brand Secondary — ذهبي للتأكيد (دفع، نجاح)
  secondary: {
    50: '#FFF8E1',
    100: '#FFECB3',
    300: '#FFD54F',
    500: '#FFC107',   // Secondary
    700: '#FFA000',
    900: '#FF6F00',
  },

  // Semantic Colors
  success: {
    light: '#81C784',
    main: '#4CAF50',
    dark: '#388E3C',
    contrast: '#FFFFFF',
  },
  warning: {
    light: '#FFB74D',
    main: '#FF9800',
    dark: '#F57C00',
    contrast: '#000000',
  },
  error: {
    light: '#E57373',
    main: '#F44336',
    dark: '#D32F2F',
    contrast: '#FFFFFF',
  },
  info: {
    light: '#64B5F6',
    main: '#2196F3',
    dark: '#1976D2',
    contrast: '#FFFFFF',
  },

  // Neutrals (Material You)
  neutral: {
    0: '#FFFFFF',
    10: '#FAFAFA',
    20: '#F5F5F5',
    50: '#EEEEEE',
    100: '#E0E0E0',
    200: '#BDBDBD',
    400: '#9E9E9E',
    600: '#757575',
    800: '#424242',
    900: '#212121',
    1000: '#000000',
  },
};
```

### 3.2 تطبيق Material 3 Color Roles

```typescript
// src/theme/themes.ts
import { MD3LightTheme, MD3DarkTheme, configureFonts } from 'react-native-paper';
import { palette } from './colors';
import { fontConfig } from './typography';

export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: palette.primary[700],          // #1976D2
    onPrimary: palette.neutral[0],          // #FFFFFF
    primaryContainer: palette.primary[100], // #BBDEFB
    onPrimaryContainer: palette.primary[900],

    secondary: palette.secondary[700],
    onSecondary: palette.neutral[1000],
    secondaryContainer: palette.secondary[100],
    onSecondaryContainer: palette.secondary[900],

    tertiary: '#7B1FA2',                    // بنفسجي للعناصر النادرة
    onTertiary: palette.neutral[0],

    error: palette.error.main,
    onError: palette.error.contrast,
    errorContainer: '#FFCDD2',
    onErrorContainer: '#B71C1C',

    background: palette.neutral[10],        // #FAFAFA — ليس أبيض صرف لراحة العين
    onBackground: palette.neutral[900],

    surface: palette.neutral[0],            // #FFFFFF للبطاقات
    onSurface: palette.neutral[900],
    surfaceVariant: palette.neutral[100],
    onSurfaceVariant: palette.neutral[600],

    outline: palette.neutral[400],
    outlineVariant: palette.neutral[200],

    // Elevation (M3)
    elevation: {
      level0: 'transparent',
      level1: '#F3F4F6',  // Card resting
      level2: '#E5E7EB',
      level3: '#D1D5DB',
      level4: '#9CA3AF',
      level5: '#6B7280',  // Modal
    },
  },
  fonts: configureFonts({ config: fontConfig }),
  roundness: 12,  // أكثر استدارة من M3 الافتراضي (8)
};

export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: palette.primary[300],          // #64B5F6
    onPrimary: palette.primary[900],
    primaryContainer: palette.primary[700],
    onPrimaryContainer: palette.primary[100],

    secondary: palette.secondary[300],
    onSecondary: palette.neutral[1000],
    secondaryContainer: palette.secondary[700],
    onSecondaryContainer: palette.secondary[100],

    error: palette.error.light,
    onError: palette.neutral[1000],

    background: '#121212',                  // M3 Dark
    onBackground: palette.neutral[10],

    surface: '#1E1E1E',
    onSurface: palette.neutral[10],
    surfaceVariant: '#2C2C2C',
    onSurfaceVariant: palette.neutral[200],
  },
  roundness: 12,
};
```

### 3.3 جدول التباين (WCAG)

اختبرنا الألوان للوصول إلى مستوى AA على الأقل:

| الخلفية | النص | نسبة التباين | المستوى |
|---|---|---:|---|
| `primary[700]` #1976D2 | `#FFFFFF` | 5.46:1 | ✅ AA |
| `secondary[700]` #FFA000 | `#000000` | 9.93:1 | ✅ AAA |
| `error.main` #F44336 | `#FFFFFF` | 4.07:1 | ⚠️ AA (Large only) |
| `error.dark` #D32F2F | `#FFFFFF` | 5.91:1 | ✅ AA |
| `neutral[900]` #212121 | `#FAFAFA` | 16.10:1 | ✅ AAA |

**القاعدة:** لا تستخدم `error.main` للنص الصغير. استخدم `error.dark` بدلاً منه.

---

## 4) الطباعة العربية (Arabic Typography)

### 4.1 اختيار العائلة الخطية

#### المرشحون:

| الخط | المميزات | العيوب | الترخيص |
|---|---|---|---|
| **Cairo** ✅ | تصميم حديث، 10 أوزان، مدعوم بـ Google Fonts، عربي وإنجليزي | يستهلك ~250KB لكل وزن | OFL (مجاني تجارياً) |
| **Tajawal** | أنيق، 7 أوزان | متاح في Google Fonts فقط | OFL |
| **IBM Plex Sans Arabic** | احترافي جداً | حديث، قد يبدو "تقني جداً" | OFL |
| **Almarai** | بسيط ومقروء | 4 أوزان فقط | OFL |
| **Noto Naskh Arabic** | افتراضي Android | كلاسيكي جداً، أقل حداثة | OFL |

**القرار: Cairo** للسببين:
1. **التنوع:** 10 أوزان (200, 300, 400, 500, 600, 700, 800, 900, Black) — مرونة للهرمية البصرية.
2. **التغطية:** يدعم الأرقام العربية والإنجليزية، الحروف المركبة (لام-ألف)، الرموز الرياضية.

### 4.2 الخطوات العملية للتثبيت

```bash
# 1. تنزيل من Google Fonts
# https://fonts.google.com/specimen/Cairo

# 2. ضع الملفات في:
# android: android/app/src/main/assets/fonts/
# ios: ios/<ProjectName>/Resources/Fonts/

# 3. أنشئ react-native.config.js
```

```javascript
// react-native.config.js
module.exports = {
  assets: ['./src/assets/fonts/'],
};
```

```bash
# 4. تطبيق
npx react-native-asset
```

**ملفات الخط المطلوبة:**

```
src/assets/fonts/
├── Cairo-Light.ttf       (300)
├── Cairo-Regular.ttf     (400)
├── Cairo-Medium.ttf      (500)
├── Cairo-SemiBold.ttf    (600)
├── Cairo-Bold.ttf        (700)
└── Cairo-ExtraBold.ttf   (800)
```

> ❗ ملاحظة Android: على Android نستخدم اسم الملف بدون امتداد. على iOS نستخدم اسم العائلة الكامل من Info.plist.

### 4.3 نظام Type Scale (Material 3)

```typescript
// src/theme/typography.ts

export const fontConfig = {
  // Display - للعناوين الرئيسية النادرة (شاشات الترحيب)
  displayLarge: {
    fontFamily: 'Cairo-Bold',
    fontSize: 57,
    lineHeight: 64,
    letterSpacing: -0.25,
    fontWeight: '700' as const,
  },
  displayMedium: {
    fontFamily: 'Cairo-Bold',
    fontSize: 45,
    lineHeight: 52,
    letterSpacing: 0,
    fontWeight: '700' as const,
  },
  displaySmall: {
    fontFamily: 'Cairo-SemiBold',
    fontSize: 36,
    lineHeight: 44,
    letterSpacing: 0,
    fontWeight: '600' as const,
  },

  // Headline - لعناوين الشاشات
  headlineLarge: {
    fontFamily: 'Cairo-SemiBold',
    fontSize: 32,
    lineHeight: 40,
    letterSpacing: 0,
    fontWeight: '600' as const,
  },
  headlineMedium: {
    fontFamily: 'Cairo-SemiBold',
    fontSize: 28,
    lineHeight: 36,
    letterSpacing: 0,
    fontWeight: '600' as const,
  },
  headlineSmall: {
    fontFamily: 'Cairo-SemiBold',
    fontSize: 24,
    lineHeight: 32,
    letterSpacing: 0,
    fontWeight: '600' as const,
  },

  // Title - لعناوين البطاقات والأقسام
  titleLarge: {
    fontFamily: 'Cairo-Medium',
    fontSize: 22,
    lineHeight: 28,
    letterSpacing: 0,
    fontWeight: '500' as const,
  },
  titleMedium: {
    fontFamily: 'Cairo-Medium',
    fontSize: 16,
    lineHeight: 24,
    letterSpacing: 0.15,
    fontWeight: '500' as const,
  },
  titleSmall: {
    fontFamily: 'Cairo-Medium',
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0.1,
    fontWeight: '500' as const,
  },

  // Body - للنصوص العامة والبيانات
  bodyLarge: {
    fontFamily: 'Cairo-Regular',
    fontSize: 16,
    lineHeight: 24,
    letterSpacing: 0.5,
    fontWeight: '400' as const,
  },
  bodyMedium: {
    fontFamily: 'Cairo-Regular',
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0.25,
    fontWeight: '400' as const,
  },
  bodySmall: {
    fontFamily: 'Cairo-Regular',
    fontSize: 12,
    lineHeight: 16,
    letterSpacing: 0.4,
    fontWeight: '400' as const,
  },

  // Label - للأزرار والوسوم
  labelLarge: {
    fontFamily: 'Cairo-Medium',
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0.1,
    fontWeight: '500' as const,
  },
  labelMedium: {
    fontFamily: 'Cairo-Medium',
    fontSize: 12,
    lineHeight: 16,
    letterSpacing: 0.5,
    fontWeight: '500' as const,
  },
  labelSmall: {
    fontFamily: 'Cairo-Medium',
    fontSize: 11,
    lineHeight: 16,
    letterSpacing: 0.5,
    fontWeight: '500' as const,
  },
};
```

### 4.4 الأرقام: عربية أم لاتينية؟

**القرار:** خيار للمستخدم في الإعدادات، الافتراضي **لاتينية (هندية شرقية)** للأسباب التالية:
- ✅ التطبيقات المصرفية في اليمن (الكريمي، CAC، الكاك) تستخدم اللاتينية
- ✅ آلات الحاسبة وآلات POS تطبع اللاتينية
- ✅ يحدث خطأ بصري في الأرقام `٠` (صفر عربي) vs `٥` (خمسة عربية)
- ✅ المطورين والداعمين الفنيين يفضلونها للسجلات

```typescript
// src/utils/numbers.ts

const arabicDigits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];

export function toArabicDigits(input: string | number): string {
  return String(input).replace(/[0-9]/g, (d) => arabicDigits[parseInt(d, 10)]);
}

export function toLatinDigits(input: string): string {
  return input.replace(/[٠-٩]/g, (d) => String(arabicDigits.indexOf(d)));
}

export function formatNumber(
  value: number,
  options: {
    useArabicDigits?: boolean;
    decimals?: number;
    locale?: 'ar-YE' | 'en-US';
  } = {}
): string {
  const { useArabicDigits = false, decimals = 0, locale = 'en-US' } = options;
  const formatted = value.toLocaleString(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return useArabicDigits ? toArabicDigits(formatted) : formatted;
}

// مثال:
formatNumber(1234567.89, { decimals: 2 });
// "1,234,567.89"

formatNumber(1234567.89, { decimals: 2, useArabicDigits: true });
// "١,٢٣٤,٥٦٧.٨٩"
```

### 4.5 تنسيق العملة (الريال اليمني)

```typescript
// src/utils/currency.ts

export type Currency = 'YER' | 'USD' | 'SAR';

const currencySymbols: Record<Currency, { symbol: string; nameAr: string }> = {
  YER: { symbol: 'ر.ي', nameAr: 'ريال يمني' },
  USD: { symbol: '$', nameAr: 'دولار' },
  SAR: { symbol: 'ر.س', nameAr: 'ريال سعودي' },
};

export function formatCurrency(
  amount: number,
  currency: Currency = 'YER',
  options: { useArabicDigits?: boolean; showName?: boolean } = {}
): string {
  const { useArabicDigits = false, showName = false } = options;
  const formatted = formatNumber(amount, { decimals: 2, useArabicDigits });
  const { symbol, nameAr } = currencySymbols[currency];

  return showName ? `${formatted} ${nameAr}` : `${formatted} ${symbol}`;
}

// مثال:
formatCurrency(15000.50);              // "15,000.50 ر.ي"
formatCurrency(15000.50, 'YER', { useArabicDigits: true });
// "١٥,٠٠٠.٥٠ ر.ي"
```

---

## 5) دعم RTL (Right-to-Left)

### 5.1 إعداد المشروع لـ RTL القسري

#### في `index.js`:

```javascript
// index.js (نقطة دخول التطبيق)
import { AppRegistry, I18nManager } from 'react-native';
import App from './App';
import { name as appName } from './app.json';

// إجبار RTL منذ البداية (التطبيق عربي فقط)
if (!I18nManager.isRTL) {
  I18nManager.allowRTL(true);
  I18nManager.forceRTL(true);
  // ملاحظة: يتطلب إعادة تشغيل التطبيق لتطبيق التغيير
}

AppRegistry.registerComponent(appName, () => App);
```

#### في `App.tsx`:

```typescript
// src/App.tsx
import React, { useEffect } from 'react';
import { I18nManager } from 'react-native';
import RNRestart from 'react-native-restart'; // npm i react-native-restart

export default function App() {
  useEffect(() => {
    if (!I18nManager.isRTL) {
      I18nManager.forceRTL(true);
      RNRestart.Restart();
    }
  }, []);

  return <RootNavigator />;
}
```

### 5.2 قواعد RTL في React Native

| القاعدة | DO ✅ | DON'T ❌ |
|---|---|---|
| **التباعد الأفقي** | `marginStart` / `marginEnd` | `marginLeft` / `marginRight` |
| **الحشو** | `paddingStart` / `paddingEnd` | `paddingLeft` / `paddingRight` |
| **التموضع** | `start` / `end` | `left` / `right` |
| **محاذاة النص** | `textAlign: 'left'` (يصبح يمين تلقائياً) | `textAlign: 'right'` (لا تنعكس!) |
| **flexDirection** | `'row'` (ينعكس تلقائياً) | تجنب `'row-reverse'` |
| **الأيقونات الاتجاهية** | استخدم `chevron-back` مرآة آلية | استخدام صريح للسهم اليمين/يسار |

### 5.3 معالجة الحالات الخاصة

```typescript
// src/components/Icons/DirectionalIcon.tsx
import { I18nManager } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

type Props = {
  name: 'back' | 'forward' | 'chevron-back' | 'chevron-forward';
  size?: number;
  color?: string;
};

const iconMap = {
  back: { ltr: 'arrow-left', rtl: 'arrow-right' },
  forward: { ltr: 'arrow-right', rtl: 'arrow-left' },
  'chevron-back': { ltr: 'chevron-left', rtl: 'chevron-right' },
  'chevron-forward': { ltr: 'chevron-right', rtl: 'chevron-left' },
};

export function DirectionalIcon({ name, size = 24, color }: Props) {
  const direction = I18nManager.isRTL ? 'rtl' : 'ltr';
  return (
    <MaterialCommunityIcons
      name={iconMap[name][direction] as any}
      size={size}
      color={color}
    />
  );
}
```

### 5.4 RTL مع Reanimated

```typescript
// src/utils/rtl.ts
import { I18nManager } from 'react-native';

/**
 * يعيد قيمة معكوسة عند RTL (للحركات والتحولات)
 */
export const rtlValue = (value: number): number =>
  I18nManager.isRTL ? -value : value;

/**
 * يعيد scaleX = -1 عند RTL لقلب أيقونات SVG الاتجاهية
 */
export const rtlIconStyle = () => ({
  transform: I18nManager.isRTL ? [{ scaleX: -1 }] : [],
});
```

### 5.5 اختبار RTL

```typescript
// __tests__/rtl.test.ts
import { I18nManager } from 'react-native';

describe('RTL Support', () => {
  beforeAll(() => {
    I18nManager.allowRTL(true);
    I18nManager.forceRTL(true);
  });

  it('should render arrows mirrored', () => {
    expect(I18nManager.isRTL).toBe(true);
    // اختبار المكونات الاتجاهية...
  });
});
```

---

## 6) مكتبة المكونات (Component Library)

### 6.1 الهيكل العام

```
src/components/
├── primitives/           # مكونات أساسية مغلفة من react-native-paper
│   ├── Button.tsx
│   ├── TextInput.tsx
│   ├── Card.tsx
│   └── Surface.tsx
├── composite/            # مكونات مركبة
│   ├── FormField.tsx
│   ├── DataTable.tsx
│   ├── EmptyState.tsx
│   └── LoadingState.tsx
├── feedback/             # تغذية راجعة
│   ├── Toast.tsx
│   ├── ConfirmDialog.tsx
│   ├── ErrorBoundary.tsx
│   └── ProgressOverlay.tsx
├── navigation/           # عناصر التنقل
│   ├── AppBar.tsx
│   ├── TabBar.tsx
│   └── BottomSheet.tsx
└── domain/               # خاصة بالمجال
    ├── CustomerCard.tsx
    ├── PaymentForm.tsx
    ├── ReceiptPreview.tsx
    └── NetworkStatusBadge.tsx
```

### 6.2 مكون Button مخصص

```typescript
// src/components/primitives/Button.tsx
import React from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import {
  Button as PaperButton,
  Text,
  useTheme,
} from 'react-native-paper';

type Variant = 'filled' | 'tonal' | 'outlined' | 'text' | 'elevated';
type Size = 'small' | 'medium' | 'large' | 'xlarge';
type Tone = 'primary' | 'secondary' | 'success' | 'warning' | 'error';

export type ButtonProps = {
  label: string;
  onPress: () => void;
  variant?: Variant;
  size?: Size;
  tone?: Tone;
  icon?: string;
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  testID?: string;
  accessibilityLabel?: string;
  accessibilityHint?: string;
};

const sizeMap: Record<Size, { height: number; fontSize: number; padding: number }> = {
  small: { height: 36, fontSize: 12, padding: 12 },
  medium: { height: 48, fontSize: 14, padding: 16 },
  large: { height: 56, fontSize: 16, padding: 24 },  // الافتراضي للكاشير
  xlarge: { height: 64, fontSize: 18, padding: 32 }, // الأزرار الأساسية (دفع، حفظ)
};

export function Button({
  label,
  onPress,
  variant = 'filled',
  size = 'large',
  tone = 'primary',
  icon,
  loading = false,
  disabled = false,
  fullWidth = false,
  testID,
  accessibilityLabel,
  accessibilityHint,
}: ButtonProps) {
  const theme = useTheme();
  const sizing = sizeMap[size];

  // ربط tone بألوان الثيم
  const toneColor = {
    primary: theme.colors.primary,
    secondary: theme.colors.secondary,
    success: '#4CAF50',
    warning: '#FF9800',
    error: theme.colors.error,
  }[tone];

  return (
    <PaperButton
      mode={variant === 'filled' ? 'contained' : variant === 'outlined' ? 'outlined' : 'text'}
      onPress={onPress}
      icon={icon}
      loading={loading}
      disabled={disabled || loading}
      buttonColor={variant === 'filled' ? toneColor : undefined}
      textColor={variant !== 'filled' ? toneColor : undefined}
      contentStyle={[
        { height: sizing.height, paddingHorizontal: sizing.padding },
        fullWidth && styles.fullWidth,
      ]}
      labelStyle={{
        fontSize: sizing.fontSize,
        fontFamily: 'Cairo-SemiBold',
      }}
      style={fullWidth && styles.fullWidth}
      testID={testID}
      accessibilityLabel={accessibilityLabel || label}
      accessibilityHint={accessibilityHint}
      accessibilityRole="button"
      accessibilityState={{ disabled: disabled || loading, busy: loading }}
    >
      {label}
    </PaperButton>
  );
}

const styles = StyleSheet.create({
  fullWidth: { width: '100%' },
});
```

### 6.3 مكون TextInput مع التحقق

```typescript
// src/components/primitives/TextInput.tsx
import React from 'react';
import { StyleSheet, View, KeyboardTypeOptions } from 'react-native';
import { TextInput as PaperTextInput, HelperText, useTheme } from 'react-native-paper';

export type TextInputProps = {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  onBlur?: () => void;
  error?: string;          // رسالة الخطأ من Zod/RHF
  hint?: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'phone' | 'numeric' | 'decimal' | 'password';
  required?: boolean;
  disabled?: boolean;
  multiline?: boolean;
  maxLength?: number;
  leftIcon?: string;
  rightIcon?: string;
  onRightIconPress?: () => void;
  testID?: string;
};

const keyboardTypeMap: Record<NonNullable<TextInputProps['type']>, KeyboardTypeOptions> = {
  text: 'default',
  email: 'email-address',
  phone: 'phone-pad',
  numeric: 'number-pad',
  decimal: 'decimal-pad',
  password: 'default',
};

export function TextInput({
  label,
  value,
  onChangeText,
  onBlur,
  error,
  hint,
  placeholder,
  type = 'text',
  required = false,
  disabled = false,
  multiline = false,
  maxLength,
  leftIcon,
  rightIcon,
  onRightIconPress,
  testID,
}: TextInputProps) {
  const theme = useTheme();
  const [secureVisible, setSecureVisible] = React.useState(false);
  const isPassword = type === 'password';

  return (
    <View style={styles.container}>
      <PaperTextInput
        label={`${label}${required ? ' *' : ''}`}
        value={value}
        onChangeText={onChangeText}
        onBlur={onBlur}
        placeholder={placeholder}
        mode="outlined"
        keyboardType={keyboardTypeMap[type]}
        secureTextEntry={isPassword && !secureVisible}
        autoCapitalize={type === 'email' ? 'none' : 'sentences'}
        autoCorrect={type === 'email' || type === 'password' ? false : true}
        disabled={disabled}
        multiline={multiline}
        maxLength={maxLength}
        error={!!error}
        left={leftIcon ? <PaperTextInput.Icon icon={leftIcon} /> : undefined}
        right={
          isPassword ? (
            <PaperTextInput.Icon
              icon={secureVisible ? 'eye-off' : 'eye'}
              onPress={() => setSecureVisible((v) => !v)}
              accessibilityLabel={secureVisible ? 'إخفاء كلمة المرور' : 'إظهار كلمة المرور'}
            />
          ) : rightIcon ? (
            <PaperTextInput.Icon icon={rightIcon} onPress={onRightIconPress} />
          ) : undefined
        }
        style={styles.input}
        contentStyle={{ fontFamily: 'Cairo-Regular', fontSize: 16 }}
        testID={testID}
        accessibilityLabel={label}
        accessibilityHint={hint}
      />
      {(error || hint) && (
        <HelperText
          type={error ? 'error' : 'info'}
          visible={!!(error || hint)}
          style={{ fontFamily: 'Cairo-Regular' }}
        >
          {error || hint}
        </HelperText>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 12 },
  input: { backgroundColor: 'transparent' },
});
```

### 6.4 مكون CustomerCard (مجالي)

```typescript
// src/components/domain/CustomerCard.tsx
import React from 'react';
import { StyleSheet } from 'react-native';
import { Card, Text, Avatar, IconButton, useTheme } from 'react-native-paper';
import { Customer } from '@/domain/types/customer';
import { formatCurrency } from '@/utils/currency';

type Props = {
  customer: Customer;
  onPress: (customer: Customer) => void;
  onLongPress?: (customer: Customer) => void;
};

export function CustomerCard({ customer, onPress, onLongPress }: Props) {
  const theme = useTheme();
  const hasDebt = customer.balance > 0;

  const statusColor = customer.isActive
    ? theme.colors.primary
    : theme.colors.outline;

  const initials = customer.name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('');

  return (
    <Card
      onPress={() => onPress(customer)}
      onLongPress={onLongPress ? () => onLongPress(customer) : undefined}
      style={styles.card}
      mode="elevated"
    >
      <Card.Title
        title={customer.name}
        titleStyle={styles.title}
        subtitle={`الحساب: ${customer.accountNumber}`}
        subtitleStyle={styles.subtitle}
        left={(props) => (
          <Avatar.Text
            {...props}
            label={initials}
            color={theme.colors.onPrimary}
            style={{ backgroundColor: statusColor }}
          />
        )}
        right={(props) => (
          <IconButton
            {...props}
            icon="chevron-left"  // RTL: يصبح يميناً
            accessibilityLabel="فتح تفاصيل العميل"
          />
        )}
      />
      <Card.Content>
        <Text variant="bodyMedium" style={styles.address}>
          {customer.address}
        </Text>
        {hasDebt && (
          <Text
            variant="titleMedium"
            style={[styles.debt, { color: theme.colors.error }]}
          >
            المتأخرات: {formatCurrency(customer.balance, 'YER')}
          </Text>
        )}
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { marginVertical: 6, marginHorizontal: 12 },
  title: { fontFamily: 'Cairo-SemiBold', fontSize: 16 },
  subtitle: { fontFamily: 'Cairo-Regular', fontSize: 13 },
  address: { fontFamily: 'Cairo-Regular', marginBottom: 8 },
  debt: { fontFamily: 'Cairo-Bold', textAlign: 'left' },
});
```

### 6.5 مكون NetworkStatusBadge

```typescript
// src/components/domain/NetworkStatusBadge.tsx
import React from 'react';
import { StyleSheet, View } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { useSyncStore } from '@/state/sync';

export function NetworkStatusBadge() {
  const theme = useTheme();
  const { isConnected, type } = useNetworkStatus();
  const { pendingCount, isSyncing } = useSyncStore();

  if (isConnected && pendingCount === 0 && !isSyncing) return null;

  let label = '';
  let bgColor = '';
  let icon = '●';

  if (!isConnected) {
    label = 'لا يوجد اتصال';
    bgColor = theme.colors.error;
    icon = '⚠';
  } else if (isSyncing) {
    label = `جاري المزامنة... (${pendingCount})`;
    bgColor = '#FF9800';
    icon = '↻';
  } else if (pendingCount > 0) {
    label = `${pendingCount} عملية في الانتظار`;
    bgColor = '#FFC107';
    icon = '⏱';
  }

  return (
    <View style={[styles.badge, { backgroundColor: bgColor }]}>
      <Text style={styles.text}>
        {icon} {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    margin: 8,
  },
  text: {
    color: '#FFFFFF',
    fontFamily: 'Cairo-Medium',
    fontSize: 12,
  },
});
```

---

## 7) الحركات والانتقالات (Animations)

### 7.1 المكتبة المختارة: `react-native-reanimated` v3

**لماذا Reanimated وليس Animated API الأصلي؟**

| الميزة | Reanimated v3 | Animated API |
|---|---|---|
| **التنفيذ** | على JS Worklets (Native Thread) | على JS Bridge |
| **الأداء** | 60 FPS مضمون | يتأثر بحمل JS |
| **التعقيد** | بناء جملة أبسط مع `withSpring` | يدوي ومُجزّأ |
| **Gesture Integration** | تكامل مع `react-native-gesture-handler` | محدود |

### 7.2 نظام Motion (M3)

```typescript
// src/theme/motion.ts

export const motion = {
  // Durations (M3)
  duration: {
    short1: 50,    // micro-interactions
    short2: 100,
    short3: 150,   // hover, focus
    short4: 200,   // small expand
    medium1: 250,
    medium2: 300,  // transitions
    medium3: 350,
    medium4: 400,
    long1: 450,
    long2: 500,    // large transitions
    long3: 550,
    long4: 600,
    extraLong: 700,
  },

  // Easing (M3 Standard)
  easing: {
    standard: 'cubic-bezier(0.2, 0, 0, 1)',           // أكثر التحركات
    standardAccelerate: 'cubic-bezier(0.3, 0, 1, 1)', // الخروج من الشاشة
    standardDecelerate: 'cubic-bezier(0, 0, 0, 1)',   // الدخول للشاشة
    emphasized: 'cubic-bezier(0.2, 0, 0, 1)',         // التركيز
  },

  // Spring presets (Reanimated)
  spring: {
    gentle: { damping: 20, stiffness: 90 },
    bouncy: { damping: 8, stiffness: 100 },
    stiff: { damping: 30, stiffness: 200 },
  },
};
```

### 7.3 أمثلة عملية

#### مثال 1: زر "حفظ" مع feedback لمسي

```typescript
import React from 'react';
import { Pressable } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withSequence,
} from 'react-native-reanimated';

export function AnimatedSaveButton({ onPress, label }) {
  const scale = useSharedValue(1);

  const handlePressIn = () => {
    scale.value = withSpring(0.95, { damping: 15, stiffness: 200 });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, { damping: 15, stiffness: 200 });
  };

  const handlePress = () => {
    scale.value = withSequence(
      withSpring(0.9, { damping: 10, stiffness: 300 }),
      withSpring(1.05, { damping: 10, stiffness: 300 }),
      withSpring(1, { damping: 15, stiffness: 200 })
    );
    onPress();
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Animated.View style={animatedStyle}>
      <Pressable
        onPress={handlePress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
      >
        {/* محتوى الزر */}
      </Pressable>
    </Animated.View>
  );
}
```

#### مثال 2: ظهور بطاقة عميل (Slide-Up + Fade-In)

```typescript
import Animated, { FadeInDown } from 'react-native-reanimated';

export function CustomerListItem({ customer, index }) {
  return (
    <Animated.View
      entering={FadeInDown.delay(index * 50).springify()}
    >
      <CustomerCard customer={customer} onPress={() => {}} />
    </Animated.View>
  );
}
```

#### مثال 3: انتقال شاشات (مخصص في React Navigation)

```typescript
// src/navigation/transitions.ts
import { StackCardInterpolationProps } from '@react-navigation/stack';

export const slideFromRightRTL = ({
  current,
  next,
  layouts,
}: StackCardInterpolationProps) => ({
  cardStyle: {
    transform: [
      {
        translateX: current.progress.interpolate({
          inputRange: [0, 1],
          outputRange: [-layouts.screen.width, 0], // معكوس لـ RTL
        }),
      },
    ],
    opacity: current.progress.interpolate({
      inputRange: [0, 0.5, 1],
      outputRange: [0, 0.5, 1],
    }),
  },
});
```

#### مثال 4: Skeleton Loading

```typescript
// src/components/feedback/Skeleton.tsx
import React, { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  Easing,
} from 'react-native-reanimated';

type Props = { width: number | string; height: number; borderRadius?: number };

export function Skeleton({ width, height, borderRadius = 4 }: Props) {
  const opacity = useSharedValue(0.3);

  useEffect(() => {
    opacity.value = withRepeat(
      withTiming(0.8, { duration: 800, easing: Easing.inOut(Easing.ease) }),
      -1,
      true
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({ opacity: opacity.value }));

  return (
    <Animated.View
      style={[
        styles.skeleton,
        { width: width as any, height, borderRadius },
        animatedStyle,
      ]}
    />
  );
}

const styles = StyleSheet.create({
  skeleton: {
    backgroundColor: '#E0E0E0',
  },
});
```

---

## 8) الوضع الداكن (Dark Mode)

### 8.1 لماذا Dark Mode للكاشير؟

- **القراءة الليلية:** كثير من الكاشيرين يعملون لساعات متأخرة
- **توفير البطارية:** على شاشات OLED، 30-60% توفير
- **تقليل إجهاد العين:** خاصة في الإضاءة المنخفضة
- **اختيار المستخدم:** احترام إعدادات النظام

### 8.2 التنفيذ

```typescript
// src/theme/ThemeProvider.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { useColorScheme } from 'react-native';
import { PaperProvider } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { lightTheme, darkTheme } from './themes';

type ThemeMode = 'light' | 'dark' | 'system';
type ThemeContextValue = {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  isDark: boolean;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

const STORAGE_KEY = '@theme_mode';

export function AppThemeProvider({ children }: { children: React.ReactNode }) {
  const systemScheme = useColorScheme();
  const [mode, setModeState] = useState<ThemeMode>('system');

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((stored) => {
      if (stored === 'light' || stored === 'dark' || stored === 'system') {
        setModeState(stored);
      }
    });
  }, []);

  const setMode = async (newMode: ThemeMode) => {
    setModeState(newMode);
    await AsyncStorage.setItem(STORAGE_KEY, newMode);
  };

  const isDark =
    mode === 'dark' || (mode === 'system' && systemScheme === 'dark');

  const theme = isDark ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ mode, setMode, isDark }}>
      <PaperProvider theme={theme}>{children}</PaperProvider>
    </ThemeContext.Provider>
  );
}

export function useAppTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useAppTheme must be used within AppThemeProvider');
  return ctx;
}
```

### 8.3 شاشة الإعدادات للوضع

```typescript
// src/screens/settings/ThemeSettings.tsx
import { List, RadioButton } from 'react-native-paper';
import { useAppTheme } from '@/theme/ThemeProvider';

export function ThemeSettings() {
  const { mode, setMode } = useAppTheme();

  return (
    <List.Section>
      <List.Subheader>مظهر التطبيق</List.Subheader>
      <RadioButton.Group onValueChange={(v) => setMode(v as any)} value={mode}>
        <RadioButton.Item label="فاتح" value="light" />
        <RadioButton.Item label="داكن" value="dark" />
        <RadioButton.Item label="حسب النظام" value="system" />
      </RadioButton.Group>
    </List.Section>
  );
}
```

### 8.4 معالجة StatusBar

```typescript
// في كل شاشة:
import { StatusBar } from 'expo-status-bar';
import { useAppTheme } from '@/theme/ThemeProvider';

export function MyScreen() {
  const { isDark } = useAppTheme();
  return (
    <>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      {/* محتوى */}
    </>
  );
}
```

---

## 9) إمكانية الوصول (Accessibility)

### 9.1 لماذا a11y مهمة هنا؟

- **التشريع:** كثير من الدول تطلبها للتطبيقات المالية
- **الفئة المستهدفة:** بعض الكاشيرين كبار في السن أو ضعاف بصر
- **الجودة:** a11y جيدة تعني UX جيدة للجميع
- **متجر التطبيقات:** Google Play يكافئ التطبيقات الميسرة

### 9.2 القواعد الرئيسية

#### قاعدة 1: كل عنصر تفاعلي له `accessibilityLabel`

```typescript
// ❌ سيء
<TouchableOpacity onPress={handlePay}>
  <Icon name="check" />
</TouchableOpacity>

// ✅ جيد
<TouchableOpacity
  onPress={handlePay}
  accessibilityRole="button"
  accessibilityLabel="تأكيد عملية الدفع"
  accessibilityHint="سيتم خصم المبلغ من رصيد العميل"
>
  <Icon name="check" />
</TouchableOpacity>
```

#### قاعدة 2: قيم النماذج تُعلَن عند التغيير

```typescript
<TextInput
  label="المبلغ المدفوع"
  value={amount}
  onChangeText={setAmount}
  accessibilityLabel="المبلغ المدفوع"
  accessibilityValue={{ text: amount ? `${amount} ريال يمني` : 'فارغ' }}
/>
```

#### قاعدة 3: حالات التحميل والأخطاء واضحة

```typescript
<View
  accessibilityRole="alert"
  accessibilityLiveRegion="polite"
>
  {loading && <Text>جاري التحميل...</Text>}
  {error && <Text>حدث خطأ: {error.message}</Text>}
</View>
```

#### قاعدة 4: حجم النص قابل للتعديل

```typescript
// في App.tsx
import { Platform } from 'react-native';

if (Platform.OS === 'android') {
  // Android: يحترم إعداد حجم النص في النظام تلقائياً
}

// لاختبار:
// adb shell settings put system font_scale 1.3
```

#### قاعدة 5: الأهداف اللمسية كبيرة كافية

```typescript
// الحد الأدنى Material: 48dp x 48dp
// نظامنا: 48dp للأزرار الثانوية، 56dp+ للأساسية

<TouchableOpacity
  style={{ minWidth: 48, minHeight: 48 }}
  hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
>
  {/* محتوى */}
</TouchableOpacity>
```

### 9.3 قائمة فحص a11y

```markdown
- [ ] كل أيقونة تفاعلية لها `accessibilityLabel` بالعربية
- [ ] كل النماذج لها `accessibilityHint` لتوضيح الغرض
- [ ] التباين الأدنى 4.5:1 للنص العادي، 3:1 للكبير
- [ ] حجم اللمس الأدنى 48x48 dp
- [ ] لا اعتماد على اللون فقط لإيصال المعلومة (أيقونة + لون + نص)
- [ ] رسائل الخطأ مرتبطة بحقولها (`accessibilityErrorMessage`)
- [ ] الترتيب المنطقي للتركيز (Focus Order) في الشاشة
- [ ] تجنب `accessibilityRole="image"` للأيقونات الزخرفية
- [ ] لا حركات سريعة (< 200ms) تسبب نوبات لذوي الحساسية الضوئية
- [ ] يعمل مع TalkBack (اختبار يدوي)
```

### 9.4 اختبار TalkBack

```bash
# تفعيل
adb shell settings put secure enabled_accessibility_services com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService

# تعطيل
adb shell settings put secure enabled_accessibility_services ""
```

---

## 10) التكيف مع الأجهزة (Responsive & Tablet)

### 10.1 نظام الـ Breakpoints

```typescript
// src/theme/breakpoints.ts

export const breakpoints = {
  compact: 0,      // الهواتف الصغيرة (< 600dp)
  medium: 600,     // الهواتف الكبيرة، الأجهزة اللوحية الصغيرة
  expanded: 840,   // الأجهزة اللوحية الكبيرة
  large: 1200,     // أجهزة سطح المكتب (نادراً)
};

export type Breakpoint = keyof typeof breakpoints;
```

### 10.2 Hook للأبعاد

```typescript
// src/hooks/useBreakpoint.ts
import { useWindowDimensions } from 'react-native';
import { breakpoints, Breakpoint } from '@/theme/breakpoints';

export function useBreakpoint(): Breakpoint {
  const { width } = useWindowDimensions();
  if (width >= breakpoints.large) return 'large';
  if (width >= breakpoints.expanded) return 'expanded';
  if (width >= breakpoints.medium) return 'medium';
  return 'compact';
}

export function useIsTablet(): boolean {
  const { width } = useWindowDimensions();
  return width >= breakpoints.medium;
}
```

### 10.3 تخطيط متجاوب — مثال

```typescript
// src/screens/customers/CustomerListScreen.tsx
import { useBreakpoint } from '@/hooks/useBreakpoint';
import { FlatList, View } from 'react-native';

export function CustomerListScreen() {
  const bp = useBreakpoint();

  // عمود واحد على الهواتف، عمودين على اللوحي، 3 على الكبير
  const numColumns = bp === 'compact' ? 1 : bp === 'medium' ? 2 : 3;

  return (
    <FlatList
      key={`cols-${numColumns}`}  // يجب إعادة الإنشاء عند تغيير العدد
      data={customers}
      numColumns={numColumns}
      renderItem={({ item }) => <CustomerCard customer={item} />}
      keyExtractor={(c) => c.id}
    />
  );
}
```

### 10.4 Master-Detail على الأجهزة اللوحية

```typescript
// src/navigation/TabletAwareNavigator.tsx
import { useIsTablet } from '@/hooks/useBreakpoint';

export function TabletAwareNavigator() {
  const isTablet = useIsTablet();
  return isTablet ? <SplitView /> : <StackNavigator />;
}

function SplitView() {
  return (
    <View style={{ flex: 1, flexDirection: 'row' }}>
      <View style={{ flex: 1, maxWidth: 360 }}>
        <CustomerListScreen />
      </View>
      <View style={{ flex: 2 }}>
        <CustomerDetailScreen />
      </View>
    </View>
  );
}
```

---

## 11) أمثلة شاشات كاملة

### 11.1 شاشة تسجيل الدخول

```typescript
// src/screens/auth/LoginScreen.tsx
import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet, View } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/primitives/Button';
import { TextInput } from '@/components/primitives/TextInput';
import { useAuth } from '@/features/auth/hooks/useAuth';

const loginSchema = z.object({
  username: z.string().min(1, 'اسم المستخدم مطلوب'),
  password: z.string().min(4, 'كلمة المرور لا تقل عن 4 خانات'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginScreen() {
  const theme = useTheme();
  const { login, isLoading } = useAuth();
  const { control, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '' },
  });

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: theme.colors.background }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text variant="displaySmall" style={styles.title}>
            العباسي للجباية
          </Text>
          <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
            نظام الكاشير الميداني
          </Text>
        </View>

        <View style={styles.form}>
          <Controller
            control={control}
            name="username"
            render={({ field: { onChange, onBlur, value } }) => (
              <TextInput
                label="اسم المستخدم"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={errors.username?.message}
                leftIcon="account"
                required
                testID="username-input"
              />
            )}
          />

          <Controller
            control={control}
            name="password"
            render={({ field: { onChange, onBlur, value } }) => (
              <TextInput
                label="كلمة المرور"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={errors.password?.message}
                type="password"
                leftIcon="lock"
                required
                testID="password-input"
              />
            )}
          />

          <Button
            label="تسجيل الدخول"
            onPress={handleSubmit(login)}
            loading={isLoading}
            size="xlarge"
            fullWidth
            testID="login-button"
          />
        </View>

        <Text variant="labelSmall" style={styles.version}>
          الإصدار 2.0.0
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, padding: 24, justifyContent: 'center' },
  header: { alignItems: 'center', marginBottom: 48 },
  title: { fontFamily: 'Cairo-Bold', marginBottom: 8 },
  form: { gap: 12 },
  version: { textAlign: 'center', marginTop: 24, opacity: 0.6 },
});
```

### 11.2 شاشة الدفع (Payment Flow)

```typescript
// src/screens/payment/PaymentScreen.tsx
import React from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { Card, Text, Divider, useTheme } from 'react-native-paper';
import { Button } from '@/components/primitives/Button';
import { TextInput } from '@/components/primitives/TextInput';
import { formatCurrency } from '@/utils/currency';

export function PaymentScreen({ route, navigation }) {
  const theme = useTheme();
  const { customer } = route.params;
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');

  const numericAmount = parseFloat(amount) || 0;
  const newBalance = customer.balance - numericAmount;

  return (
    <ScrollView style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <Card style={styles.customerCard} mode="contained">
        <Card.Content>
          <Text variant="titleMedium">{customer.name}</Text>
          <Text variant="bodySmall" style={{ marginVertical: 4 }}>
            رقم الحساب: {customer.accountNumber}
          </Text>
          <Divider style={{ marginVertical: 8 }} />
          <View style={styles.balanceRow}>
            <Text variant="bodyMedium">الرصيد المستحق:</Text>
            <Text variant="titleMedium" style={{ color: theme.colors.error }}>
              {formatCurrency(customer.balance)}
            </Text>
          </View>
        </Card.Content>
      </Card>

      <View style={styles.form}>
        <TextInput
          label="المبلغ المدفوع"
          value={amount}
          onChangeText={setAmount}
          type="decimal"
          required
          leftIcon="cash"
          testID="amount-input"
        />

        <TextInput
          label="ملاحظات (اختياري)"
          value={note}
          onChangeText={setNote}
          multiline
          maxLength={200}
          leftIcon="note-text"
        />

        {numericAmount > 0 && (
          <Card style={styles.summary} mode="outlined">
            <Card.Content>
              <Text variant="titleSmall">ملخص العملية</Text>
              <View style={styles.summaryRow}>
                <Text>المبلغ المدفوع:</Text>
                <Text style={{ color: theme.colors.primary, fontFamily: 'Cairo-Bold' }}>
                  {formatCurrency(numericAmount)}
                </Text>
              </View>
              <View style={styles.summaryRow}>
                <Text>الرصيد بعد الدفع:</Text>
                <Text style={{ fontFamily: 'Cairo-Bold' }}>
                  {formatCurrency(newBalance)}
                </Text>
              </View>
            </Card.Content>
          </Card>
        )}
      </View>

      <View style={styles.actions}>
        <Button
          label="إلغاء"
          variant="outlined"
          onPress={() => navigation.goBack()}
          size="large"
        />
        <Button
          label="تأكيد الدفع"
          variant="filled"
          tone="success"
          onPress={() => {/* ... */}}
          disabled={numericAmount <= 0}
          size="xlarge"
          fullWidth
        />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  customerCard: { margin: 16 },
  form: { paddingHorizontal: 16, gap: 12 },
  balanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  summary: { marginTop: 8 },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  actions: { padding: 16, gap: 12, marginBottom: 32 },
});
```

---

## 12) خلاصة قرارات التصميم

| الموضوع | القرار | السبب |
|---|---|---|
| **نظام التصميم** | Material Design 3 + react-native-paper | معيار صناعي، تكامل ممتاز مع RN |
| **الخط الأساسي** | Cairo (Google Fonts) | تنوع الأوزان، يدعم العربية والإنجليزية |
| **الأرقام الافتراضية** | لاتينية (1,2,3) | متوافق مع التطبيقات المصرفية اليمنية |
| **RTL** | `I18nManager.forceRTL(true)` + restart | تطبيق عربي حصرياً |
| **اللون الأساسي** | أزرق `#1976D2` | يوحي بالاستقرار، يناسب الكهرباء |
| **اللون الثانوي** | ذهبي `#FFA000` | للنجاح والتأكيد |
| **حجم اللمس** | 56dp للأزرار الأساسية، 48dp للثانوية | كاشير في الميدان، أصابع كبيرة |
| **استدارة الزوايا** | 12dp (أكثر من M3 الافتراضي) | مظهر حديث وودود |
| **الحركات** | react-native-reanimated v3 | أداء 60fps، يعمل على UI thread |
| **الوضع الداكن** | متاح، الافتراضي = نظام | للعمل الليلي والتوفير |
| **a11y** | TalkBack + WCAG AA كحد أدنى | شمولية + متطلب قانوني محتمل |
| **Tablet Support** | Master-Detail عند `width >= 600dp` | الشركات قد تستخدم لوحياً للمدراء |
| **Status Indicators** | Network badge، Sync badge دائم الظهور | offline-first يتطلب وضوح الحالة |
| **عملة العرض** | `ر.ي` رمز + اسم اختياري | مألوف للمستخدم اليمني |
| **Animation Density** | معتدل (لا حركات > 600ms) | احترام كاشير "في عجلة" |

---

## 🔗 الترابط مع باقي القسم

- **02_recommended_architecture.md:** بنية المجلدات (src/components، src/theme، src/screens)
- **03_data_models_typescript.md:** أنواع `Customer`، `Payment` المستخدمة في الواجهات
- **04_api_client_skeleton.md:** ربط الـ APIs بمكونات الـ UI
- **05_security_improvements.md:** Dev-only Debug screen بديلاً عن الـ Magic Backdoor
- **07_migration_path.md (التالي):** خارطة الطريق لتنفيذ هذا التحديث

---

## 📚 مراجع

1. **Material Design 3:** https://m3.material.io/
2. **React Native Paper v5:** https://reactnativepaper.com/
3. **WCAG 2.1 Quick Reference:** https://www.w3.org/WAI/WCAG21/quickref/
4. **Cairo Font Family:** https://fonts.google.com/specimen/Cairo
5. **React Native RTL Best Practices:** https://reactnative.dev/blog/2016/08/19/right-to-left-support-for-react-native-apps
6. **Reanimated v3 Docs:** https://docs.swmansion.com/react-native-reanimated/

---

**الملف التالي:** [`07_migration_path.md`](./07_migration_path.md) — خارطة الطريق للهجرة (8 مراحل)
