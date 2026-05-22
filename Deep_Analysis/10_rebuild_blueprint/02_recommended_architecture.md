# مخطط إعادة البناء — البنية المعمارية الموصى بها

> **الملف:** `10_rebuild_blueprint/02_recommended_architecture.md`
> **الغرض:** تحديد البنية المعمارية الكاملة (Architecture) لتطبيق AbbasiyCashiers الجديد بـ React Native.
> **المرجع:** بناءً على القرار في `01_tech_stack_options.md` (React Native + TS + WatermelonDB)

---

## 📋 جدول المحتويات

1. [نظرة عامة على البنية](#1-نظرة-عامة-على-البنية)
2. [طبقات النظام](#2-طبقات-النظام)
3. [هيكل المجلدات (Folder Structure)](#3-هيكل-المجلدات-folder-structure)
4. [تدفق البيانات](#4-تدفق-البيانات)
5. [إدارة الحالة (State Management)](#5-إدارة-الحالة-state-management)
6. [طبقة التخزين (Storage Layer)](#6-طبقة-التخزين-storage-layer)
7. [طبقة الشبكة (Network Layer)](#7-طبقة-الشبكة-network-layer)
8. [طبقة الأمان (Security Layer)](#8-طبقة-الأمان-security-layer)
9. [التنقل (Navigation)](#9-التنقل-navigation)
10. [أنماط التصميم المستخدمة](#10-أنماط-التصميم-المستخدمة)

---

## 1. نظرة عامة على البنية

### 1.1 المخطط المعماري الشامل

```
┌─────────────────────────────────────────────────────────────────────┐
│                    📱 AbbasiyCashiers Mobile App                     │
│                  React Native 0.74+ / TypeScript                     │
└─────────────────────────────────────────────────────────────────────┘
        │
        │
┌───────▼─────────────────────────────────────────────────────────────┐
│                  Layer 1: Presentation Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Screens  │  │   UI     │  │  Themes  │  │   i18n   │            │
│  │  (RN)    │  │ Library  │  │ (Light/  │  │ (ar/en)  │            │
│  │          │  │ (Paper)  │  │  Dark)   │  │   RTL    │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└───────┬─────────────────────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────────┐
│                  Layer 2: Business Logic Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Hooks   │  │ Services │  │Validators│  │ Formatters│            │
│  │ (React)  │  │          │  │  (Zod)   │  │ (currency)│            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└───────┬─────────────────────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────────┐
│                  Layer 3: State Management Layer                     │
│  ┌──────────────────┐         ┌──────────────────────┐              │
│  │  Zustand Store   │◀────────│  React Query Cache   │              │
│  │  (UI state)      │         │  (Server state)      │              │
│  └──────────────────┘         └──────────────────────┘              │
└───────┬─────────────────────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────────┐
│                  Layer 4: Data Access Layer                          │
│  ┌─────────────────────┐    ┌─────────────────────────┐             │
│  │   Repository (TS)   │    │   Sync Engine            │             │
│  │  - PaymentsRepo     │◀──▶│  (WatermelonDB → API)   │             │
│  │  - CustomersRepo    │    │  - pull, push           │             │
│  │  - SettingsRepo     │    │  - conflict resolution  │             │
│  └─────────┬───────────┘    └─────────────┬───────────┘             │
└────────────┼────────────────────────────────┼───────────────────────┘
             │                                │
       ┌─────▼──────┐                  ┌──────▼──────┐
       │ WatermelonDB│                 │ Axios Client │
       │  (SQLite)   │                 │              │
       │             │                 │ + Interceptors│
       │ Tables:     │                 │ + SSL Pinning│
       │ - customers │                 │ + JWT auth   │
       │ - payments  │                 │ + Retry      │
       │ - readings  │                 │              │
       │ - settings  │                 │              │
       └─────────────┘                 └──────┬───────┘
                                              │
                                       ┌──────▼──────────┐
                                       │ ASP.NET Web API │
                                       │ (Backend)       │
                                       └─────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│           Native Layer (TurboModules / Native Modules)              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ BluetoothPrinter │  │   Camera/QR      │  │   GPS / Location │  │
│  │  (Bixolon JPOS)  │  │   Scanner        │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 المبادئ المعمارية

| المبدأ | التطبيق العملي |
|--------|----------------|
| **Separation of Concerns** | كل طبقة لها مسؤولية واحدة محددة |
| **Single Source of Truth** | WatermelonDB هو المصدر الوحيد للبيانات المحلية |
| **Offline-First** | كل عملية تعمل بدون إنترنت ثم تُزامَن لاحقاً |
| **Type Safety** | TypeScript صارم (strict mode) + Zod schemas |
| **Testability** | كل طبقة قابلة للاختبار باستقلالية |
| **Dependency Injection** | Services تُحقن في hooks، ليست singletons |
| **Immutability** | استخدام `readonly` و spread operators |
| **Composition over Inheritance** | Hooks مركّبة، لا فئات OOP |

---

## 2. طبقات النظام

### 2.1 Layer 1: Presentation Layer (طبقة العرض)

**المسؤولية:** عرض البيانات وجمع المدخلات من المستخدم.

**المكونات:**
- **Screens:** كل شاشة في ملف منفصل (LoginScreen, MainScreen, OperationsScreen, ...)
- **Components:** مكونات قابلة لإعادة الاستخدام (Button, Card, Input, ...)
- **Themes:** ألوان، خطوط، أحجام (نظام موحد)
- **i18n:** نصوص متعددة اللغات (ar/en)

**القواعد:**
- ❌ لا منطق أعمال هنا
- ❌ لا استدعاءات API مباشرة
- ❌ لا وصول مباشر لـ Database
- ✅ فقط: عرض، استماع للأحداث، استدعاء hooks

```tsx
// مثال صحيح
function PaymentScreen() {
  const { customer, isLoading } = useCustomerLookup();
  const { savePayment, isSaving } = useSavePayment();
  
  return (
    <View>
      <Text>{customer?.name}</Text>
      <Button onPress={() => savePayment(amount)} disabled={isSaving} />
    </View>
  );
}
```

### 2.2 Layer 2: Business Logic Layer (طبقة منطق الأعمال)

**المسؤولية:** قواعد العمل، التحقق، التحويلات.

**المكونات:**
- **Custom Hooks:** `useCustomerLookup`, `useSavePayment`, `useDailyReport`
- **Services:** classes أو functions تنفذ منطق محدد
- **Validators:** Zod schemas للتحقق
- **Formatters:** تنسيق الأرقام، التواريخ، العملة

```ts
// مثال: validator
export const PaymentSchema = z.object({
  customerCode: z.string().regex(/^\d{1,12}$/),
  amount: z.number().int().positive().max(10_000_000),  // YER
  notes: z.string().max(500).optional(),
});

// مثال: formatter
export function formatYER(amount: number): string {
  return new Intl.NumberFormat('ar-YE', {
    style: 'currency',
    currency: 'YER',
  }).format(amount);
}

// مثال: service
export class PaymentService {
  constructor(
    private repo: PaymentRepository,
    private api: PaymentAPI,
  ) {}
  
  async savePayment(input: PaymentInput): Promise<Payment> {
    PaymentSchema.parse(input);  // validation
    const payment = await this.repo.create({
      ...input,
      idempotencyKey: uuid(),
      synced: false,
    });
    // محاولة السنكنة فوراً، وإذا فشلت ستُجدول لاحقاً
    this.api.savePayment(payment).catch(() => {
      // سيُعاد المحاولة بواسطة Sync Engine
    });
    return payment;
  }
}
```

### 2.3 Layer 3: State Management Layer

**المسؤولية:** إدارة حالة التطبيق الحالية في الذاكرة.

**نمطان:**
1. **UI State** (Zustand): زر مفتوح/مغلق، الوضع المظلم، اللغة الحالية
2. **Server State** (React Query): بيانات المستخدم، قوائم العمليات، إلخ.

```ts
// مثال: Zustand store
interface UIState {
  theme: 'light' | 'dark';
  language: 'ar' | 'en';
  isOffline: boolean;
  toggleTheme: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  theme: 'light',
  language: 'ar',
  isOffline: false,
  toggleTheme: () => set((s) => ({ theme: s.theme === 'light' ? 'dark' : 'light' })),
}));

// مثال: React Query hook
export function useUserProfile() {
  return useQuery({
    queryKey: ['user', 'profile'],
    queryFn: () => UserService.getProfile(),
    staleTime: 5 * 60_000,  // 5 min
  });
}
```

### 2.4 Layer 4: Data Access Layer (طبقة الوصول للبيانات)

**المسؤولية:** القراءة والكتابة من/إلى الـ DB والـ API.

**نمط Repository:**
- كل entity (Customer, Payment, Reading) له Repository خاص
- Repository هو الوحيد الذي يتحدث مع WatermelonDB
- Sync Engine يتزامن مع الـ API في الخلفية

```ts
// PaymentRepository
export class PaymentRepository {
  constructor(private db: Database) {}
  
  async create(input: PaymentInput): Promise<Payment> {
    return this.db.write(async () => {
      return this.db.collections.get<Payment>('payments').create((p) => {
        p.customerCode = input.customerCode;
        p.amount = input.amount;
        p.notes = input.notes ?? '';
        p.synced = false;
      });
    });
  }
  
  async findUnsynced(): Promise<Payment[]> {
    return this.db.collections
      .get<Payment>('payments')
      .query(Q.where('synced', false))
      .fetch();
  }
}
```

### 2.5 Native Layer (الطبقة الأصلية)

**المسؤولية:** الوصول لميزات Android/iOS الأصلية.

**TurboModules مطلوبة:**
1. **BluetoothPrinterModule** — للتعامل مع Bixolon JPOS SDK
2. **DeepLinkHandler** — للتعامل مع `ecas.web.link` (مع التحسينات الأمنية)
3. **SecureStorageModule** — للتخزين المشفر للـ tokens (يمكن استخدام `react-native-keychain` بدلاً)

---

## 3. هيكل المجلدات (Folder Structure)

```
AbbasiyCashiersV2/
├── android/                    ← Native Android code
│   ├── app/
│   └── ...
├── ios/                        ← Native iOS code (لاحقاً)
│
├── src/
│   ├── app/                    ← App entry, providers, navigation
│   │   ├── App.tsx
│   │   ├── providers/
│   │   │   ├── QueryProvider.tsx
│   │   │   ├── ThemeProvider.tsx
│   │   │   ├── DatabaseProvider.tsx
│   │   │   └── I18nProvider.tsx
│   │   └── navigation/
│   │       ├── RootNavigator.tsx
│   │       ├── AuthStack.tsx
│   │       └── MainStack.tsx
│   │
│   ├── screens/                ← شاشات التطبيق
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   └── ChangePasswordScreen.tsx
│   │   ├── main/
│   │   │   └── MainScreen.tsx
│   │   ├── operations/
│   │   │   ├── OperationsScreen.tsx
│   │   │   ├── PaymentScreen.tsx
│   │   │   ├── ReadingScreen.tsx
│   │   │   └── LocationScreen.tsx
│   │   ├── reports/
│   │   │   ├── PaymentsReportScreen.tsx
│   │   │   └── ReadingsReportScreen.tsx
│   │   └── settings/
│   │       └── PrinterSettingsScreen.tsx
│   │
│   ├── components/             ← مكونات UI قابلة لإعادة الاستخدام
│   │   ├── ui/                 ← مكونات أساسية
│   │   │   ├── Button.tsx
│   │   │   ├── TextInput.tsx
│   │   │   ├── Card.tsx
│   │   │   └── ...
│   │   ├── forms/              ← مكونات نماذج
│   │   │   ├── CustomerSearch.tsx
│   │   │   ├── AmountInput.tsx
│   │   │   └── ...
│   │   └── feedback/           ← Toasts, Modals, Dialogs
│   │       ├── ConfirmDialog.tsx
│   │       └── Toast.tsx
│   │
│   ├── features/               ← Feature-based modules
│   │   ├── auth/
│   │   │   ├── api.ts          ← API calls
│   │   │   ├── service.ts      ← Business logic
│   │   │   ├── hooks.ts        ← React hooks
│   │   │   ├── store.ts        ← Zustand slice
│   │   │   ├── types.ts        ← TypeScript types
│   │   │   ├── schemas.ts      ← Zod schemas
│   │   │   └── index.ts        ← Public API of module
│   │   ├── payment/
│   │   ├── reading/
│   │   ├── customer/
│   │   ├── printer/
│   │   └── reports/
│   │
│   ├── database/               ← WatermelonDB
│   │   ├── index.ts            ← Database instance
│   │   ├── schema.ts           ← DB schema
│   │   ├── migrations.ts       ← Migration files
│   │   ├── models/             ← WatermelonDB models
│   │   │   ├── Customer.ts
│   │   │   ├── Payment.ts
│   │   │   ├── Reading.ts
│   │   │   └── Settings.ts
│   │   └── sync/
│   │       ├── syncEngine.ts
│   │       ├── pull.ts
│   │       └── push.ts
│   │
│   ├── api/                    ← API Client
│   │   ├── client.ts           ← Axios instance
│   │   ├── interceptors.ts     ← Auth, errors, logging
│   │   ├── endpoints.ts        ← URL constants
│   │   └── types.ts            ← Request/Response types
│   │
│   ├── theme/                  ← Theme system
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   ├── spacing.ts
│   │   └── index.ts
│   │
│   ├── i18n/                   ← Internationalization
│   │   ├── index.ts
│   │   ├── locales/
│   │   │   ├── ar.json
│   │   │   └── en.json
│   │   └── hooks.ts
│   │
│   ├── utils/                  ← Utility functions
│   │   ├── currency.ts         ← formatYER, parseAmount
│   │   ├── arabic.ts           ← Arabic number to words
│   │   ├── date.ts             ← Date formatting
│   │   ├── validation.ts       ← Common validators
│   │   └── id.ts               ← UUID generation
│   │
│   ├── native/                 ← TurboModules wrappers
│   │   ├── BluetoothPrinter.ts
│   │   ├── DeepLink.ts
│   │   └── SecureStorage.ts
│   │
│   ├── config/                 ← App configuration
│   │   ├── env.ts              ← Environment vars
│   │   ├── constants.ts        ← App constants
│   │   └── allowedHosts.ts     ← Whitelist للخوادم
│   │
│   └── types/                  ← Global types
│       ├── api.ts
│       ├── domain.ts
│       └── env.d.ts
│
├── assets/                     ← الموارد
│   ├── images/
│   ├── fonts/
│   │   ├── Cairo-Regular.ttf
│   │   ├── Cairo-Bold.ttf
│   │   └── ...
│   └── icons/
│
├── __tests__/                  ← Unit tests
│   ├── features/
│   ├── utils/
│   └── ...
│
├── e2e/                        ← Detox E2E tests
│
├── .env.example
├── .eslintrc.js
├── .prettierrc.js
├── babel.config.js
├── metro.config.js
├── tsconfig.json
├── package.json
└── README.md
```

### 3.1 لماذا Feature-based؟

بدلاً من تنظيم الكود حسب النوع (`components/`, `hooks/`, `services/`)، نُنظِّمه حسب الميزة:

❌ **Type-based (نتجنبه):**
```
src/
├── components/PaymentForm.tsx
├── components/PaymentList.tsx
├── hooks/usePayment.ts
├── services/paymentService.ts
└── types/payment.ts
```

✅ **Feature-based (نختاره):**
```
src/features/payment/
├── components/
├── hooks.ts
├── service.ts
├── types.ts
└── index.ts
```

**الفائدة:** عند العمل على ميزة، كل ما يخصها في مكان واحد. سهل الفهم، سهل الحذف، سهل النقل.

---

## 4. تدفق البيانات

### 4.1 تدفق عملية دفع (Payment Save) — Offline-First

```
1. المستخدم يضغط "حفظ"
   │
   ▼
2. PaymentScreen يستدعي useSavePayment hook
   │
   ▼
3. Hook يستدعي PaymentService.savePayment()
   │
   ▼
4. Service ينفذ:
   ├─▶ Validation (Zod)
   ├─▶ Repository.create() → WatermelonDB
   │                          └─▶ يحفظ مع synced=false
   ├─▶ Cache invalidation (React Query)
   └─▶ Sync attempt (async, non-blocking)
        │
        ▼
5. UI تُحدَّث فوراً (من WatermelonDB)
   ├─▶ Toast: "تم الحفظ"
   └─▶ Navigation: العودة للقائمة
   │
   ▼
6. Sync Engine (في الخلفية):
   ├─▶ يأخذ كل payments حيث synced=false
   ├─▶ POST /api/Payment/saveBillRequest
   ├─▶ إذا نجح: update synced=true
   └─▶ إذا فشل: retry exponential backoff
```

### 4.2 تدفق البحث عن مشترك (Customer Search)

```
1. المستخدم يدخل رقم المشترك
   │
   ▼
2. useCustomerLookup hook يُفعَّل (مع debounce 500ms)
   │
   ▼
3. أولاً: البحث في WatermelonDB المحلي
   │
   ├─▶ موجود؟ → اعرض فوراً
   │
   └─▶ غير موجود؟ ↓
       │
       ▼
4. ثانياً: استدعاء API /api/Payment/GetCustomersData
   │
   ├─▶ موجود؟ → احفظ في DB + اعرض
   │
   └─▶ خطأ؟ → اعرض رسالة + خيار "تحديث"
```

---

## 5. إدارة الحالة (State Management)

### 5.1 تقسيم الحالة

| نوع الحالة | الأداة | أمثلة |
|------------|-------|--------|
| **UI Local** | `useState` | فتح/إغلاق Modal، Input values |
| **UI Global** | Zustand | Theme, Language, Offline status |
| **Server (cached)** | React Query | Customer data, Reports, User profile |
| **Database** | WatermelonDB observers | قائمة المدفوعات، العملاء |
| **Form** | React Hook Form | جميع النماذج (login, payment, ...) |

### 5.2 لماذا Zustand بدل Redux؟

```ts
// Redux (الطريقة القديمة) — boilerplate كثير
const initialState = { user: null };
const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action) => { state.user = action.payload; },
  },
});
export const { setUser } = userSlice.actions;
export default userSlice.reducer;

// Zustand (الطريقة الحديثة) — سطر واحد
const useUserStore = create((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));
```

**الفروق:**
| | Redux | Zustand |
|--|-------|---------|
| Boilerplate | كثير | قليل جداً |
| TypeScript | جيد لكن يحتاج إعداد | ممتاز out-of-the-box |
| Bundle size | ~13 KB | ~1 KB |
| Async | يحتاج Thunk/Saga | مدمج |

---

## 6. طبقة التخزين (Storage Layer)

### 6.1 ثلاث أنواع تخزين

| النوع | الأداة | الاستخدام |
|------|-------|-----------|
| **SQL Database** | WatermelonDB | Customers, Payments, Readings |
| **Key-Value (Simple)** | MMKV | Theme, Language, Last sync time |
| **Secure Storage** | Keychain | JWT Token, RSA keys |

### 6.2 WatermelonDB Schema (مختصر — التفاصيل في `03_data_models_typescript.md`)

```ts
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'customers',
      columns: [
        { name: 'code', type: 'string', isIndexed: true },
        { name: 'name', type: 'string' },
        { name: 'balance', type: 'number' },
        { name: 'address', type: 'string', isOptional: true },
        { name: 'phone', type: 'string', isOptional: true },
        { name: 'last_reading', type: 'number', isOptional: true },
        { name: 'last_synced_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'payments',
      columns: [
        { name: 'customer_code', type: 'string', isIndexed: true },
        { name: 'amount', type: 'number' },
        { name: 'notes', type: 'string', isOptional: true },
        { name: 'location_xy', type: 'string', isOptional: true },
        { name: 'idempotency_key', type: 'string' },
        { name: 'synced', type: 'boolean', isIndexed: true },
        { name: 'created_at', type: 'number' },
        { name: 'synced_at', type: 'number', isOptional: true },
      ],
    }),
    tableSchema({
      name: 'readings',
      columns: [
        { name: 'customer_code', type: 'string', isIndexed: true },
        { name: 'reading_value', type: 'number' },
        { name: 'meter_image_path', type: 'string', isOptional: true },
        { name: 'notes', type: 'string', isOptional: true },
        { name: 'idempotency_key', type: 'string' },
        { name: 'synced', type: 'boolean', isIndexed: true },
        { name: 'created_at', type: 'number' },
        { name: 'synced_at', type: 'number', isOptional: true },
      ],
    }),
    tableSchema({
      name: 'settings',
      columns: [
        { name: 'key', type: 'string', isIndexed: true },
        { name: 'value', type: 'string' },
      ],
    }),
  ],
});
```

### 6.3 Sync Strategy

```
┌─────────────────────────────────────────────┐
│              Sync Engine                     │
│                                             │
│  ┌─────────────┐         ┌──────────────┐  │
│  │   PULL      │         │     PUSH     │  │
│  │             │         │              │  │
│  │ من Server   │         │  من Device   │  │
│  │ ► Customers │         │ ► Payments   │  │
│  │ ► Updates   │         │ ► Readings   │  │
│  └─────────────┘         └──────────────┘  │
│                                             │
│  Trigger:                                   │
│  - App start                                │
│  - Network reconnect                        │
│  - Manual refresh                           │
│  - Every 5 min when active                  │
└─────────────────────────────────────────────┘
```

---

## 7. طبقة الشبكة (Network Layer)

التفاصيل الكاملة في `04_api_client_skeleton.md`. الملخص:

```ts
// src/api/client.ts
const apiClient = axios.create({
  baseURL: Config.API_BASE_URL,
  timeout: 10_000,
});

// Interceptors
apiClient.interceptors.request.use(addAuthToken);
apiClient.interceptors.request.use(addDeviceId);
apiClient.interceptors.response.use(
  successHandler,
  errorHandler,  // Auto-retry on 401, refresh token
);

// SSL Pinning (بدلاً من X509TrustManager الفارغ)
applySSLPinning(apiClient);
```

---

## 8. طبقة الأمان (Security Layer)

التفاصيل الكاملة في `05_security_improvements.md`. الملخص:

| الإجراء | الأداة | الغرض |
|---------|--------|--------|
| Token storage | Keychain (iOS) / Keystore (Android) | بدلاً من SharedPreferences |
| SSL Pinning | `react-native-ssl-pinning` | بدلاً من Empty X509TrustManager |
| Encrypted DB | WatermelonDB + SQLCipher | تشفير البيانات على القرص |
| Code Obfuscation | Hermes + ProGuard | منع reverse engineering |
| Root Detection | `jail-monkey` | منع التشغيل على أجهزة Rooted |
| Deeplink Whitelist | Custom validation | بدلاً من قبول أي خادم |

---

## 9. التنقل (Navigation)

```ts
// React Navigation 6
RootNavigator
├── AuthStack (إذا لم يكن مسجل)
│   ├── LoginScreen
│   ├── ChangePasswordScreen
│   └── DeeplinkHandlerScreen
│
└── MainStack (إذا كان مسجل)
    ├── MainScreen
    ├── OperationsStack
    │   ├── PaymentScreen
    │   ├── ReadingScreen
    │   └── LocationScreen
    ├── ReportsStack
    │   ├── PaymentsReportScreen
    │   └── ReadingsReportScreen
    └── SettingsStack
        └── PrinterSettingsScreen
```

### 9.1 Type-safe Navigation

```ts
// src/app/navigation/types.ts
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  ChangePassword: { userId: string };
};

