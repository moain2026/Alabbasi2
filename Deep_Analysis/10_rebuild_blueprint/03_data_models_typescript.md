# مخطط إعادة البناء — نماذج البيانات بـ TypeScript

> **الملف:** `10_rebuild_blueprint/03_data_models_typescript.md`
> **الغرض:** كود TypeScript جاهز للنسخ-اللصق يحتوي كل نماذج البيانات المطلوبة.
> **المرجع الأصلي:** القسم `03_data_models/` يحتوي تحليل النماذج الأصلية.

---

## 📋 جدول المحتويات

1. [نظرة عامة](#1-نظرة-عامة)
2. [Domain Types (TypeScript Pure)](#2-domain-types-typescript-pure)
3. [Zod Schemas (Validation)](#3-zod-schemas-validation)
4. [WatermelonDB Models](#4-watermelondb-models)
5. [API DTOs (Request/Response)](#5-api-dtos-requestresponse)
6. [Mappers (DTO ↔ Domain ↔ DB)](#6-mappers-dto--domain--db)
7. [Type Tests](#7-type-tests)

---

## 1. نظرة عامة

نستخدم **3 طبقات من النماذج**، كل واحدة لغرض محدد:

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   API DTOs       │    │  Domain Types    │    │  DB Models       │
│  (الشبكة)        │◀──▶│  (منطق الأعمال)  │◀──▶│  (WatermelonDB)  │
│                  │    │                  │    │                  │
│  PayloadInput    │    │  Payment         │    │  PaymentModel    │
│  PayloadResponse │    │  Customer        │    │  CustomerModel   │
│  (snake_case)    │    │  Reading         │    │  ReadingModel    │
│                  │    │  (camelCase)     │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   مطابقة JSON              منطق التطبيق           SQLite columns
   من ASP.NET API           Type-safe              Reactive
```

**لماذا 3 طبقات؟**
- Domain Types مستقلة عن التفاصيل التقنية (يمكن تبديل DB أو API بدون كسرها)
- DTOs تتبع تنسيق الـ Backend بالضبط (`snake_case`، حقول إجبارية)
- DB Models تستفيد من ميزات WatermelonDB (observers, queries)

---

## 2. Domain Types (TypeScript Pure)

### 2.1 User (المستخدم)

من تحليل `03_data_models/01_user_model.md` — 21 حقلاً في النموذج الأصلي.

```ts
// src/types/domain/user.ts

/**
 * نموذج المستخدم في طبقة منطق الأعمال
 * المرجع: User.java في التطبيق الأصلي (21 @SerializedName)
 */
export interface User {
  // === الهوية ===
  /** معرف المستخدم (UserCode في الأصل) */
  readonly id: string;
  
  /** اسم المستخدم */
  readonly username: string;
  
  /** الاسم الكامل (FullName) */
  readonly fullName: string;
  
  // === المصادقة ===
  /** رمز المصادقة (Token) — JWT بدلاً من النص العادي */
  readonly token: string;
  
  /** تاريخ انتهاء الـ Token */
  readonly tokenExpiresAt: Date;
  
  /** RSA Public Key المُستلَم من /getAppPK (PK_Key) */
  readonly publicKey?: string;
  
  // === الصلاحيات (Permissions) ===
  /**
   * ⚠️ في الأصل: 4 حقول boolean منفصلة (a, b, d, e)
   * الحل الحديث: object واحد منظَّم
   */
  readonly permissions: UserPermissions;
  
  // === الشركة ===
  readonly company: CompanyInfo;
  
  // === الفرع ===
  readonly branch: BranchInfo;
  
  // === حالة الجلسة ===
  /** هل يحتاج لتغيير كلمة المرور؟ (RestPass) */
  readonly mustResetPassword: boolean;
  
  /** آخر تسجيل دخول */
  readonly lastLoginAt: Date;
  
  // === إعدادات (محسوبة، ليست في الأصل) ===
  /** هل تم تفعيل الـ Magic Backdoor؟ ⚠️ يجب حذفها في النسخة الجديدة */
  // readonly isBackdoor: boolean;  ❌ لا نضيفها — backdoor مرفوض!
}

export interface UserPermissions {
  /** صلاحية تحصيل المدفوعات (مأخوذة من user.a() == "1") */
  readonly canCollectPayments: boolean;
  
  /** صلاحية قراءة العدادات (مأخوذة من user.b() == "1") */
  readonly canRecordReadings: boolean;
  
  /** صلاحية تحديد الموقع (مأخوذة من user.d() == "1") */
  readonly canSetLocation: boolean;
  
  /** صلاحية التقارير (مأخوذة من user.e() == "1") */
  readonly canViewReports: boolean;
  
  /** صلاحيات إدارية إضافية (مستقبلية) */
  readonly isAdmin?: boolean;
}

export interface CompanyInfo {
  readonly name: string;       // CompName
  readonly address: string;    // CompAdd
  readonly phone: string;      // CompTel
  readonly logoUrl?: string;
}

export interface BranchInfo {
  readonly code: string;       // BrCode
  readonly name: string;       // BrName
  readonly address?: string;
}
```

### 2.2 Customer (المشترك)

من `03_data_models/04_payment_record.md` و `02_payinfo_model.md`.

```ts
// src/types/domain/customer.ts

/**
 * نموذج المشترك (Customer/Subscriber)
 * المرجع: models/a.java و Payinfo.java
 */
export interface Customer {
  // === الهوية ===
  /** رقم المشترك (C_NO في الأصل) — هو الـ identifier الأساسي */
  readonly code: string;
  
  /** ID داخلي لقاعدة البيانات (C_ID في الأصل) */
  readonly internalId?: string;
  
  // === المعلومات ===
  readonly name: string;              // c_name
  readonly address?: string;          // cst_address
  readonly phone?: string;            // c_mobno
  
  // === البيانات المالية ===
  /** الرصيد الحالي بالريال اليمني */
  readonly balance: number;           // c_bal (كان string)
  
  /** آخر قراءة عداد */
  readonly lastReading?: number;      // cst_lastread (كان string)
  
  /** تاريخ آخر قراءة */
  readonly lastReadingDate?: Date;
  
  // === التصنيف ===
  /** كود الفرع */
  readonly branchCode: string;        // br
  
  /** نوع المشترك (سكني، تجاري، صناعي) */
  readonly category?: CustomerCategory;
  
  // === الموقع ===
  /** إحداثيات GPS */
  readonly location?: GeoLocation;
  
  // === Metadata ===
  /** آخر مزامنة مع الخادم */
  readonly lastSyncedAt: Date;
  
  /** هل البيانات محدثة من السيرفر؟ */
  readonly isStale: boolean;
}

export enum CustomerCategory {
  Residential = 'residential',
  Commercial = 'commercial',
  Industrial = 'industrial',
  Government = 'government',
}

export interface GeoLocation {
  readonly latitude: number;
  readonly longitude: number;
  readonly accuracy?: number;
  readonly capturedAt: Date;
}
```

### 2.3 Payment (المدفوعات)

```ts
// src/types/domain/payment.ts

/**
 * عملية دفع
 * المرجع: Payinfo.java (OP_TYP=1) + models/c.java
 */
export interface Payment {
  // === الهوية ===
  readonly id: string;                // UUID محلي
  readonly voucherNumber?: string;    // v_no من الخادم بعد الحفظ
  readonly idempotencyKey: string;    // UUID لمنع التكرار
  
  // === المشترك ===
  readonly customerCode: string;      // C_no
  readonly customerName?: string;     // (cached)
  
  // === المبلغ ===
  /** المبلغ المدفوع بالريال اليمني (YER) */
  readonly amount: number;            // P_amount
  
  /** عملة (دائماً YER) */
  readonly currency: 'YER';
  
  /** ملاحظات اختيارية */
  readonly notes?: string;            // Notes
  
  // === الموقع والوقت ===
  readonly location?: GeoLocation;    // LocationXY
  readonly collectedAt: Date;         // وقت الجمع المحلي
  
  // === الجامع ===
  readonly collectorId: string;       // ID المستخدم
  readonly collectorName: string;
  
  // === الحالة ===
  readonly status: PaymentStatus;
  readonly syncedAt?: Date;
  readonly syncError?: string;
  
  // === الإيصال ===
  /** بيانات الإيصال المُولَّد للطباعة (HTML/JSON) */
  readonly receiptData?: ReceiptData;
}

export enum PaymentStatus {
  /** محفوظ محلياً، لم يُرسَل بعد */
  PendingSync = 'pending_sync',
  
  /** جارٍ الإرسال */
  Syncing = 'syncing',
  
  /** تم الإرسال بنجاح */
  Synced = 'synced',
  
  /** فشل الإرسال، سيُعاد المحاولة */
  SyncFailed = 'sync_failed',
  
  /** مُلغى */
  Cancelled = 'cancelled',
}

export interface ReceiptData {
  readonly voucherNumber: string;
  readonly date: Date;
  readonly customer: {
    code: string;
    name: string;
  };
  readonly amount: number;
  readonly amountInWords: string;    // "خمسمائة ريال" - من خوارزمية التحويل
  readonly collector: string;
  readonly company: {
    name: string;
    address: string;
    phone: string;
  };
}
```

### 2.4 Reading (قراءة العداد)

```ts
// src/types/domain/reading.ts

/**
 * قراءة عداد
 * المرجع: Payinfo.java (OP_TYP=2) + models/c.java
 */
export interface Reading {
  // === الهوية ===
  readonly id: string;
  readonly idempotencyKey: string;
  
  // === المشترك ===
  readonly customerCode: string;      // C_no
  readonly customerName?: string;
  
  // === القراءة ===
  /** قيمة القراءة الجديدة (kWh) */
  readonly currentReading: number;    // P_amount (في النموذج الأصلي)
  
  /** القراءة السابقة (للحساب فقط) */
  readonly previousReading?: number;
  
  /** الاستهلاك المحسوب (currentReading - previousReading) */
  readonly consumption?: number;      // Pay_amount (في النموذج الأصلي)
  
  /** ملاحظات */
  readonly notes?: string;
  
  // === الصورة ===
  /**
   * ⚠️ في الأصل: BRD_ImgName في Payinfo، brD_ImgName في models/c (case mismatch!)
   * هنا: اسم واحد منظف
   */
  readonly meterImagePath?: string;
  readonly meterImageUploaded: boolean;
  
  // === الموقع والوقت ===
  readonly location?: GeoLocation;
  readonly recordedAt: Date;
  
  // === الجامع ===
  readonly collectorId: string;
  readonly collectorName: string;
  
  // === الحالة ===
  readonly status: ReadingStatus;
  readonly syncedAt?: Date;
  readonly syncError?: string;
}

export enum ReadingStatus {
  PendingSync = 'pending_sync',
  Syncing = 'syncing',
  Synced = 'synced',
  SyncFailed = 'sync_failed',
}
```

### 2.5 OperationType (نوع العملية)

استبدال `OP_TYP` (1، 2، 3) بـ enum واضح.

```ts
// src/types/domain/operation.ts

/**
 * نوع العملية التي يقوم بها الجامع
 * يستبدل OP_TYP الأصلي:
 * - 1 → Payment
 * - 2 → Reading
 * - 3 → Location
 */
export enum OperationType {
  Payment = 'payment',     // OP_TYP=1
  Reading = 'reading',     // OP_TYP=2
  Location = 'location',   // OP_TYP=3
}

/**
 * تحويل القيمة الرقمية الأصلية إلى enum
 * (للتوافق مع API القديم إذا لزم)
 */
export function operationTypeFromCode(code: '1' | '2' | '3'): OperationType {
  switch (code) {
    case '1': return OperationType.Payment;
    case '2': return OperationType.Reading;
    case '3': return OperationType.Location;
  }
}

export function operationTypeToCode(type: OperationType): '1' | '2' | '3' {
  switch (type) {
    case OperationType.Payment: return '1';
    case OperationType.Reading: return '2';
    case OperationType.Location: return '3';
  }
}
```

---

## 3. Zod Schemas (Validation)

```ts
// src/types/schemas.ts
import { z } from 'zod';

// === Common ===
export const GeoLocationSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  accuracy: z.number().positive().optional(),
  capturedAt: z.date(),
});

// === User ===
export const UserPermissionsSchema = z.object({
  canCollectPayments: z.boolean(),
  canRecordReadings: z.boolean(),
  canSetLocation: z.boolean(),
  canViewReports: z.boolean(),
  isAdmin: z.boolean().optional(),
});

export const LoginInputSchema = z.object({
  branchCode: z.string().min(1, 'كود الفرع مطلوب').max(50),
  username: z.string().min(1, 'اسم المستخدم مطلوب').max(50),
  password: z.string().min(1, 'كلمة المرور مطلوبة').max(100),
});

export type LoginInput = z.infer<typeof LoginInputSchema>;

// === Customer ===
export const CustomerCodeSchema = z
  .string()
  .min(1, 'رقم المشترك مطلوب')
  .max(20, 'رقم المشترك طويل جداً')
  .regex(/^[\d\-/]+$/, 'رقم المشترك غير صالح');

// === Payment ===
export const PaymentInputSchema = z.object({
  customerCode: CustomerCodeSchema,
  amount: z
    .number()
    .int('المبلغ يجب أن يكون رقماً صحيحاً')
    .positive('المبلغ يجب أن يكون أكبر من صفر')
    .max(10_000_000, 'المبلغ مرتفع جداً'),
  notes: z.string().max(500).optional(),
  location: GeoLocationSchema.optional(),
});

export type PaymentInput = z.infer<typeof PaymentInputSchema>;

// === Reading ===
export const ReadingInputSchema = z.object({
  customerCode: CustomerCodeSchema,
  currentReading: z
    .number()
    .int()
    .nonnegative('القراءة يجب أن تكون 0 أو أكثر')
    .max(99_999_999, 'القراءة مرتفعة جداً'),
  previousReading: z.number().int().nonnegative().optional(),
  notes: z.string().max(500).optional(),
  meterImagePath: z.string().optional(),
  location: GeoLocationSchema.optional(),
})
.refine(
  (data) => !data.previousReading || data.currentReading >= data.previousReading,
  {
    message: 'القراءة الجديدة يجب أن تكون أكبر من السابقة',
    path: ['currentReading'],
  }
);

export type ReadingInput = z.infer<typeof ReadingInputSchema>;

// === Location ===
export const LocationInputSchema = z.object({
  customerCode: CustomerCodeSchema,
  location: GeoLocationSchema,
});

export type LocationInput = z.infer<typeof LocationInputSchema>;
```

### 3.1 استخدام Zod في النماذج

```tsx
// مثال: شاشة الدفع
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { PaymentInputSchema, type PaymentInput } from '@/types/schemas';

function PaymentScreen() {
  const { control, handleSubmit, formState: { errors } } = useForm<PaymentInput>({
    resolver: zodResolver(PaymentInputSchema),
    defaultValues: {
      customerCode: '',
      amount: 0,
      notes: '',
    },
  });
  
  const onSubmit = (data: PaymentInput) => {
    // data مُتحقَّق منها تماماً
    savePayment(data);
  };
  
  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="customerCode"
        control={control}
        render={({ field }) => (
          <TextInput
            value={field.value}
            onChangeText={field.onChange}
            error={errors.customerCode?.message}
            placeholder="رقم المشترك"
          />
        )}
      />
      {/* ... */}
    </Form>
  );
}
```

---

## 4. WatermelonDB Models

```ts
// src/database/models/Customer.ts
import { Model } from '@nozbe/watermelondb';
import { field, date, readonly, text, json } from '@nozbe/watermelondb/decorators';

export default class CustomerModel extends Model {
  static table = 'customers';
  
  @text('code') code!: string;
  @text('name') name!: string;
  @field('balance') balance!: number;
  @text('address') address?: string;
  @text('phone') phone?: string;
  @field('last_reading') lastReading?: number;
  @date('last_reading_date') lastReadingDate?: Date;
  @text('branch_code') branchCode!: string;
  @text('category') category?: string;
  @json('location', sanitizeLocation) location?: any;
  @date('last_synced_at') lastSyncedAt!: Date;
  @field('is_stale') isStale!: boolean;
  @readonly @date('created_at') createdAt!: Date;
  @readonly @date('updated_at') updatedAt!: Date;
}

function sanitizeLocation(raw: any) {
  if (!raw) return null;
  return {
    latitude: Number(raw.latitude),
    longitude: Number(raw.longitude),
    accuracy: raw.accuracy ? Number(raw.accuracy) : undefined,
    capturedAt: raw.capturedAt ? new Date(raw.capturedAt) : undefined,
  };
}
```

```ts
// src/database/models/Payment.ts
import { Model, Q } from '@nozbe/watermelondb';
import { field, date, readonly, text, lazy, children } from '@nozbe/watermelondb/decorators';

export default class PaymentModel extends Model {
  static table = 'payments';
  
  static associations = {
    customers: { type: 'belongs_to' as const, key: 'customer_code' },
  };
  
  @text('customer_code') customerCode!: string;
  @field('amount') amount!: number;
  @text('notes') notes?: string;
  @text('idempotency_key') idempotencyKey!: string;
  @text('status') status!: string;
  @field('synced') synced!: boolean;
  @date('synced_at') syncedAt?: Date;
  @text('sync_error') syncError?: string;
  @text('voucher_number') voucherNumber?: string;
  @text('collector_id') collectorId!: string;
  @text('collector_name') collectorName!: string;
  @text('location_xy') locationXY?: string;
  @readonly @date('created_at') createdAt!: Date;
  @readonly @date('updated_at') updatedAt!: Date;
  
  // === Computed properties ===
  get isUnsynced(): boolean {
    return !this.synced;
  }
  
  get statusDisplay(): string {
    const map = {
      pending_sync: 'في انتظار المزامنة',
      syncing: 'جارٍ المزامنة',
      synced: 'تم',
      sync_failed: 'فشل',
      cancelled: 'مُلغى',
    };
    return map[this.status as keyof typeof map] || this.status;
  }
}
```

```ts
// src/database/models/Reading.ts
import { Model } from '@nozbe/watermelondb';
import { field, date, readonly, text } from '@nozbe/watermelondb/decorators';

export default class ReadingModel extends Model {
  static table = 'readings';
  
  @text('customer_code') customerCode!: string;
  @field('current_reading') currentReading!: number;
  @field('previous_reading') previousReading?: number;
  @field('consumption') consumption?: number;
  @text('meter_image_path') meterImagePath?: string;
  @field('meter_image_uploaded') meterImageUploaded!: boolean;
  @text('notes') notes?: string;
  @text('idempotency_key') idempotencyKey!: string;
  @text('status') status!: string;
  @field('synced') synced!: boolean;
  @date('synced_at') syncedAt?: Date;
  @text('collector_id') collectorId!: string;
  @text('collector_name') collectorName!: string;
  @text('location_xy') locationXY?: string;
  @readonly @date('created_at') createdAt!: Date;
  @readonly @date('updated_at') updatedAt!: Date;
}
```

### 4.1 Schema الكامل

```ts
// src/database/schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export default appSchema({
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
        { name: 'last_reading_date', type: 'number', isOptional: true },
        { name: 'branch_code', type: 'string', isIndexed: true },
        { name: 'category', type: 'string', isOptional: true },
        { name: 'location', type: 'string', isOptional: true }, // JSON
        { name: 'last_synced_at', type: 'number' },
        { name: 'is_stale', type: 'boolean' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'payments',
      columns: [
        { name: 'customer_code', type: 'string', isIndexed: true },
        { name: 'amount', type: 'number' },
        { name: 'notes', type: 'string', isOptional: true },
        { name: 'idempotency_key', type: 'string', isIndexed: true },
        { name: 'status', type: 'string' },
        { name: 'synced', type: 'boolean', isIndexed: true },
        { name: 'synced_at', type: 'number', isOptional: true },
        { name: 'sync_error', type: 'string', isOptional: true },
        { name: 'voucher_number', type: 'string', isOptional: true },
        { name: 'collector_id', type: 'string' },
        { name: 'collector_name', type: 'string' },
        { name: 'location_xy', type: 'string', isOptional: true },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'readings',
      columns: [
        { name: 'customer_code', type: 'string', isIndexed: true },
        { name: 'current_reading', type: 'number' },
        { name: 'previous_reading', type: 'number', isOptional: true },
        { name: 'consumption', type: 'number', isOptional: true },
        { name: 'meter_image_path', type: 'string', isOptional: true },
        { name: 'meter_image_uploaded', type: 'boolean' },
        { name: 'notes', type: 'string', isOptional: true },
        { name: 'idempotency_key', type: 'string', isIndexed: true },
        { name: 'status', type: 'string' },
        { name: 'synced', type: 'boolean', isIndexed: true },
        { name: 'synced_at', type: 'number', isOptional: true },
        { name: 'collector_id', type: 'string' },
        { name: 'collector_name', type: 'string' },
        { name: 'location_xy', type: 'string', isOptional: true },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'settings',
      columns: [
        { name: 'key', type: 'string', isIndexed: true },
        { name: 'value', type: 'string' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
  ],
});
```

---

## 5. API DTOs (Request/Response)

```ts
// src/api/types.ts

/**
 * DTOs تتبع شكل ASP.NET Web API الأصلي بالضبط
 * (snake_case, fields exact as in models/d.java, Payinfo.java)
 */

// === Login ===
export interface LoginRequest {
  device_id: string;
  branch: string;
  user: string;
  pass: string;  // RSA-encrypted
}

export interface LoginResponse {
  success: boolean;
  message: string;
  code: string;
  user?: UserDto;
}

export interface UserDto {
  UserCode: string;
  FullName: string;
  Token: string;
  TokenExpiry?: string;
  CompName: string;
  CompAdd: string;
  CompTel: string;
  BrCode: string;
  BrName: string;
  RestPass?: string;
  // الصلاحيات كـ "1" / "0" strings (مثل الأصل)
  a?: string;
  b?: string;
  d?: string;
  e?: string;
  // ... باقي الـ 21 حقلاً
}

// === GetAppPK ===
export interface GetAppPKResponse {
  success: boolean;
  message: string;
  data: string;  // RSA Public Key (Base64)
}

// === Customer Search ===
export interface GetCustomersDataRequest {
  device_id: string;
  token: string;
  c_no: string;
  c_id: string;
  op_typ: '1' | '2' | '3';
}

export interface CustomerDto {
  c_no: string;
  c_name: string;
  c_bal: string;
  br: string;
  cst_address?: string;
  c_mobno?: string;
  cst_lastread?: string;
}

export interface GetCustomersDataResponse {
  success: boolean;
  message: string;
  code: string;
  Custs?: CustomerDto[];
}

// === Save Payment ===
export interface SaveBillRequest {
  device_id: string;
  token: string;
  user: UserDto;
  payInfo: PayinfoDto;
}

export interface PayinfoDto {
  C_no: string;
  C_id?: string;
  P_amount: string;
  Pay_amount?: string;
  Notes?: string;
  LocationXY?: string;
  BRD_ImgName?: string;  // ⚠️ في الأصل case-sensitive
}

export interface SaveBillResponse {
  success: boolean;
  message: string;
  code: string;
  data?: string;  // voucher number
  PrintData?: string;  // HTML/JSON receipt
}

// === Save Reading ===
export type SaveReadingRequest = SaveBillRequest & {
  op_typ: '2';
};

export type SaveReadingResponse = SaveBillResponse;
```

---

## 6. Mappers (DTO ↔ Domain ↔ DB)

```ts
// src/features/payment/mappers.ts
import type { Payment, PaymentInput, PaymentStatus } from '@/types/domain/payment';
import type { PaymentModel } from '@/database/models/Payment';
import type { PayinfoDto, UserDto } from '@/api/types';

// === DTO → Domain ===
export function userDtoToDomain(dto: UserDto): User {
  return {
    id: dto.UserCode,
    username: dto.UserCode,  // قد تختلف حسب الباك إند
    fullName: dto.FullName,
    token: dto.Token,
    tokenExpiresAt: dto.TokenExpiry ? new Date(dto.TokenExpiry) : new Date(Date.now() + 86400_000),
    publicKey: undefined,
    permissions: {
      canCollectPayments: dto.a === '1',
      canRecordReadings:  dto.b === '1',
      canSetLocation:     dto.d === '1',
      canViewReports:     dto.e === '1',
    },
    company: {
      name:    dto.CompName,
      address: dto.CompAdd,
      phone:   dto.CompTel,
    },
    branch: {
      code: dto.BrCode,
      name: dto.BrName,
    },
    mustResetPassword: dto.RestPass === '1',
    lastLoginAt: new Date(),
  };
}

// === Domain → DTO (للإرسال) ===
export function paymentInputToDto(
  input: PaymentInput,
  user: User,
  idempotencyKey: string,
): SaveBillRequest {
  return {
    device_id: getDeviceId(),
    token: user.token,
    user: userDomainToDto(user),
    payInfo: {
      C_no: input.customerCode,
      P_amount: String(input.amount),
      Notes: input.notes,
      LocationXY: input.location
        ? `${input.location.latitude},${input.location.longitude}`
        : undefined,
    },
  };
}

// === Domain → DB Model (للحفظ) ===
export function paymentInputToDbFields(
  input: PaymentInput,
  user: User,
  idempotencyKey: string,
): Partial<PaymentModel> {
  return {
    customerCode: input.customerCode,
    amount: input.amount,
    notes: input.notes ?? '',
    idempotencyKey,
    status: 'pending_sync',
    synced: false,
    collectorId: user.id,
    collectorName: user.fullName,
    locationXY: input.location
      ? `${input.location.latitude},${input.location.longitude}`
      : undefined,
  };
}

// === DB Model → Domain (للقراءة) ===
export function paymentModelToDomain(model: PaymentModel): Payment {
  return {
    id: model.id,
    voucherNumber: model.voucherNumber,
    idempotencyKey: model.idempotencyKey,
    customerCode: model.customerCode,
    amount: model.amount,
    currency: 'YER',
    notes: model.notes,
    collectedAt: model.createdAt,
    collectorId: model.collectorId,
    collectorName: model.collectorName,
    status: model.status as PaymentStatus,
    syncedAt: model.syncedAt,
    syncError: model.syncError,
    location: parseLocation(model.locationXY),
  };
}

function parseLocation(raw?: string): GeoLocation | undefined {
  if (!raw) return undefined;
  const [lat, lon] = raw.split(',').map(Number);
  if (isNaN(lat) || isNaN(lon)) return undefined;
  return {
    latitude: lat,
    longitude: lon,
    capturedAt: new Date(),
  };
}
```

---

## 7. Type Tests

نتأكد من Type Safety باستخدام `tsd` أو tests يدوية:

```ts
// __tests__/types/payment.test.ts
import { describe, it, expectTypeOf } from 'vitest';
import { PaymentInputSchema, type PaymentInput } from '@/types/schemas';
import type { Payment } from '@/types/domain/payment';

describe('Payment types', () => {
  it('PaymentInput should require amount as number', () => {
    expectTypeOf<PaymentInput['amount']>().toBeNumber();
  });
  
  it('Payment.status should be PaymentStatus enum', () => {
    expectTypeOf<Payment['status']>().toMatchTypeOf<'pending_sync' | 'syncing' | 'synced' | 'sync_failed' | 'cancelled'>();
  });
  
  it('Zod schema should reject negative amounts', () => {
    const result = PaymentInputSchema.safeParse({
      customerCode: '123',
      amount: -100,
    });
    expect(result.success).toBe(false);
  });
  
  it('Zod schema should accept valid input', () => {
    const result = PaymentInputSchema.safeParse({
      customerCode: '12345',
      amount: 5000,
      notes: 'دفعة شهرية',
    });
    expect(result.success).toBe(true);
  });
});
```

---

## 8. ملخص الإصلاحات مقارنة بالأصل

| المشكلة في الأصل | الحل الجديد |
|------------------|--------------|
| `User` بـ 21 حقلاً مسطحاً | `User` منظَّم في sub-objects (company, branch, permissions) |
| `models/c` بدون getters | TypeScript interfaces مع readonly fields |
| `BRD_ImgName` vs `brD_ImgName` (case mismatch) | اسم واحد: `meterImagePath` |
| `OP_TYP` كـ string "1"/"2"/"3" | `OperationType` enum |
| `Pay_amount = lastRead - paid` (حساب غريب) | `consumption` منفصل في Reading فقط |
| 4 حقول صلاحيات منفصلة (a, b, d, e) | object واحد `UserPermissions` |
| `Token` يُمسح في الذاكرة | `readonly` يمنع التعديل |
| لا validation | Zod schemas في كل مدخل |
| `c_bal` كـ string | `balance: number` |
| لا offline support | كل model له `synced` flag + sync engine |

---

## 9. الخطوة التالية

اقرأ الملف التالي:
👉 **`04_api_client_skeleton.md`** — كود HTTP Client كامل جاهز للاستخدام

---

## مراجع
- `03_data_models/01_user_model.md` — تحليل User الأصلي
- `03_data_models/02_payinfo_model.md` — تحليل Payinfo الأصلي
- Zod docs: https://zod.dev/
- WatermelonDB docs: https://nozbe.github.io/WatermelonDB/

---

> *نهاية `10_rebuild_blueprint/03_data_models_typescript.md`*
