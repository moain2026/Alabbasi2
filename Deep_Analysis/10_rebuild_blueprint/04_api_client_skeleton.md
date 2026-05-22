# مخطط إعادة البناء — هيكل HTTP Client

> **الملف:** `10_rebuild_blueprint/04_api_client_skeleton.md`
> **الغرض:** كود كامل جاهز لطبقة الشبكة (Network Layer) باستخدام Axios + TypeScript.
> **المرجع:** يستبدل `c.b.a.f.c` (Volley + JSON-Java) من التطبيق الأصلي.

---

## 📋 جدول المحتويات

1. [نظرة عامة](#1-نظرة-عامة)
2. [إعداد Axios Client](#2-إعداد-axios-client)
3. [Interceptors](#3-interceptors)
4. [SSL Pinning](#4-ssl-pinning)
5. [Endpoint Constants](#5-endpoint-constants)
6. [Feature APIs](#6-feature-apis)
7. [Error Handling](#7-error-handling)
8. [Retry Strategy](#8-retry-strategy)
9. [React Query Integration](#9-react-query-integration)
10. [Testing](#10-testing)

---

## 1. نظرة عامة

### 1.1 ما الذي نستبدله؟

| التطبيق الأصلي | البديل الحديث |
|----------------|----------------|
| Volley (`c.a.b.*`) | Axios |
| `c.b.a.f.c` wrapper | `apiClient` instance |
| `c.b.a.f.b` business calls | Feature-specific API modules |
| `c.b.a.f.d` (Empty TrustManager) ⚠️ | SSL Pinning (`react-native-ssl-pinning`) |
| 10s timeout hardcoded | Configurable timeouts per endpoint |
| Gson serialization | Native JSON + Zod validation |
| لا retry logic | Exponential backoff retry |
| Token في كل request يدوياً | Interceptor تلقائي |

### 1.2 المعمارية

```
┌─────────────────────────────────────────────────────────────┐
│                    Feature API Modules                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  authApi │ │paymentApi│ │customerApi│ │readingApi│       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
└───────┼────────────┼────────────┼────────────┼─────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                          │
                ┌─────────▼─────────┐
                │  apiClient (Axios)│
                │                   │
                │  Interceptors:    │
                │  - Request: auth  │
                │  - Request: log   │
                │  - Response: error│
                │  - Response: retry│
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │   SSL Pinning     │
                │  Certificate Check │
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │   HTTPS Network   │
                │   (ASP.NET API)   │
                └───────────────────┘
```

---

## 2. إعداد Axios Client

### 2.1 الـ Client الرئيسي

```ts
// src/api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import Config from 'react-native-config';
import { applyRequestInterceptors } from './interceptors/request';
import { applyResponseInterceptors } from './interceptors/response';
import { applyRetryLogic } from './interceptors/retry';

/**
 * HTTP Client الرئيسي للتطبيق
 * يستبدل c.b.a.f.c من التطبيق الأصلي
 */
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: Config.API_BASE_URL,
    timeout: 15_000,  // 15s (كان 10s في الأصل)
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': `AbbasiyCashiers/${Config.APP_VERSION} (Android)`,
    },
  });
  
  // ترتيب مهم: الـ interceptors تُطبَّق بالترتيب
  applyRequestInterceptors(client);
  applyResponseInterceptors(client);
  applyRetryLogic(client);
  
  return client;
}

export const apiClient = createApiClient();

/**
 * تحديث الـ baseURL في وقت التشغيل
 * (للتعامل مع تغيير الخادم عبر deeplink)
 */
export function setApiBaseUrl(url: string): void {
  apiClient.defaults.baseURL = url;
}

/**
 * تنفيذ طلب بشكل آمن مع type safety
 */
export async function safeRequest<TResponse>(
  config: AxiosRequestConfig,
): Promise<TResponse> {
  try {
    const response = await apiClient.request<TResponse>(config);
    return response.data;
  } catch (error) {
    throw normalizeApiError(error);
  }
}
```

### 2.2 إعدادات Environment

```ts
// src/config/env.ts
import Config from 'react-native-config';
import { z } from 'zod';

const envSchema = z.object({
  API_BASE_URL: z.string().url(),
  API_TIMEOUT: z.string().regex(/^\d+$/).transform(Number).default('15000'),
  ENVIRONMENT: z.enum(['development', 'staging', 'production']),
  APP_VERSION: z.string(),
  SENTRY_DSN: z.string().optional(),
});

function loadEnv() {
  const result = envSchema.safeParse(Config);
  if (!result.success) {
    console.error('Invalid environment variables:', result.error.format());
    throw new Error('Environment configuration is invalid');
  }
  return result.data;
}

export const env = loadEnv();
```

```bash
# .env.example
API_BASE_URL=https://abbasiy.yedns.org:8057/payment
API_TIMEOUT=15000
ENVIRONMENT=development
APP_VERSION=1.0.0
SENTRY_DSN=
```

---

## 3. Interceptors

### 3.1 Request Interceptors

```ts
// src/api/interceptors/request.ts
import { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { getStoredToken, getDeviceId } from '@/features/auth/storage';
import { logRequest } from '@/utils/logger';
import { v4 as uuid } from 'uuid';

/**
 * يضيف:
 * - Authorization header
 * - Device ID
 * - Request ID (لتتبع الطلبات في الـ logs)
 */
export function applyRequestInterceptors(client: AxiosInstance) {
  client.interceptors.request.use(
    async (config) => {
      // 1. إضافة token (إذا موجود)
      const token = await getStoredToken();
      if (token) {
        config.headers.set('Authorization', `Bearer ${token}`);
      }
      
      // 2. إضافة Device ID (يستبدل MediaSessionCompat.D() من الأصل)
      const deviceId = await getDeviceId();
      config.headers.set('X-Device-ID', deviceId);
      
      // 3. إضافة Request ID للتتبع
      const requestId = uuid();
      config.headers.set('X-Request-ID', requestId);
      
      // 4. إضافة Locale
      config.headers.set('Accept-Language', 'ar-YE,ar;q=0.9,en;q=0.5');
      
      // 5. إضافة Timestamp
      config.headers.set('X-Timestamp', new Date().toISOString());
      
      // 6. Logging
      logRequest(config, requestId);
      
      return config;
    },
    (error) => Promise.reject(error),
  );
}
```

### 3.2 Response Interceptors

```ts
// src/api/interceptors/response.ts
import { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { logResponse, logError } from '@/utils/logger';
import { ApiError, NetworkError, AuthError, ValidationError } from '../errors';
import { useAuthStore } from '@/features/auth/store';

export function applyResponseInterceptors(client: AxiosInstance) {
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      logResponse(response);
      
      // الباك إند ASP.NET يرسل أحياناً status 200 مع success=false
      const data = response.data;
      if (data && typeof data === 'object' && 'success' in data && !data.success) {
        throw new ApiError(
          data.message || 'فشل في تنفيذ العملية',
          data.code,
          response.status,
        );
      }
      
      return response;
    },
    async (error: AxiosError) => {
      logError(error);
      
      // === Network errors ===
      if (!error.response) {
        if (error.code === 'ECONNABORTED') {
          throw new NetworkError('انتهت مهلة الاتصال، تحقق من الإنترنت');
        }
        if (error.message?.includes('Network')) {
          throw new NetworkError('لا يوجد اتصال بالإنترنت');
        }
        throw new NetworkError(error.message);
      }
      
      // === HTTP errors ===
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Token غير صالح أو منتهي
          useAuthStore.getState().logout();
          throw new AuthError('انتهت الجلسة، يرجى إعادة تسجيل الدخول');
        
        case 403:
          throw new AuthError('ليس لديك صلاحية لهذا الإجراء');
        
        case 404:
          throw new ApiError('المورد غير موجود', 'NOT_FOUND', 404);
        
        case 422:
        case 400:
          throw new ValidationError(
            (data as any)?.message || 'بيانات غير صالحة',
            (data as any)?.errors,
          );
        
        case 429:
          throw new ApiError('عدد الطلبات كبير، حاول لاحقاً', 'RATE_LIMIT', 429);
        
        case 500:
        case 502:
        case 503:
          throw new ApiError('خطأ في الخادم، حاول لاحقاً', 'SERVER_ERROR', status);
        
        default:
          throw new ApiError(
            (data as any)?.message || 'خطأ غير متوقع',
            'UNKNOWN',
            status,
          );
      }
    },
  );
}
```

### 3.3 Retry Logic

```ts
// src/api/interceptors/retry.ts
import { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

interface RetryConfig extends InternalAxiosRequestConfig {
  _retryCount?: number;
  _maxRetries?: number;
}

const MAX_RETRIES = 3;
const RETRY_DELAY_BASE = 1000;  // 1s

export function applyRetryLogic(client: AxiosInstance) {
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const config = error.config as RetryConfig;
      if (!config) return Promise.reject(error);
      
      // التهيئة الأولى
      config._retryCount = config._retryCount ?? 0;
      config._maxRetries = config._maxRetries ?? MAX_RETRIES;
      
      // لا نُعيد المحاولة لأنواع معينة
      if (!shouldRetry(error)) {
        return Promise.reject(error);
      }
      
      // فحص الحد الأقصى
      if (config._retryCount >= config._maxRetries) {
        return Promise.reject(error);
      }
      
      config._retryCount++;
      
      // Exponential backoff: 1s, 2s, 4s
      const delay = RETRY_DELAY_BASE * Math.pow(2, config._retryCount - 1);
      await sleep(delay);
      
      console.log(`Retry attempt ${config._retryCount}/${config._maxRetries} after ${delay}ms`);
      
      return client.request(config);
    },
  );
}

function shouldRetry(error: AxiosError): boolean {
  // أعد المحاولة فقط لـ:
  // - أخطاء الشبكة
  // - أخطاء السيرفر 5xx
  // - timeout
  
  if (!error.response) {
    return true;  // network error
  }
  
  const status = error.response.status;
  return status >= 500 && status < 600;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

---

## 4. SSL Pinning

### 4.1 الفكرة

نستبدل `c.b.a.f.d` (Empty X509TrustManager الذي يقبل **أي شهادة**) بـ SSL Pinning حقيقي.

```ts
// src/api/ssl-pinning.ts
import { fetch as pinnedFetch } from 'react-native-ssl-pinning';

interface PinnedFetchOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: string;
  sslPinning?: {
    certs: string[];  // أسماء الشهادات في assets/certs/
  };
  timeoutInterval?: number;
}

/**
 * البديل الآمن لـ Axios عند الحاجة لـ SSL Pinning
 * نستخدمه في الإنتاج فقط (في dev: Axios عادي)
 */
export async function fetchWithPinning(
  url: string,
  options: PinnedFetchOptions = {},
) {
  return pinnedFetch(url, {
    method: options.method ?? 'GET',
    headers: options.headers,
    body: options.body,
    sslPinning: {
      certs: ['abbasiy-cert', 'abbasiy-cert-backup'],  // primary + backup
    },
    timeoutInterval: options.timeoutInterval ?? 15000,
  });
}
```

### 4.2 الإعداد

```bash
# الخطوات:
# 1. احصل على شهادة السيرفر:
openssl s_client -connect abbasiy.yedns.org:8057 -showcerts < /dev/null \
  | openssl x509 -outform DER > android/app/src/main/assets/abbasiy-cert.cer

# 2. كرر للحصول على شهادة احتياطية (backup):
# (مثلاً: شهادة الـ intermediate CA)

# 3. للـ iOS:
cp android/app/src/main/assets/abbasiy-cert.cer ios/AbbasiyCashiers/
```

### 4.3 مفتاح Public Key Pinning (Alternative)

```ts
// أفضل من Cert Pinning لأن الشهادة قد تتغير لكن الـ public key يبقى
export async function pinnedRequest(url: string, options: any) {
  return pinnedFetch(url, {
    ...options,
    sslPinning: {
      certs: ['abbasiy-pubkey-sha256'],
    },
    pkPinning: true,  // public key pinning بدلاً من cert
  });
}
```

---

## 5. Endpoint Constants

```ts
// src/api/endpoints.ts

/**
 * كل الـ endpoints مجمَّعة في مكان واحد
 * المرجع: 02_api_contract/01_endpoints_overview.md
 */
export const ENDPOINTS = {
  // === Users ===
  auth: {
    getAppPK:           '/api/Users/getAppPK',
    login:              '/api/Users/Login',
    changePassword:     '/api/Users/changePasswordRequest',
  },
  
  // === Payment Controller ===
  payment: {
    getCustomersData:        '/api/Payment/GetCustomersData',
    saveBillRequest:         '/api/Payment/saveBillRequest',
    saveReadingRequest:      '/api/Payment/saveReadingRequest',
    saveCustLocation:        '/api/Payment/saveCustLocation',
    getPaymentsReportData:   '/api/Payment/GetPaymentsReportData',
    getReadingListData:      '/api/Payment/GetReadingListData',
  },
} as const;

// Type helper للحصول على kind type-safe على الـ URLs
export type EndpointPath = 
  | typeof ENDPOINTS.auth[keyof typeof ENDPOINTS.auth]
  | typeof ENDPOINTS.payment[keyof typeof ENDPOINTS.payment];
```

---

## 6. Feature APIs

### 6.1 Auth API

```ts
// src/features/auth/api.ts
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import { encryptPasswordWithRSA } from './crypto';
import { getDeviceId } from './device';
import type {
  GetAppPKResponse,
  LoginRequest,
  LoginResponse,
  ChangePasswordRequest,
  ChangePasswordResponse,
} from './types';

export const authApi = {
  /**
   * 1. جلب RSA Public Key قبل تسجيل الدخول
   */
  async getAppPK(): Promise<string> {
    const response = await apiClient.post<GetAppPKResponse>(
      ENDPOINTS.auth.getAppPK,
      {},
    );
    
    if (!response.data.success || !response.data.data) {
      throw new Error('فشل في جلب مفتاح التشفير من الخادم');
    }
    
    return response.data.data;  // RSA Public Key (Base64)
  },
  
  /**
   * 2. تسجيل الدخول
   * كلمة المرور مشفرة بـ RSA قبل الإرسال (مثل الأصل)
   */
  async login(input: {
    branchCode: string;
    username: string;
    password: string;
  }): Promise<LoginResponse> {
    // أولاً نجلب الـ public key
    const publicKey = await authApi.getAppPK();
    
    // ثانياً نشفر كلمة المرور
    const encryptedPassword = encryptPasswordWithRSA(input.password, publicKey);
    
    // ثالثاً نرسل طلب الدخول
    const deviceId = await getDeviceId();
    
    const request: LoginRequest = {
      device_id: deviceId,
      branch: input.branchCode,
      user: input.username,
      pass: encryptedPassword,
    };
    
    const response = await apiClient.post<LoginResponse>(
      ENDPOINTS.auth.login,
      request,
    );
    
    if (!response.data.success) {
      throw new Error(response.data.message || 'فشل تسجيل الدخول');
    }
    
    return response.data;
  },
  
  /**
   * 3. تغيير كلمة المرور
   */
  async changePassword(input: {
    oldPassword: string;
    newPassword: string;
  }): Promise<ChangePasswordResponse> {
    const publicKey = await authApi.getAppPK();
    
    const request: ChangePasswordRequest = {
      device_id: await getDeviceId(),
      old_pass: encryptPasswordWithRSA(input.oldPassword, publicKey),
      new_pass: encryptPasswordWithRSA(input.newPassword, publicKey),
    };
    
    const response = await apiClient.post<ChangePasswordResponse>(
      ENDPOINTS.auth.changePassword,
      request,
    );
    
    return response.data;
  },
};
```

### 6.2 Payment API

```ts
// src/features/payment/api.ts
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import { v4 as uuid } from 'uuid';
import { paymentInputToDto } from './mappers';
import type {
  GetCustomersDataResponse,
  SaveBillRequest,
  SaveBillResponse,
} from '@/api/types';
import type { PaymentInput } from '@/types/schemas';
import type { User } from '@/types/domain/user';

export const paymentApi = {
  /**
   * البحث عن مشترك
   */
  async searchCustomer(input: {
    customerCode: string;
    operationType: '1' | '2' | '3';
  }): Promise<GetCustomersDataResponse> {
    const response = await apiClient.post<GetCustomersDataResponse>(
      ENDPOINTS.payment.getCustomersData,
      {
        c_no: input.customerCode,
        c_id: '',
        op_typ: input.operationType,
      },
    );
    return response.data;
  },
  
  /**
   * حفظ عملية دفع
   * مع Idempotency Key لمنع التكرار
   */
  async savePayment(
    input: PaymentInput,
    user: User,
  ): Promise<SaveBillResponse> {
    const idempotencyKey = uuid();
    const request = paymentInputToDto(input, user, idempotencyKey);
    
    const response = await apiClient.post<SaveBillResponse>(
      ENDPOINTS.payment.saveBillRequest,
      request,
      {
        headers: {
          'X-Idempotency-Key': idempotencyKey,
        },
      },
    );
    
    return response.data;
  },
  
  /**
   * قائمة المدفوعات السابقة (للتقرير في WebView)
   */
  async getPaymentsReport(input: {
    fromDate: string;
    toDate: string;
    customerCode?: string;
  }): Promise<any> {
    const response = await apiClient.post(
      ENDPOINTS.payment.getPaymentsReportData,
      input,
    );
    return response.data;
  },
};
```

### 6.3 Reading API

```ts
// src/features/reading/api.ts
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import { v4 as uuid } from 'uuid';
import type { ReadingInput } from '@/types/schemas';
import type { User } from '@/types/domain/user';

export const readingApi = {
  /**
   * حفظ قراءة عداد
   * + رفع صورة العداد قبل ذلك
   */
  async saveReading(
    input: ReadingInput,
    user: User,
  ): Promise<any> {
    // 1. رفع الصورة أولاً (إن وجدت)
    let imagePath: string | undefined;
    if (input.meterImagePath) {
      imagePath = await uploadMeterImage(input.meterImagePath);
    }
    
    // 2. حفظ القراءة
    const idempotencyKey = uuid();
    const response = await apiClient.post(
      ENDPOINTS.payment.saveReadingRequest,
      {
        token: user.token,
        device_id: await getDeviceId(),
        user: userDomainToDto(user),
        payInfo: {
          C_no: input.customerCode,
          P_amount: String(input.currentReading),
          Pay_amount: input.previousReading 
            ? String(input.currentReading - input.previousReading)
            : undefined,
          Notes: input.notes,
          BRD_ImgName: imagePath,  // ⚠️ field name matches API
          LocationXY: input.location
            ? `${input.location.latitude},${input.location.longitude}`
            : undefined,
        },
        op_typ: '2',
      },
      {
        headers: { 'X-Idempotency-Key': idempotencyKey },
      },
    );
    
    return response.data;
  },
};

async function uploadMeterImage(localPath: string): Promise<string> {
  const formData = new FormData();
  formData.append('image', {
    uri: localPath,
    name: 'meter.jpg',
    type: 'image/jpeg',
  } as any);
  
  const response = await apiClient.post('/api/Upload/MeterImage', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data.path;
}
```

---

## 7. Error Handling

```ts
// src/api/errors.ts

/**
 * Base class لكل أخطاء الـ API
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number,
    public details?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
  }
  
  /** هل الخطأ قابل لإعادة المحاولة؟ */
  get isRetryable(): boolean {
    return this.statusCode >= 500 || this.statusCode === 408 || this.statusCode === 429;
  }
}

export class NetworkError extends ApiError {
  constructor(message: string) {
    super(message, 'NETWORK_ERROR', 0);
    this.name = 'NetworkError';
  }
}

export class AuthError extends ApiError {
  constructor(message: string) {
    super(message, 'AUTH_ERROR', 401);
    this.name = 'AuthError';
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, public fieldErrors?: Record<string, string>) {
    super(message, 'VALIDATION_ERROR', 422);
    this.name = 'ValidationError';
  }
}

/**
 * تحويل أي خطأ إلى ApiError
 */
export function normalizeApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  
  if (error instanceof Error) {
    return new ApiError(error.message, 'UNKNOWN', 0);
  }
  
  return new ApiError('خطأ غير متوقع', 'UNKNOWN', 0);
}
```

### 7.1 رسائل الأخطاء بالعربية

```ts
// src/api/error-messages.ts
import type { ApiError } from './errors';

const messagesMap: Record<string, string> = {
  NETWORK_ERROR: 'لا يوجد اتصال بالإنترنت',
  AUTH_ERROR: 'انتهت الجلسة، يرجى إعادة تسجيل الدخول',
  VALIDATION_ERROR: 'بيانات غير صالحة',
  NOT_FOUND: 'المورد غير موجود',
  RATE_LIMIT: 'عدد الطلبات كبير، حاول لاحقاً',
  SERVER_ERROR: 'خطأ في الخادم، حاول لاحقاً',
  UNKNOWN: 'خطأ غير متوقع، حاول مرة أخرى',
};

export function getErrorMessage(error: ApiError): string {
  return messagesMap[error.code] ?? error.message ?? messagesMap.UNKNOWN;
}
```

---

## 8. Retry Strategy

### 8.1 سياسات إعادة المحاولة

| نوع الخطأ | إعادة المحاولة؟ | عدد المحاولات | التأخير |
|----------|------------------|----------------|---------|
| Network error | ✅ نعم | 3 | 1s, 2s, 4s |
| Timeout | ✅ نعم | 3 | 1s, 2s, 4s |
| 500-599 | ✅ نعم | 3 | 1s, 2s, 4s |
| 429 (Rate limit) | ✅ نعم | 2 | 5s, 10s |
| 401 | ❌ لا | - | - |
| 403 | ❌ لا | - | - |
| 400-499 (other) | ❌ لا | - | - |

### 8.2 Idempotency

لمنع تكرار العمليات الحساسة (مثل حفظ دفعة)، نستخدم **Idempotency Keys**:

```ts
// كل request حساسة لها UUID فريد
const idempotencyKey = uuid();

await apiClient.post('/api/Payment/saveBillRequest', data, {
  headers: { 'X-Idempotency-Key': idempotencyKey },
});

// الخادم يجب أن يتذكر هذا الـ key لمدة 24 ساعة
// إذا جاء نفس الـ key مرة أخرى، يُرجع نفس الرد بدلاً من تنفيذ العملية مرتين
```

---

## 9. React Query Integration

```ts
// src/features/payment/hooks.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { paymentApi } from './api';
import { paymentRepository } from '@/database/repositories';
import type { PaymentInput } from '@/types/schemas';

/**
 * Hook للبحث عن مشترك
 */
export function useCustomerSearch(customerCode: string, enabled = true) {
  return useQuery({
    queryKey: ['customer', customerCode],
    queryFn: () => paymentApi.searchCustomer({
      customerCode,
      operationType: '1',
    }),
    enabled: enabled && customerCode.length > 0,
    staleTime: 5 * 60_000,  // 5 min
    retry: 2,
  });
}

/**
 * Hook لحفظ دفعة (Offline-first)
 */
export function useSavePayment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: PaymentInput) => {
      // 1. احفظ محلياً في WatermelonDB
      const payment = await paymentRepository.create(input);
      
      // 2. حاول الإرسال للخادم (async)
      try {
        const response = await paymentApi.savePayment(input, user);
        await paymentRepository.markSynced(payment.id, response.data);
      } catch (error) {
        // فشل في المزامنة، سيُعاد المحاولة بواسطة Sync Engine
        console.warn('Payment sync failed, queued for retry', error);
      }
      
      return payment;
    },
    onSuccess: () => {
      // أبطل cache للقوائم المتعلقة
      queryClient.invalidateQueries({ queryKey: ['payments'] });
    },
  });
}

/**
 * Hook لجلب تقرير المدفوعات
 */
export function usePaymentsReport(fromDate: string, toDate: string) {
  return useQuery({
    queryKey: ['payments', 'report', fromDate, toDate],
    queryFn: () => paymentApi.getPaymentsReport({ fromDate, toDate }),
    staleTime: 30 * 60_000,  // 30 min
  });
}
```

---

## 10. Testing

### 10.1 Unit Tests

```ts
// __tests__/api/client.test.ts
import { apiClient } from '@/api/client';
import MockAdapter from 'axios-mock-adapter';

describe('apiClient', () => {
  let mock: MockAdapter;
  
  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });
  
  afterEach(() => {
    mock.restore();
  });
  
  it('should add auth header automatically', async () => {
    // إعداد token
    await storeToken('test-token-123');
    
    mock.onPost('/api/test').reply((config) => {
      expect(config.headers?.Authorization).toBe('Bearer test-token-123');
      return [200, { success: true }];
    });
    
    await apiClient.post('/api/test');
  });
  
  it('should retry on 500 errors', async () => {
    let attempts = 0;
    mock.onPost('/api/test').reply(() => {
      attempts++;
      if (attempts < 3) return [500];
      return [200, { success: true }];
    });
    
    await apiClient.post('/api/test');
    expect(attempts).toBe(3);
  });
  
  it('should NOT retry on 401', async () => {
    let attempts = 0;
    mock.onPost('/api/test').reply(() => {
      attempts++;
      return [401];
    });
    
    await expect(apiClient.post('/api/test')).rejects.toThrow();
    expect(attempts).toBe(1);
  });
});
```

### 10.2 Integration Tests

```ts
// __tests__/features/payment/api.test.ts
import { paymentApi } from '@/features/payment/api';

describe('paymentApi.savePayment', () => {
  it('should include idempotency key header', async () => {
    const spy = jest.spyOn(apiClient, 'post');
    
    await paymentApi.savePayment(validInput, validUser);
    
    expect(spy).toHaveBeenCalledWith(
      expect.any(String),
      expect.any(Object),
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-Idempotency-Key': expect.any(String),
        }),
      }),
    );
  });
});
```

---

## 11. ملخص الإصلاحات

| المشكلة في الأصل | الحل |
|-------------------|------|
| Empty X509TrustManager ⚠️ | SSL Pinning مع شهادتين (primary + backup) |
| لا retry logic | Exponential backoff على 5xx + network |
| Token مرسل يدوياً في كل طلب | Interceptor تلقائي |
| لا idempotency | `X-Idempotency-Key` header |
| Hardcoded 10s timeout | Configurable per endpoint |
| Error messages بالإنجليزية فقط | رسائل عربية واضحة |
| لا logging | logger متكامل + Sentry |
| لا type safety للـ responses | Full TypeScript + Zod validation |

---

## 12. الخطوة التالية

اقرأ الملف التالي:
👉 **`05_security_improvements.md`** — الإصلاحات الأمنية المطلوبة

---

## مراجع
- `02_api_contract/01_endpoints_overview.md` — قائمة كل الـ endpoints
- `02_api_contract/05_error_codes.md` — رموز الأخطاء
- `03_data_models_typescript.md` — TypeScript types
- Axios docs: https://axios-http.com/
- react-native-ssl-pinning: https://github.com/MaxToyberman/react-native-ssl-pinning

---

> *نهاية `10_rebuild_blueprint/04_api_client_skeleton.md`*