export type MainStackParamList = {
  Home: undefined;
  Operations: { mode: 'payment' | 'reading' | 'location' };
  Reports: undefined;
  Settings: undefined;
};

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
```

---

## 10. أنماط التصميم المستخدمة

| النمط | الاستخدام | المثال |
|-------|-----------|---------|
| **Repository Pattern** | عزل DB layer | `PaymentRepository` |
| **Service Layer** | Business logic | `PaymentService` |
| **Dependency Injection** | Testability | React Context للـ services |
| **Observer Pattern** | Reactive data | WatermelonDB observers |
| **Factory Pattern** | إنشاء complex objects | `PaymentFactory.fromInput()` |
| **Strategy Pattern** | Multiple payment methods | `PrintStrategy` (text/image) |
| **Command Pattern** | Undo/redo | `PaymentCommand.execute()` |
| **Singleton (limited)** | Logger, Database instance | `db` instance |

---

## 11. مقارنة سريعة: الحالي vs الجديد

| الجانب | الحالي (WebView) | الجديد (RN) |
|--------|------------------|--------------|
| **UI** | HTML/JS داخل WebView | React Native components |
| **State** | Globals + SharedPreferences | Zustand + React Query |
| **DB** | SharedPreferences فقط | WatermelonDB (SQLite) |
| **Network** | Volley + JSON-Java | Axios + TypeScript |
| **Auth** | Token in SharedPreferences | Token in Keychain |
| **TLS** | Empty X509TrustManager 🔴 | SSL Pinning ✅ |
| **Offline** | لا يعمل ❌ | Offline-first ✅ |
| **i18n** | Hardcoded Arabic | i18next ar/en |
| **Type safety** | None (Java + JS) | TypeScript strict |
| **Testing** | None | Jest + Detox |

---

## 12. الخطوة التالية

اقرأ الملف التالي:
👉 **`03_data_models_typescript.md`** — نماذج البيانات بـ TypeScript جاهزة للاستخدام

---

## مراجع
- `01_tech_stack_options.md` — اختيار Stack
- `01_overview/02_architecture_diagram.md` — البنية الحالية للمقارنة
- WatermelonDB docs: https://nozbe.github.io/WatermelonDB/
- React Navigation: https://reactnavigation.org/

---

> *نهاية `10_rebuild_blueprint/02_recommended_architecture.md`*
