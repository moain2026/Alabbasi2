# 10.07 — Migration Path (خارطة الهجرة)

> **القسم:** `10_rebuild_blueprint/` — الملف 7 من 8
> **الموضوع:** خارطة طريق مرحلية ومنظمة لاستبدال `Ecas v18.4` بتطبيق React Native الجديد
> **المخاطبون:** فريق التطوير، إدارة المشروع، فريق العمليات
> **يعتمد على:** كل الملفات السابقة في `10_rebuild_blueprint/` (01-06)

---

## 📌 الفهرس

1. [الخلاصة التنفيذية](#1-الخلاصة-التنفيذية)
2. [مبادئ الهجرة](#2-مبادئ-الهجرة)
3. [خارطة الزمن الإجمالية](#3-خارطة-الزمن-الإجمالية)
4. [المرحلة 0: التحضير](#4-المرحلة-0-التحضير-week--1)
5. [المرحلة 1: التأسيس](#5-المرحلة-1-التأسيس-week-1-2)
6. [المرحلة 2: المصادقة والتنقل](#6-المرحلة-2-المصادقة-والتنقل-week-3-4)
7. [المرحلة 3: العملاء + قاعدة بيانات](#7-المرحلة-3-العملاء--قاعدة-بيانات-week-5-7)
8. [المرحلة 4: الدفع + الطابعة](#8-المرحلة-4-الدفع--الطابعة-week-8-10)
9. [المرحلة 5: قراءة العداد + الصور](#9-المرحلة-5-قراءة-العداد--الصور-week-11-12)
10. [المرحلة 6: التقارير + إزالة WebView](#10-المرحلة-6-التقارير--إزالة-webview-week-13-14)
11. [المرحلة 7: الاختبار التجريبي](#11-المرحلة-7-الاختبار-التجريبي-week-15-17)
12. [المرحلة 8: التحول النهائي](#12-المرحلة-8-التحول-النهائي-week-18-20)
13. [هجرة البيانات](#13-هجرة-البيانات-من-التطبيق-القديم)
14. [استراتيجيات التراجع (Rollback)](#14-استراتيجيات-التراجع-rollback)
15. [مخاطر وتخفيفات](#15-مخاطر-وتخفيفات)

---

## 1) الخلاصة التنفيذية

### 1.1 الموقف الحالي

- **التطبيق الحالي:** `com.egy.webpaymentapp` Ecas v18.4 — Android Native + WebView
- **المستخدمون النشطون:** كاشيرون ميدانيون (عدد غير محدد، يُفترض 50-500)
- **الأجهزة:** Android 5.0+، Bluetooth POS Printers
- **الكود المصدري:** غير متاح، فقط APK + هندسة عكسية
- **المخاطر:** 20 ثغرة أمنية مصنفة (V1-V20)، أعطال حرجة (`Pay_amount` bug)

### 1.2 الاستراتيجية

> **Big Bang vs. Incremental:** نختار **Incremental with Parallel Run**

| النهج | المميزات | العيوب | قرارنا |
|---|---|---|---|
| **Big Bang** (إعادة كتابة كاملة ثم إطلاق) | بسيط، تطوير سريع | مخاطر عالية، توقف العمل | ❌ |
| **Strangler Fig** (استبدال تدريجي لكل ميزة) | تقليل المخاطر، تعلم سريع | يتطلب WebView في الجديد | ⚠️ ممكن |
| **Parallel Run** (نسختان تعملان جنباً لجنب) | أمان عالي، مقارنة دقيقة | يتطلب موارد إضافية، تدريب مزدوج | ✅ **مختار** |

### 1.3 الجدول الزمني الإجمالي

```
الأسابيع: 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
        ━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━─━━
M0: ▓▓     التحضير
M1:    ▓▓▓▓   التأسيس
M2:          ▓▓▓▓   المصادقة + التنقل
M3:                ▓▓▓▓▓▓   العملاء + DB
M4:                         ▓▓▓▓▓▓   الدفع + الطابعة
M5:                                  ▓▓▓▓   القراءة + الصور
M6:                                        ▓▓▓▓   التقارير
M7:                                              ▓▓▓▓▓▓   البيتا
M8:                                                       ▓▓▓▓▓▓   التحول
```

**إجمالي المدة:** ~20 أسبوع (5 أشهر) للإصدار 1.0
**الفريق المقترح:** 1 PM، 2 RN Devs، 1 Backend Dev (للتعديلات على API)، 1 QA، 1 UX/UI

---

## 2) مبادئ الهجرة

### 2.1 المبادئ الذهبية

| # | المبدأ | التطبيق |
|---|---|---|
| 1 | **لا انقطاع للعمل** | التطبيق القديم يبقى يعمل حتى نهاية المرحلة 8 |
| 2 | **قابلية التراجع** | كل مرحلة لها rollback plan |
| 3 | **اختبار مبكر** | تشغيل تجريبي مع كاشير واحد بدءاً من المرحلة 4 |
| 4 | **توافق الباك-إند** | لا تغيير في الـ API الموجود حتى نهاية المرحلة 6 |
| 5 | **توثيق مستمر** | قرارات معمارية في ADR (Architecture Decision Records) |
| 6 | **مقاييس واقعية** | KPIs قابلة للقياس قبل وبعد |
| 7 | **تدريب موازٍ** | تدريب الكاشيرين والدعم الفني بالتوازي مع التطوير |

### 2.2 مقاييس النجاح (KPIs)

```typescript
// مقاييس قبل وبعد الهجرة

interface MigrationKPIs {
  // الأداء
  appStartTime: number;          // قبل: ~3s | هدف: <1.5s
  loginToHome: number;            // قبل: ~5s | هدف: <2s
  customerSearch: number;         // قبل: ~2s | هدف: <500ms
  paymentSubmission: number;      // قبل: ~3s | هدف: <1.5s

  // الموثوقية
  crashRateAndroid: number;       // قبل: ~5% | هدف: <0.5%
  apiSuccessRate: number;         // قبل: ~85% | هدف: >98%
  syncSuccessRate: number;        // قبل: N/A | هدف: >99% (جديد)

  // تجربة المستخدم
  npsScore: number;               // قياس قبل وبعد
  tasksCompletedPerHour: number;  // إنتاجية الكاشير
  trainingTimeMinutes: number;    // وقت تدريب كاشير جديد

  // الأمان
  securityIssuesOpen: number;     // قبل: 20 | هدف: 0
}
```

---

## 3) خارطة الزمن الإجمالية

### 3.1 جدول المراحل

| المرحلة | المدة | الأسابيع | الناتج الرئيسي |
|---|---|---|---|
| **M0** | 1 أسبوع | -1 إلى 0 | بيئة التطوير جاهزة |
| **M1** | 2 أسبوع | 1-2 | مشروع RN يقلع، CI/CD |
| **M2** | 2 أسبوع | 3-4 | شاشات تسجيل دخول + تنقل أساسي |
| **M3** | 3 أسابيع | 5-7 | عملاء + WatermelonDB + بحث offline |
| **M4** | 3 أسابيع | 8-10 | دفع كامل + طابعة Bluetooth + إيصالات |
| **M5** | 2 أسبوع | 11-12 | قراءة عداد + رفع صور |
| **M6** | 2 أسبوع | 13-14 | تقارير + إزالة WebView |
| **M7** | 3 أسابيع | 15-17 | بيتا داخلي + ميداني + إصلاحات |
| **M8** | 3 أسابيع | 18-20 | إطلاق تدريجي + إيقاف القديم |

### 3.2 المعالم (Milestones) الرئيسية

```
🏁 M0 End: بيئة تطوير وفريق جاهز
🏁 M1 End: "Hello World" يعمل على أجهزة الكاشيرين
🏁 M2 End: كاشير يستطيع تسجيل الدخول والتنقل
🏁 M3 End: كاشير يستطيع البحث عن العملاء offline
🏁 M4 End: كاشير يستطيع تنفيذ دفع كامل وطباعة إيصال ⭐ (MVP)
🏁 M5 End: كاشير يستطيع تسجيل قراءة عداد مع صورة
🏁 M6 End: كل وظائف WebView مستبدلة (Feature Complete)
🏁 M7 End: تطبيق مستقر مع 5+ كاشيرين في الميدان
🏁 M8 End: 100% من الكاشيرين على التطبيق الجديد، القديم متوقف
```

---

## 4) المرحلة 0: التحضير (Week -1)

### 4.1 الأهداف

- إعداد البيئة والأدوات
- تأكيد المتطلبات النهائية مع الأعمال
- إنشاء الـ Backlog الأولي

### 4.2 المهام التفصيلية

#### 4.2.1 البنية التحتية للتطوير

```bash
# 1. إنشاء مستودع جديد على GitHub
gh repo create AbbasiyCashiers-RN --private

# 2. إعداد قواعد فرع
# - main: محمي، يتطلب PR + 2 reviewers
# - develop: للدمج اليومي
# - feature/*: فروع الميزات

# 3. ربط أدوات الجودة
# - SonarCloud (تحليل ساكن)
# - CodeCov (تغطية الاختبارات)
# - Snyk (فحص التبعيات)
```

#### 4.2.2 أدوات المطور المطلوبة

```yaml
# .nvmrc
20.10.0  # Node LTS

# الأدوات المطلوبة لكل مطور:
- Node.js v20+
- Yarn v3+ (workspaces)
- JDK 17
- Android Studio (Hedgehog أو أحدث)
- Xcode 15+ (للمطورين Mac)
- Watchman
- React Native Debugger / Flipper
- VSCode + Extensions:
  - ESLint
  - Prettier
  - React Native Tools
  - TypeScript Importer
```

#### 4.2.3 إعداد CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'
      - run: yarn install --frozen-lockfile
      - run: yarn lint
      - run: yarn typecheck
      - run: yarn test --coverage
      - uses: codecov/codecov-action@v3

  build-android:
    needs: lint-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: yarn install --frozen-lockfile
      - run: cd android && ./gradlew assembleDebug
      - uses: actions/upload-artifact@v4
        with:
          name: app-debug.apk
          path: android/app/build/outputs/apk/debug/app-debug.apk
```

#### 4.2.4 جلسات Discovery

- **مع الأعمال:** تحديد الميزات MUST-HAVE vs NICE-TO-HAVE
- **مع الكاشيرين:** Shadowing لـ 3 كاشيرين لمدة يوم كامل
- **مع الباك-إند:** مراجعة الـ APIs، تحديد التحسينات المطلوبة
- **مع الإدارة:** الموافقة على الميزانية والجدول

#### 4.2.5 الناتج

- [x] مستودع جاهز مع CI/CD
- [x] Backlog مبدئي في Jira/Linear (~150 تذكرة)
- [x] دفتر القرارات المعمارية (ADR) — أول 5 قرارات موثقة
- [x] قائمة بيئات (Dev، Staging، Production)
- [x] Definition of Done موثقة

### 4.3 معايير الإنجاز

✅ كل المطورين يستطيعون استنساخ المشروع وتشغيله محلياً
✅ CI ينجح على PR تجريبي
✅ خطة المشروع مُوافق عليها من الإدارة

---

## 5) المرحلة 1: التأسيس (Week 1-2)

### 5.1 الأهداف

- مشروع RN قابل للتشغيل على Android + iOS
- البنية الأساسية للمجلدات
- التبعيات الرئيسية مثبتة
- "Hello World" يقلع

### 5.2 المهام

#### 5.2.1 إنشاء المشروع

```bash
npx react-native@latest init AbbasiyCashiers \
  --template react-native-template-typescript \
  --version 0.74.5

cd AbbasiyCashiers

# إعداد yarn workspaces (سنحتاج monorepo لاحقاً)
mkdir -p packages/app packages/shared
```

#### 5.2.2 تثبيت التبعيات الأساسية

```json
// package.json (مختصر)
{
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.74.5",

    // التنقل
    "@react-navigation/native": "^6.1.0",
    "@react-navigation/native-stack": "^6.9.0",
    "@react-navigation/bottom-tabs": "^6.5.0",
    "react-native-screens": "^3.29.0",
    "react-native-safe-area-context": "^4.8.0",

    // الواجهة
    "react-native-paper": "^5.12.0",
    "react-native-vector-icons": "^10.0.3",
    "react-native-reanimated": "^3.6.0",
    "react-native-gesture-handler": "^2.14.0",

    // الحالة
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.17.0",

    // الشبكة
    "axios": "^1.6.0",
    "react-native-ssl-pinning": "^1.5.7",

    // التخزين
    "@nozbe/watermelondb": "^0.27.1",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "react-native-keychain": "^8.1.0",

    // النماذج والتحقق
    "react-hook-form": "^7.49.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0",

    // المرافق
    "date-fns": "^3.0.0",
    "react-native-restart": "^0.0.27"
  },
  "devDependencies": {
    "typescript": "5.3.0",
    "@types/react": "^18.2.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0",
    "jest": "^29.7.0",
    "@testing-library/react-native": "^12.4.0",
    "detox": "^20.13.0"
  }
}
```

#### 5.2.3 إعداد TypeScript بصرامة

```json
// tsconfig.json
{
  "extends": "@tsconfig/react-native/tsconfig.json",
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@features/*": ["src/features/*"],
      "@domain/*": ["src/domain/*"]
    }
  }
}
```

#### 5.2.4 إعداد ESLint + Prettier

```json
// .eslintrc.js
module.exports = {
  root: true,
  extends: [
    '@react-native',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  plugins: ['@typescript-eslint', 'react-hooks', 'jest'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'no-console': ['error', { allow: ['warn', 'error'] }],
  },
};
```

#### 5.2.5 هيكل المجلدات

```
AbbasiyCashiers/
├── src/
│   ├── App.tsx
│   ├── domain/              # كيانات المجال (Customer, Payment...)
│   ├── data/                # WatermelonDB models, API clients
│   ├── features/            # ميزات: auth, customers, payments
│   ├── components/          # مكونات مشتركة
│   ├── navigation/          # RootNavigator, types
│   ├── theme/               # ألوان، خطوط، motion
│   ├── hooks/               # useNetwork, useTheme
│   ├── utils/               # numbers, currency, date
│   ├── assets/              # fonts, images
│   └── types/               # global.d.ts
├── android/
├── ios/
├── __tests__/
├── e2e/                     # اختبارات Detox
└── .github/workflows/
```

#### 5.2.6 شاشة Splash مبدئية

```typescript
// src/App.tsx
import React from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppThemeProvider } from '@/theme/ThemeProvider';
import { RootNavigator } from '@/navigation/RootNavigator';

const queryClient = new QueryClient();

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <AppThemeProvider>
            <RootNavigator />
          </AppThemeProvider>
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
```

### 5.3 الناتج

- [x] مشروع RN يقلع على Android emulator + جهاز فعلي
- [x] CI ينجح ويبني APK
- [x] هيكل المجلدات النهائي مُنشأ
- [x] خطوط Cairo مثبتة وتعمل
- [x] الثيم الفاتح/الداكن يعمل
- [x] RTL مُفعّل
- [x] أول test صفري يمر (`expect(1+1).toBe(2)`)

### 5.4 معايير الإنجاز

✅ `npx react-native run-android` ينجح على Windows/Mac/Linux
✅ APK يقل عن 30MB (مع Hermes)
✅ زمن إقلاع التطبيق على جهاز متوسط < 1.5s

---

## 6) المرحلة 2: المصادقة والتنقل (Week 3-4)

### 6.1 الأهداف

- شاشة تسجيل دخول كاملة
- ربط بـ API الموجود (`/users/login`)
- تخزين Token في Keychain
- التنقل الأساسي
- معالجة انتهاء الجلسة

### 6.2 المهام

#### 6.2.1 شاشات

- `SplashScreen` — يتحقق من Token الموجود
- `LoginScreen` — اسم مستخدم + كلمة مرور (RSA encrypted)
- `HomeScreen` — Dashboard مبدئي مع أزرار التنقل
- `SettingsScreen` — تغيير الثيم، تسجيل الخروج

#### 6.2.2 ميزات تقنية

```typescript
// src/features/auth/api/authApi.ts
export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    // 1. تشفير كلمة المرور بـ RSA (نفس البروتوكول القديم للتوافق)
    const encryptedPassword = await rsaEncrypt(password);

    // 2. استدعاء API
    const response = await apiClient.post('/users/login', {
      Username: username,
      Password: encryptedPassword,
      DeviceId: await getDeviceId(),
    });

    // 3. حفظ Token في Keychain
    await Keychain.setGenericPassword(
      username,
      response.data.Token,
      { service: 'com.abbasiy.cashiers' }
    );

    return response.data;
  },

  logout: async () => {
    await Keychain.resetGenericPassword();
    await secureStore.clear();
  },
};
```

#### 6.2.3 معالجة 401

```typescript
// في apiClient interceptor (تم تفصيلها في 04_api_client_skeleton.md)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await Keychain.resetGenericPassword();
      navigationRef.reset({
        index: 0,
        routes: [{ name: 'Login' }],
      });
    }
    return Promise.reject(error);
  }
);
```

### 6.3 الاختبارات

```typescript
// __tests__/auth/login.test.ts
describe('Login Flow', () => {
  it('encrypts password with RSA before sending', async () => {
    const spy = jest.spyOn(rsaUtils, 'rsaEncrypt');
    await authApi.login('cashier1', 'password123');
    expect(spy).toHaveBeenCalledWith('password123');
  });

  it('stores token in Keychain on success', async () => {
    mockApi.onPost('/users/login').reply(200, { Token: 'abc123' });
    await authApi.login('cashier1', 'password123');
    const stored = await Keychain.getGenericPassword();
    expect(stored.password).toBe('abc123');
  });

  it('clears token on 401', async () => {
    await Keychain.setGenericPassword('user', 'old-token');
    mockApi.onGet('/customers').reply(401);
    await apiClient.get('/customers').catch(() => {});
    const stored = await Keychain.getGenericPassword();
    expect(stored).toBe(false);
  });
});
```

### 6.4 الناتج

- [x] كاشير يستطيع تسجيل الدخول
- [x] Token محفوظ بأمان في Keychain
- [x] الجلسات منتهية الصلاحية تُعالج تلقائياً
- [x] تسجيل الخروج يمسح كل البيانات الحساسة
- [x] الانتقالات بين الشاشات سلسة (60fps)

### 6.5 معايير الإنجاز

✅ Login → Home في أقل من 2 ثانية
✅ التطبيق يفتح على Home مباشرة إذا Token صالح موجود
✅ 100% من Auth flow مغطى بـ Unit Tests

---

## 7) المرحلة 3: العملاء + قاعدة بيانات (Week 5-7)

### 7.1 الأهداف

- WatermelonDB schema كاملة
- جلب العملاء من API وتخزينهم محلياً
- البحث والتصفية offline
- مزامنة دلتا (Delta Sync)

### 7.2 المهام

#### 7.2.1 إعداد WatermelonDB

```typescript
// src/data/database/schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'customers',
      columns: [
        { name: 'server_id', type: 'string', isIndexed: true },
        { name: 'account_number', type: 'string', isIndexed: true },
        { name: 'name', type: 'string' },
        { name: 'name_normalized', type: 'string', isIndexed: true }, // للبحث
        { name: 'phone', type: 'string', isOptional: true },
        { name: 'address', type: 'string' },
        { name: 'balance', type: 'number' },
        { name: 'last_reading', type: 'number' },
        { name: 'last_reading_date', type: 'number', isOptional: true },
        { name: 'meter_number', type: 'string', isIndexed: true },
        { name: 'region_id', type: 'string', isIndexed: true },
        { name: 'is_active', type: 'boolean' },
        { name: 'last_synced_at', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'payments',
      columns: [
        { name: 'server_id', type: 'string', isOptional: true, isIndexed: true },
        { name: 'idempotency_key', type: 'string', isIndexed: true },
        { name: 'customer_id', type: 'string', isIndexed: true },
        { name: 'amount', type: 'number' },
        { name: 'note', type: 'string', isOptional: true },
        { name: 'payment_date', type: 'number' },
        { name: 'sync_status', type: 'string', isIndexed: true }, // pending|syncing|synced|failed
        { name: 'failure_reason', type: 'string', isOptional: true },
        { name: 'retry_count', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    // readings, regions, sync_logs ...
  ],
});
```

#### 7.2.2 خدمة المزامنة

```typescript
// src/features/sync/services/syncService.ts
import { synchronize } from '@nozbe/watermelondb/sync';
import { database } from '@/data/database';
import { customerApi } from '@/features/customers/api';

export async function syncCustomers() {
  await synchronize({
    database,
    pullChanges: async ({ lastPulledAt }) => {
      const response = await customerApi.getDelta({
        since: lastPulledAt || 0,
      });
      return {
        changes: {
          customers: {
            created: response.created.map(toWatermelon),
            updated: response.updated.map(toWatermelon),
            deleted: response.deleted,
          },
        },
        timestamp: response.serverTimestamp,
      };
    },
    pushChanges: async ({ changes, lastPulledAt }) => {
      // العملاء قراءة فقط — لا push
    },
  });
}
```

#### 7.2.3 الشاشات

- `CustomerListScreen` — قائمة مع بحث وتصفية
- `CustomerDetailScreen` — تفاصيل العميل + تاريخ المعاملات
- شريط حالة المزامنة في الأعلى

#### 7.2.4 البحث offline

```typescript
// src/features/customers/hooks/useCustomerSearch.ts
import { Q } from '@nozbe/watermelondb';
import { database } from '@/data/database';

export function useCustomerSearch(query: string) {
  return useQuery({
    queryKey: ['customers', 'search', query],
    queryFn: async () => {
      const normalized = normalizeArabic(query.toLowerCase().trim());
      if (!normalized) return [];

      return database
        .get('customers')
        .query(
          Q.or(
            Q.where('name_normalized', Q.like(`%${normalized}%`)),
            Q.where('account_number', Q.like(`${normalized}%`)),
            Q.where('meter_number', Q.like(`${normalized}%`))
          )
        )
        .fetch();
    },
    enabled: query.length >= 2,
  });
}

function normalizeArabic(text: string): string {
  return text
    .replace(/[إأآا]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[ًٌٍَُِّْـ]/g, '');
}
```

### 7.3 الناتج

- [x] مزامنة أولية لـ 10,000+ عميل في أقل من 30 ثانية
- [x] البحث offline في أقل من 100ms حتى مع 50,000 سجل
- [x] مزامنة دلتا عند إعادة الفتح أو سحب القائمة
- [x] واجهة Master-Detail على الأجهزة اللوحية

### 7.4 معايير الإنجاز

✅ التطبيق يعمل بالكامل بدون اتصال (للبحث والعرض)
✅ البحث بالعربية مع normalization (إ/أ/ا = ا)
✅ حجم DB أقل من 50MB لـ 50,000 عميل

---

## 8) المرحلة 4: الدفع + الطابعة (Week 8-10) ⭐ **MVP**

### 8.1 الأهداف (الأكثر أهمية!)

- تنفيذ دفع كامل offline-first
- طباعة إيصال على Bluetooth POS
- مزامنة المدفوعات عند الاتصال
- إصلاح bug `Pay_amount = lastRead - amount` 🐛

### 8.2 المهام

#### 8.2.1 نموذج الدفع

استخدم المخططات من `06_ui_modernization.md` و `03_data_models_typescript.md`.

#### 8.2.2 الحفظ Offline-First

```typescript
// src/features/payments/services/paymentService.ts
import { database } from '@/data/database';
import { generateIdempotencyKey } from '@/utils/idempotency';
import { syncQueue } from '@/features/sync/queue';

export async function createPayment(input: {
  customerId: string;
  amount: number;
  note?: string;
}) {
  const idempotencyKey = generateIdempotencyKey();

  // 1. احفظ محلياً فوراً
  const payment = await database.write(async () => {
    return database.get('payments').create((p) => {
      p.serverId = null;
      p.idempotencyKey = idempotencyKey;
      p.customerId = input.customerId;
      p.amount = input.amount;
      p.note = input.note || null;
      p.paymentDate = Date.now();
      p.syncStatus = 'pending';
      p.retryCount = 0;
    });
  });

  // 2. أضف للقائمة لمزامنة لاحقاً
  await syncQueue.enqueue({
    type: 'payment',
    entityId: payment.id,
    idempotencyKey,
  });

  // 3. حاول المزامنة فوراً (إذا متصل)
  if (await isOnline()) {
    syncQueue.processPending(); // غير محظور
  }

  return payment;
}
```

#### 8.2.3 طابعة Bluetooth POS

```typescript
// src/features/printing/services/printerService.ts
// نستخدم TurboModule مخصص يلف Bixolon JPOS SDK

import { NativeModules } from 'react-native';
const { BluetoothPrinter } = NativeModules;

export async function printReceipt(receipt: Receipt): Promise<void> {
  // 1. اتصال
  const printerAddress = await getStoredPrinterAddress();
  if (!printerAddress) {
    throw new PrinterError('PRINTER_NOT_CONFIGURED');
  }
  await BluetoothPrinter.connect(printerAddress);

  // 2. طباعة (ESC/POS commands)
  await BluetoothPrinter.printText('= مؤسسة العباسي للجباية =\n', {
    align: 'center',
    bold: true,
    size: 'large',
  });

  await BluetoothPrinter.printLine();

  await BluetoothPrinter.printKeyValue('رقم الإيصال', receipt.id);
  await BluetoothPrinter.printKeyValue('التاريخ', formatDate(receipt.date));
  await BluetoothPrinter.printKeyValue('الكاشير', receipt.cashierName);

  await BluetoothPrinter.printLine();

  await BluetoothPrinter.printKeyValue('العميل', receipt.customer.name);
  await BluetoothPrinter.printKeyValue('رقم الحساب', receipt.customer.accountNumber);

  await BluetoothPrinter.printLine();

  await BluetoothPrinter.printKeyValue(
    'المبلغ المدفوع',
    formatCurrency(receipt.amount)
  );
  await BluetoothPrinter.printKeyValue(
    'كتابة',
    convertNumberToArabicWords(receipt.amount)
  );

  if (receipt.note) {
    await BluetoothPrinter.printText(`ملاحظة: ${receipt.note}\n`);
  }

  await BluetoothPrinter.printLine();
  await BluetoothPrinter.printQRCode(receipt.verificationUrl);
  await BluetoothPrinter.printText('شكراً لتعاملكم معنا', { align: 'center' });
  await BluetoothPrinter.cutPaper();

  // 3. فصل
  await BluetoothPrinter.disconnect();
}
```

#### 8.2.4 إصلاح Bug Pay_amount

```typescript
// قاعدة: المبلغ المدفوع هو ما يدخله الكاشير، فقط.

// ❌ القديم (مع البق):
// Pay_amount = lastRead - amount  // خطأ منطقي!

// ✅ الجديد:
const paymentRequest = {
  Pay_amount: input.amount,           // المبلغ كما هو
  Customer_id: input.customerId,
  Note: input.note,
  Cashier_id: currentUser.id,
  Idempotency_Key: idempotencyKey,
};
```

### 8.3 الناتج

- [x] الدفع يحفظ ويطبع حتى بدون اتصال
- [x] إعادة الاتصال تُزامن تلقائياً
- [x] إيصال جميل ومقروء
- [x] Bug `Pay_amount` مُصلح ومُغطى باختبارات

### 8.4 معايير الإنجاز ⭐ **هذه المرحلة هي MVP**

✅ كاشير واحد يستخدم التطبيق ميدانياً يوم كامل بدون مشاكل
✅ 100% من المدفوعات تتم مزامنتها خلال 5 دقائق من الاتصال
✅ زمن طباعة إيصال < 3 ثوانٍ
✅ التطبيق يتعامل مع 100+ معاملة offline قبل المزامنة

---

## 9) المرحلة 5: قراءة العداد + الصور (Week 11-12)

### 9.1 الأهداف

- شاشة قراءة عداد
- التقاط صورة عداد
- ضغط ورفع الصور
- التحقق من القراءة الجديدة ≥ السابقة

### 9.2 المهام

#### 9.2.1 شاشة القراءة

```typescript
// src/features/readings/screens/ReadingScreen.tsx
// مع التحقق:
const readingSchema = z.object({
  newReading: z.coerce.number()
    .positive('القراءة يجب أن تكون موجبة')
    .refine(
      (val) => val >= customer.lastReading,
      `القراءة الجديدة يجب أن تكون أكبر من ${customer.lastReading}`
    ),
  imageUri: z.string().min(1, 'الصورة مطلوبة'),
});
```

#### 9.2.2 التقاط وضغط الصورة

```typescript
import { launchCamera } from 'react-native-image-picker';
import ImageResizer from 'react-native-image-resizer';

async function captureReadingImage(): Promise<string> {
  const result = await launchCamera({
    mediaType: 'photo',
    cameraType: 'back',
    saveToPhotos: false,
    quality: 0.8,
  });

  if (!result.assets?.[0]?.uri) {
    throw new Error('لم يتم التقاط الصورة');
  }

  // ضغط إلى < 200KB
  const compressed = await ImageResizer.createResizedImage(
    result.assets[0].uri,
    1024,      // max width
    1024,      // max height
    'JPEG',
    70,        // quality
    0,         // rotation
    undefined,
    false,
    { onlyScaleDown: true }
  );

  return compressed.uri;
}
```

#### 9.2.3 رفع الصورة (مع retry)

```typescript
async function uploadReadingImage(
  localUri: string,
  readingId: string
): Promise<string> {
  const formData = new FormData();
  formData.append('image', {
    uri: localUri,
    type: 'image/jpeg',
    name: `reading_${readingId}.jpg`,
  } as any);
  formData.append('readingId', readingId);

  const response = await apiClient.post('/readings/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000, // الصور قد تكون بطيئة
  });

  return response.data.serverUrl;
}
```

### 9.3 الناتج

- [x] قراءة العداد مع التقاط صورة
- [x] الصور مضغوطة محلياً (< 200KB)
- [x] رفع تلقائي مع إعادة محاولة
- [x] الصور محفوظة محلياً حتى نجاح الرفع

### 9.4 معايير الإنجاز

✅ التقاط + ضغط + معاينة < 3 ثوانٍ
✅ رفع صورة على 3G < 10 ثوانٍ
✅ لا فقدان للصور أبداً (حتى لو فشل الرفع 10 مرات)

---

## 10) المرحلة 6: التقارير + إزالة WebView (Week 13-14)

### 10.1 الأهداف

- شاشات تقارير native بديلاً عن WebView
- إحصائيات يومية للكاشير
- تصدير PDF
- **إزالة WebView بالكامل** ✅

### 10.2 المهام

#### 10.2.1 لوحة التقارير

```typescript
// src/features/reports/screens/DailyReportScreen.tsx

export function DailyReportScreen() {
  const today = new Date();
  const { data: stats } = useQuery({
    queryKey: ['reports', 'daily', formatDate(today)],
    queryFn: () => reportsApi.getDailyStats(today),
  });

  return (
    <ScrollView>
      <StatCard
        title="إجمالي المدفوعات اليوم"
        value={formatCurrency(stats?.totalAmount || 0)}
        icon="cash"
        color="success"
      />
      <StatCard
        title="عدد المعاملات"
        value={stats?.transactionCount || 0}
        icon="receipt"
      />
      <StatCard
        title="عدد العملاء المخدومين"
        value={stats?.uniqueCustomers || 0}
        icon="account-group"
      />

      <Card style={{ margin: 16 }}>
        <Card.Title title="آخر المعاملات" />
        <Card.Content>
          {stats?.recentPayments.map((p) => (
            <PaymentListItem key={p.id} payment={p} />
          ))}
        </Card.Content>
      </Card>

      <Button
        label="تصدير PDF"
        icon="file-pdf-box"
        onPress={exportPdf}
        variant="outlined"
      />
    </ScrollView>
  );
}
```

#### 10.2.2 تصدير PDF

```typescript
// npm i react-native-html-to-pdf
import RNHTMLtoPDF from 'react-native-html-to-pdf';
import Share from 'react-native-share';

async function exportDailyReportPdf(stats: DailyStats) {
  const html = `
    <html dir="rtl" lang="ar">
      <head>
        <meta charset="UTF-8">
        <style>
          body { font-family: 'Cairo', sans-serif; padding: 20px; }
          h1 { color: #1976D2; text-align: center; }
          table { width: 100%; border-collapse: collapse; }
          th { background: #1976D2; color: white; padding: 8px; }
          td { border: 1px solid #ddd; padding: 8px; }
        </style>
      </head>
      <body>
        <h1>تقرير اليوم — ${formatDate(stats.date)}</h1>
        <h2>الكاشير: ${stats.cashierName}</h2>
        <p>إجمالي المبلغ: <strong>${formatCurrency(stats.totalAmount)}</strong></p>
        <p>عدد المعاملات: ${stats.transactionCount}</p>
        <table>
          <tr><th>الوقت</th><th>العميل</th><th>المبلغ</th></tr>
          ${stats.payments.map(p => `
            <tr>
              <td>${formatTime(p.date)}</td>
              <td>${p.customerName}</td>
              <td>${formatCurrency(p.amount)}</td>
            </tr>
          `).join('')}
        </table>
      </body>
    </html>
  `;

  const pdf = await RNHTMLtoPDF.convert({
    html,
    fileName: `report_${formatDate(stats.date)}`,
    directory: 'Documents',
  });

  await Share.open({
    url: `file://${pdf.filePath}`,
    type: 'application/pdf',
  });
}
```

### 10.3 الناتج

- [x] كل تقارير WebView مُستبدلة بـ Native
- [x] تصدير PDF يعمل
- [x] **WebView لم يعد مستخدماً في الكود** ✅
- [x] إزالة كل dependencies WebView

### 10.4 معايير الإنجاز

✅ زمن فتح تقرير يومي < 500ms
✅ تصدير PDF لـ 500 معاملة < 5 ثوانٍ
✅ الكود لا يحتوي على `react-native-webview`

---

## 11) المرحلة 7: الاختبار التجريبي (Week 15-17)

### 11.1 الأهداف

- بيتا داخلي مع 3 كاشيرين
- جمع feedback
- إصلاح Bugs الحرجة
- تحسين الأداء

### 11.2 المهام

#### 11.2.1 إعداد Internal Testing

```yaml
# Google Play Console:
# - Internal Testing track
# - 10 كاشيرين مدعوين
# - تحديثات يومية ممكنة
```

#### 11.2.2 المراقبة

- **Crashlytics** (Firebase) — تتبع crashes
- **Sentry** — تتبع errors و performance
- **Analytics** — أحداث UX (login_success, payment_completed)

```typescript
// src/utils/analytics.ts
import analytics from '@react-native-firebase/analytics';

export const trackEvent = async (
  name: string,
  params?: Record<string, any>
) => {
  if (__DEV__) {
    console.log('[Analytics]', name, params);
    return;
  }
  await analytics().logEvent(name, params);
};

// استخدام:
trackEvent('payment_created', {
  amount_bucket: getAmountBucket(amount),
  is_offline: !await isOnline(),
});
```

#### 11.2.3 جمع Feedback

- نموذج داخل التطبيق ("شكاوي/اقتراحات")
- مكالمات أسبوعية مع الكاشيرين البيتا
- متابعة لجلسات Shadowing

#### 11.2.4 اختبارات الإجهاد

```bash
# اختبار حمل: 1000 معاملة offline
yarn test:e2e:stress

# اختبار شبكة بطيئة
adb shell tc qdisc add dev eth0 root netem rate 50kbit delay 1000ms

# اختبار بطارية منخفضة
adb shell dumpsys battery set level 5
```

### 11.3 الناتج

- [x] 3+ كاشيرين يستخدمون التطبيق يومياً لمدة 3 أسابيع
- [x] قائمة Bugs مُحدثة وأولوياتها مرتبة
- [x] أعلى 5 شكاوى مُعالجة
- [x] Crashlytics: < 0.5% crash rate

### 11.4 معايير الإنجاز

✅ NPS من البيتا ≥ 7/10
✅ < 1 crash لكل 100 جلسة
✅ 95% من المعاملات تنجح في المحاولة الأولى

---

## 12) المرحلة 8: التحول النهائي (Week 18-20)

### 12.1 الأهداف

- إطلاق تدريجي لكل الكاشيرين
- مراقبة دقيقة لأول أسبوع
- إيقاف التطبيق القديم
- إعلان "النصر" 🎉

### 12.2 خطة التدريج

```
الأسبوع 18:
  - الإثنين: 10% من الكاشيرين (5 أشخاص)
  - الأربعاء: مراجعة → 25% (12 شخص)
  - الجمعة: إذا KPIs جيدة → 50%

الأسبوع 19:
  - الإثنين: 75%
  - الجمعة: 100%

الأسبوع 20:
  - مراقبة دقيقة
  - إعلان إيقاف التطبيق القديم (تاريخ + 30 يوم)
  - تدريب إضافي حسب الحاجة
```

### 12.3 آلية التحول

```typescript
// إعلان داخل التطبيق القديم (WebView):
// إذا كان المستخدم لم ينتقل بعد → اظهر notification

// في التطبيق القديم (تحديث صغير):
const showMigrationNotice = () => {
  WebAppInterface.showAlert(
    'تحديث مهم',
    'تم إصدار النسخة الجديدة من التطبيق. ' +
    'يرجى تحميلها من الرابط:\n' +
    'https://abbasiy.com/app-new\n\n' +
    'سيتم إيقاف هذا التطبيق بعد 30 يوماً.',
    'حسناً'
  );
};
```

### 12.4 إيقاف التطبيق القديم

1. **يوم 0:** الإطلاق الكامل للجديد
2. **يوم +14:** بريد/SMS للكاشيرين بتاريخ الإيقاف
3. **يوم +21:** التطبيق القديم يعرض banner تحذيري
4. **يوم +30:** التطبيق القديم يرفض الـ login (الباك-إند يرفض)
5. **يوم +60:** إزالة التطبيق القديم من المتجر (إن وُجد)

### 12.5 الناتج

- [x] 100% من الكاشيرين على التطبيق الجديد
- [x] التطبيق القديم متوقف
- [x] KPIs أفضل من السابق
- [x] فريق الدعم مدرّب

### 12.6 معايير الإنجاز ✅ **النجاح النهائي**

✅ NPS ≥ 8/10
✅ Crash rate < 0.3%
✅ تخفيض وقت معالجة المعاملة ≥ 30%
✅ صفر بلاغات أمان مفتوحة

---

## 13) هجرة البيانات من التطبيق القديم

### 13.1 ما الذي يحتاج للهجرة؟

من التطبيق القديم نجد البيانات في:

| المصدر | المحتوى | الأهمية |
|---|---|---|
| **SharedPreferences** (`SETTING_OPRATIONS_NEW`) | إعدادات الخادم، API URL، Token | 🔴 حرج |
| **SharedPreferences** (`user`) | بيانات المستخدم المسجل | 🔴 حرج |
| **SQLite** (مخفي إذا موجود) | لا يبدو موجوداً | — |
| **Cache** (WebView) | غير ضروري | ⚪ تجاهل |
| **External Storage** | صور قراءات قديمة | 🟡 اختياري |

### 13.2 آلية الهجرة

#### الخيار أ: هجرة تلقائية عند أول تشغيل

```typescript
// src/migration/legacyMigration.ts
import { NativeModules } from 'react-native';
const { LegacyDataReader } = NativeModules; // TurboModule نكتبه

export async function migrateLegacyData(): Promise<MigrationResult> {
  // 1. تحقق هل التطبيق القديم مثبت
  const legacyInstalled = await LegacyDataReader.isLegacyAppInstalled();
  if (!legacyInstalled) return { migrated: false, reason: 'no_legacy' };

  // 2. اطلب الإذن من المستخدم
  const userConsent = await showMigrationConsentDialog();
  if (!userConsent) return { migrated: false, reason: 'user_declined' };

  // 3. اقرأ بيانات SharedPreferences (يتطلب Content Provider في القديم)
  const legacyPrefs = await LegacyDataReader.getLegacySharedPreferences();

  // 4. ترجم البيانات
  const apiUrl = legacyPrefs.apiUrl; // كان مشفراً DESede — فك التشفير
  const username = legacyPrefs.savedUsername;

  // 5. احفظها في النظام الجديد
  await AsyncStorage.setItem('@server_config', JSON.stringify({
    apiUrl: validateAndSanitizeUrl(apiUrl),
    migrated: true,
    migratedAt: new Date().toISOString(),
  }));

  if (username) {
    await AsyncStorage.setItem('@last_username', username);
  }

  return { migrated: true };
}
```

#### الخيار ب: تصدير/استيراد يدوي (احتياطي)

في التطبيق القديم (تحديث صغير) نضيف زر:
```
[تصدير البيانات للتطبيق الجديد]
→ ينشئ ملف encrypted.dat
→ المستخدم يفتحه في التطبيق الجديد
→ التطبيق الجديد يستورده
```

### 13.3 ما لا نهاجر

- ❌ كلمات المرور (سيُعيدون تسجيل الدخول)
- ❌ Cache التطبيق القديم
- ❌ ملفات WebView (cookies, localStorage)
- ❌ المدفوعات/القراءات الـ pending (يجب رفعها في القديم قبل التحول)

### 13.4 خطة "Pending Data" قبل التحول

**قبل أسبوع من التحول، الكاشير يجب:**
1. التأكد من اتصاله بالإنترنت
2. فتح التطبيق القديم
3. التحقق من رفع كل المعاملات المعلقة
4. الحصول على تأكيد "كل العمليات مزامنة"

ثم وقت التحول، نضمن أن قاعدة البيانات في الخادم محدثة.

---

## 14) استراتيجيات التراجع (Rollback)

### 14.1 لكل مرحلة لها rollback

| المرحلة | استراتيجية التراجع |
|---|---|
| M1-M2 | كل شيء داخلي، لا تأثير على الإنتاج |
| M3 | إزالة WatermelonDB، العودة لـ API calls فقط |
| M4 (MVP) | الكاشير يعود للتطبيق القديم (لا يزال مثبتاً) |
| M5-M6 | إخفاء الميزات الجديدة بـ feature flags |
| M7 | إزالة المستخدمين البيتا، العودة للقديم |
| M8 | **حرج:** خطة rollback تفصيلية |

### 14.2 خطة Rollback لمرحلة M8

```yaml
trigger: # متى نُفعل rollback
  - crashRate > 2%
  - apiSuccessRate < 90%
  - أكثر من 5 شكاوى حرجة في يوم واحد
  - فقدان بيانات مالية

steps:
  1. إيقاف الإطلاق التدريجي (Google Play Console)
  2. إعادة الكاشيرين المتأثرين للتطبيق القديم:
     - SMS بالخطوات
     - رابط التطبيق القديم (محتفظ به)
  3. تحقق من سلامة بيانات الخادم
  4. تحليل السبب الجذري (RCA)
  5. إصلاح + اختبار + إعادة محاولة

rollback_window: 72 ساعة (بعدها التراجع صعب)
```

### 14.3 Feature Flags

```typescript
// src/features/featureFlags.ts
export const featureFlags = {
  newPaymentFlow: true,
  bluetoothPrinter: true,
  cameraReading: true,
  dailyReports: true,
  pdfExport: false, // مثلاً، نطلق لاحقاً
  darkMode: true,
  arabicNumbers: false,
} as const;

// استخدام:
if (featureFlags.newPaymentFlow) {
  return <NewPaymentScreen />;
} else {
  return <FallbackScreen />;
}
```

يمكن لاحقاً ربطها بـ Firebase Remote Config لتحكم عن بعد.

---

## 15) مخاطر وتخفيفات

### 15.1 المخاطر الرئيسية

| # | المخاطرة | الاحتمالية | التأثير | التخفيف |
|---|---|---|---|---|
| R1 | عدم توافق الـ API بين القديم والجديد | متوسطة | عالٍ | اختبار شامل، Mock servers |
| R2 | الطابعة Bluetooth لا تعمل مع SDK جديد | متوسطة | عالٍ جداً | Spike مبكر في M0، احتفاظ بـ SDK القديم احتياطياً |
| R3 | بطء WatermelonDB مع بيانات كبيرة | منخفضة | متوسط | Benchmark في M3، استخدام Lazy loading |
| R4 | رفض الكاشيرين للتطبيق الجديد | متوسطة | عالٍ | إشراكهم منذ البيتا، تدريب جيد |
| R5 | فقدان بيانات أثناء الهجرة | منخفضة | عالٍ جداً | Parallel run، نسخ احتياطية، صفر-data-loss design |
| R6 | تجاوز الميزانية الزمنية | عالية | متوسط | Buffer 20%، نطاق MVP واضح |
| R7 | استقالة مطور رئيسي | منخفضة | عالٍ | توثيق جيد، Pair programming، Knowledge sharing |
| R8 | تغير متطلبات الباك-إند | متوسطة | متوسط | تعاقد محكم، contract testing |
| R9 | مشاكل أمنية مكتشفة بعد الإطلاق | متوسطة | عالٍ جداً | Pen test قبل الإطلاق، Bug bounty داخلي |
| R10 | عدم دعم Android القديم | متوسطة | متوسط | تحديد min SDK = 24 (Android 7) — يغطي 95%+ |

### 15.2 خطة الطوارئ

**إذا تأخر المشروع 4+ أسابيع:**
1. تقليص النطاق: تأجيل M6 (التقارير) للنسخة 1.1
2. تأجيل ميزات NICE-TO-HAVE
3. تمديد فترة Parallel Run

**إذا تجاوز الميزانية 30%:**
1. تقييم المتبقي بدقة
2. عرض الخيارات على الإدارة (تمديد / تقليص)
3. تجنب "Sunk Cost Fallacy"

---

## 16) خلاصة الهجرة

### 16.1 الجدول الزمني

```
الأسبوع     -1  1   3   5   8   11  13  15  18  20
الحدث       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
الإعداد     ◆
التأسيس     ━━◆
المصادقة         ━━◆
العملاء              ━━━◆
الدفع MVP                ━━━◆ ⭐
القراءة                       ━━◆
التقارير                          ━━◆
البيتا                                ━━━◆
التحول                                     ━━━◆ 🎉
```

### 16.2 الفريق المثالي

| الدور | عدد | المسؤولية |
|---|---|---|
| Tech Lead / Architect | 1 | قرارات معمارية، Code review |
| React Native Senior | 2 | تطوير الميزات الأساسية |
| React Native Mid | 1 | UI components، اختبارات |
| Backend Dev | 0.5 (نصف وقت) | تعديلات API |
| QA Engineer | 1 | اختبارات يدوية + E2E |
| UX/UI Designer | 0.5 (نصف وقت) | تصميم الشاشات |
| Product Manager | 1 | تنسيق، Backlog |
| **المجموع** | **7 أشخاص** | |

### 16.3 الميزانية التقديرية

```
الموارد البشرية (5 أشهر × 7 أشخاص × متوسط راتب):
  - تقريبي: $80,000 - $150,000

الأدوات والخدمات:
  - Apple Developer + Google Play: $200/سنة
  - Firebase + Crashlytics: $0-$200/شهر
  - Sentry: $0-$100/شهر
  - SonarCloud: $0-$50/شهر
  - GitHub Pro: $0-$50/شهر
  - تقريبي: $1,500 - $3,000

الأجهزة للاختبار:
  - 3 أجهزة Android متنوعة: $1,500
  - 2 طابعات Bluetooth: $500
  - تقريبي: $2,000

التدريب والإطلاق:
  - دورات للكاشيرين: $1,000
  - مواد تسويقية: $500
  - تقريبي: $1,500

الإجمالي التقديري: $85,000 - $156,500
```

### 16.4 العائد على الاستثمار (ROI)

```
التوفير المتوقع سنوياً:
  - تقليل الأخطاء (Pay_amount bug): ~$10,000
  - تقليل وقت معالجة المعاملة 30%: ~$20,000
  - تقليل crashes وإعادة العمل: ~$5,000
  - تجنب تكلفة الاختراق الأمني المحتمل: ~$50,000+ (متغير)

نقطة التعادل: ~12-18 شهر
العمر الافتراضي للنظام الجديد: 5+ سنوات
```

---

## 🔗 الترابط مع باقي القسم

- **01_tech_stack_options.md:** التقنيات المختارة
- **02_recommended_architecture.md:** البنية المعمارية
- **03_data_models_typescript.md:** نماذج البيانات
- **04_api_client_skeleton.md:** ربط الـ API
- **05_security_improvements.md:** متى تُحل كل ثغرة من V1-V20
- **06_ui_modernization.md:** التصميم المعتمد
- **08_acceptance_criteria.md (التالي):** كيف نعرف أن المشروع نجح

---

## 📚 مراجع

1. **Strangler Fig Pattern:** https://martinfowler.com/bliki/StranglerFigApplication.html
2. **Parallel Run Strategy:** https://martinfowler.com/bliki/ParallelChange.html
3. **WatermelonDB Sync:** https://watermelondb.dev/docs/Sync/Intro
4. **Google Play Internal Testing:** https://support.google.com/googleplay/android-developer/answer/9845334
5. **Firebase Crashlytics:** https://firebase.google.com/docs/crashlytics
6. **Architecture Decision Records (ADR):** https://adr.github.io/

---

**الملف التالي والأخير في هذا القسم:** [`08_acceptance_criteria.md`](./08_acceptance_criteria.md) — معايير القبول النهائية
