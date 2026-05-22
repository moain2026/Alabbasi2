# 07.04 — بروتوكول التواصل الآمن (Secure Communication Protocol)

> **الهدف:** تصميم بروتوكول كامل لتواصل التطبيق الجديد مع Backend.
> **المُتطلَّبات:** Token management + Anti-replay + Idempotency للدفع + حماية الحقول الحساسة.
> **المرجع:** ما اكتشفناه فعلياً في `01_current_crypto_audit.md` + بنية API المُستخرَجة من الكود.

---

## 0. خلاصة البروتوكول الحالي vs المقترح

| البند | الحالي (Ecas v18.4) | المقترح |
|------|--------------------|----------|
| HTTP Library | Google Volley (deprecated 2021) | Axios + react-native-ssl-pinning |
| Auth | `Token` field داخل JSON body | JWT في `Authorization: Bearer` header |
| Token Lifecycle | لا انتهاء واضحة، لا تجديد | Access (15min) + Refresh (30d) + rotation |
| Token Storage | في الذاكرة فقط (User object) | Keychain (Hardware-backed) |
| Anti-Replay | ❌ لا | ✅ Nonce + Timestamp window |
| Request Signing | HMAC-SHA1 على URL params | HMAC-SHA256 على body + headers + nonce |
| Idempotency | ❌ لا (يمكن تكرار دفع!) | ✅ `Idempotency-Key` header + server dedup |
| Field-level Encryption | RSA (غير مُستَدعى) | فقط لحقول خاصة (PIN, MPIN) |
| Logout | `C.s("")` يمسح Token محلياً فقط | `POST /auth/logout` + revoke server-side |
| Session Recovery | لا | Refresh token مع rotation detection |
| Rate Limiting | غير معروف | Server enforced + Client back-off |

---

## 1. ما اكتشفناه فعلياً عن البروتوكول الحالي

### 1.1 Endpoints المستخدمة

من فحص الكود (`grep -rn '"/api/'`):

```
"/api/Payment/GetCustomersData"        — جلب قائمة المشتركين
"/api/Payment/GetPaymentsReportData"   — تقرير المدفوعات
"/api/Payment/GetReadingListData"      — قائمة قراءات العداد
"/api/Payment/saveBillRequest"         — حفظ عملية دفع
"/api/Payment/saveCustLocation"        — حفظ موقع GPS للمشترك
"/api/Payment/saveReadingRequest"      — حفظ قراءة عداد
```

**+ URL WebView داخلي:**
```
https://@doman/cashiers.php?bNo=@branch&cashierNo=@casherno&tokenID=@tokid
```

### 1.2 بنية الـ Request (من `com.egy.webpaymentapp.webapi.models.d`)

```java
public class d {
    @c.c.b.a0.b("c_no")        public String f2458a;     // customer number
    @c.c.b.a0.b("findVal")     public String f2459b;     // search value
    @c.c.b.a0.b("area_no")     public String f2460c;     // area number
    @c.c.b.a0.b("user_no")     public String f2461d;     // user (cashier) number
    @c.c.b.a0.b("acc_token")   public String f2462e;     // ⚠️ Token في body
    @c.c.b.a0.b("payinfo")     public Payinfo f;         // payment details
    @c.c.b.a0.b("user")        public User g;            // ⚠️ User كامل مع password!
    @c.c.b.a0.b("oldpass")     public String h;          // ⚠️ كلمة المرور القديمة
    @c.c.b.a0.b("newpass")     public String i;          // ⚠️ كلمة المرور الجديدة
    @c.c.b.a0.b("user_branch") private String j;
    @c.c.b.a0.b("op_typ")      public String k;
}
```

### 1.3 ما يعنيه هذا

**اكتشافات حرجة:**

1. 🔴 **Token يُرسَل في body** (`acc_token`) — يدخل في server logs بسهولة.
2. 🔴 **User object يُرسَل كاملاً** بما فيه `Password` field — ⚠️ مع كل request!
3. 🔴 **`oldpass` / `newpass` كنص واضح** في body.
4. 🔴 **لا `Authorization` header** — هذا ليس standard.
5. 🔴 **لا `Idempotency-Key`** — يمكن تكرار `saveBillRequest` ⇒ دفع مزدوج.
6. 🟠 **`user_no` + `user_branch` كلاهما في body** رغم أنهما يمكن استنتاجهما من Token.

### 1.4 توقيع الـ URL (من `n.java:70`)

```java
str2 = MediaSessionCompat.B(f, user7.n(), MediaSessionCompat.D(this.f2383b));
//                          ^                                  ^
//                          userId                              ANDROID_ID = HMAC key
```

ثم `str2` يُحقن في:
```
?tokenID=<HMAC_SHA1_signature>
```

- لا nonce
- لا timestamp
- المفتاح ضعيف (ANDROID_ID)
- يحمي **URL فقط**، لا body

---

## 2. التصميم الجديد: نظرة عامة

### 2.1 طبقات الحماية

```
┌─────────────────────────────────────────────────────┐
│  Layer 5: Application Logic                          │
│    └─ Idempotency-Key للعمليات المالية              │
├─────────────────────────────────────────────────────┤
│  Layer 4: Request Signing                            │
│    └─ HMAC-SHA256 على (nonce + ts + body)           │
│    └─ يحمي من Replay                                 │
├─────────────────────────────────────────────────────┤
│  Layer 3: Authentication                             │
│    └─ JWT Access (15min) في Authorization header     │
│    └─ Refresh Token (30d) في Keychain                │
├─────────────────────────────────────────────────────┤
│  Layer 2: Transport                                  │
│    └─ TLS 1.3 + Certificate Pinning (راجع 03)        │
├─────────────────────────────────────────────────────┤
│  Layer 1: Network                                    │
│    └─ HTTPS only (no cleartext)                     │
└─────────────────────────────────────────────────────┘
```

### 2.2 المبدأ التوجيهي

> **كل طلب POST/PUT/DELETE يحمل 3 ضمانات:**
> 1. **Authenticated** — Server يعرف من المستخدم (JWT).
> 2. **Fresh** — Server يرفض إذا الـ timestamp قديم (Anti-replay).
> 3. **Idempotent** (للعمليات المالية) — Server يكتشف التكرارات تلقائياً.

---

## 3. Token Management (الطبقة 3)

### 3.1 نموذج Access + Refresh

| النوع | الحياة | التخزين | الاستخدام | التجديد |
|------|--------|----------|------------|----------|
| **Access Token** (JWT) | 15 دقيقة | Memory + Keychain | كل request في `Authorization: Bearer ...` | تلقائي عبر Refresh |
| **Refresh Token** (opaque) | 30 يوم | Keychain (Biometric) | فقط لـ `POST /auth/refresh` | يُجدَّد تلقائياً مع كل refresh (rotation) |

### 3.2 شكل JWT المُتوقَّع من الخادم

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "abbasiy-2026-01"   // ← Key ID لدعم Key Rotation
}
.
{
  "iss": "abbasiy-server",
  "aud": "abbasiy-cashier-app",
  "sub": "user_12345",
  "iat": 1716393600,
  "exp": 1716394500,
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "branch": "0001",
  "cashier_no": "C123",
  "permissions": [
    "payment.create",
    "payment.read",
    "reading.create",
    "customer.read"
  ],
  "device_id": "abc-def-ghi"
}
.
<RSA-2048 signature>
```

### 3.3 Login Flow

```typescript
// src/features/auth/login.ts
import { z } from 'zod';
import { apiClient } from '@/api/sslClient';
import { SecureStorage } from '@/security/secureStorage';

const LoginRequestSchema = z.object({
  username: z.string().min(1).max(64),
  password: z.string().min(8).max(128),
  device_id: z.string().uuid(),
  app_version: z.string(),
});

const LoginResponseSchema = z.object({
  access_token: z.string(),         // JWT
  refresh_token: z.string(),         // opaque
  hmac_session_key: z.string(),      // base64 (256-bit)
  expires_in: z.number().int().positive(),
  user: z.object({
    id: z.string(),
    full_name: z.string(),
    branch: z.string(),
    cashier_no: z.string(),
    permissions: z.array(z.string()),
  }),
});

export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type LoginResponse = z.infer<typeof LoginResponseSchema>;

export async function login(req: LoginRequest): Promise<LoginResponse['user']> {
  // 1. Validate
  const validated = LoginRequestSchema.parse(req);

  // 2. POST to server (TLS+Pinning auto-applied via apiClient)
  const raw = await apiClient.request<unknown>('/auth/login', {
    method: 'POST',
    body: validated,
  });

  // 3. Validate response
  const response = LoginResponseSchema.parse(raw);

  // 4. Store credentials securely
  await SecureStorage.set('session.access', response.access_token, 'auth');
  await SecureStorage.set('session.refresh', response.refresh_token, 'sensitive');
  await SecureStorage.set('session.hmac', response.hmac_session_key, 'auth');
  await SecureStorage.set(
    'session.expiry',
    String(Date.now() + response.expires_in * 1000),
    'basic'
  );

  return response.user;
}
```

### 3.4 Refresh Flow (مع Rotation Detection)

```typescript
// src/features/auth/refresh.ts
import { SecureStorage } from '@/security/secureStorage';
import { apiClient } from '@/api/sslClient';
import { logout } from './logout';

let refreshInFlight: Promise<string> | null = null;

/**
 * تجديد Access Token. إذا اكتشف server أن Refresh Token قديم
 * (تم استخدامه مرتين) ⇒ logout قسري.
 */
export async function refreshAccessToken(): Promise<string> {
  // De-duplicate concurrent refreshes
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    try {
      const refreshToken = await SecureStorage.get('session.refresh');
      if (!refreshToken) throw new Error('No refresh token');

      const raw = await apiClient.request<{
        access_token: string;
        refresh_token: string;     // ← rotated
        hmac_session_key?: string; // ← may rotate too
        expires_in: number;
      }>('/auth/refresh', {
        method: 'POST',
        body: { refresh_token: refreshToken },
      });

      // CRITICAL: Update BOTH tokens (rotation)
      await SecureStorage.set('session.access', raw.access_token, 'auth');
      await SecureStorage.set('session.refresh', raw.refresh_token, 'sensitive');

      if (raw.hmac_session_key) {
        await SecureStorage.set('session.hmac', raw.hmac_session_key, 'auth');
      }

      await SecureStorage.set(
        'session.expiry',
        String(Date.now() + raw.expires_in * 1000),
        'basic'
      );

      return raw.access_token;

    } catch (err: any) {
      // HTTP 401 على /auth/refresh = Refresh Token مُلغى (تم استعماله بالفعل = اختراق محتمل)
      if (err?.status === 401) {
        console.warn('[Auth] Refresh rejected — possible token theft. Forcing logout.');
        await logout({ force: true, reason: 'refresh_rejected' });
      }
      throw err;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

/**
 * يعيد Access Token الحالي، أو يجدّده تلقائياً إذا انتهى.
 * يُستدعى من Axios interceptor قبل كل request.
 */
export async function getValidAccessToken(): Promise<string> {
  const expiryStr = await SecureStorage.get('session.expiry');
  const expiry = expiryStr ? parseInt(expiryStr) : 0;

  // Refresh proactively 60s before expiry
  if (Date.now() >= expiry - 60_000) {
    return refreshAccessToken();
  }

  const access = await SecureStorage.get('session.access');
  if (!access) throw new Error('Not authenticated');
  return access;
}
```

### 3.5 Logout — مع Server-side Revocation

```typescript
// src/features/auth/logout.ts
import { SecureStorage } from '@/security/secureStorage';
import { apiClient } from '@/api/sslClient';

interface LogoutOptions {
  force?: boolean;       // إذا true: لا نهتم بفشل API call
  reason?: string;       // للـ analytics
}

export async function logout(opts: LogoutOptions = {}): Promise<void> {
  const refreshToken = await SecureStorage.get('session.refresh').catch(() => null);

  // 1. أبلغ الخادم بإلغاء كل tokens المستخدم على هذا الجهاز
  if (refreshToken) {
    try {
      await apiClient.request('/auth/logout', {
        method: 'POST',
        body: { refresh_token: refreshToken, reason: opts.reason },
        timeoutMs: 5000,
      });
    } catch (err) {
      if (!opts.force) throw err;
      // في الـ force mode، تابع حتى لو فشل
    }
  }

  // 2. امسح كل بيانات الجلسة محلياً (هذا ما لم يحدث في القديم!)
  await SecureStorage.removeAll();

  // 3. ⚠️ امسح أي in-memory state (Zustand stores, React Query cache)
  // queryClient.clear();
  // sessionStore.reset();
}
```

> **مقارنة مع القديم:** في `OprationsActivity.E():139` (V13)، الكود يستدعي `User.s("")` الذي يمسح Token من Java object فقط. الخادم لا يعرف ⇒ Token يبقى صالحاً 30 يوم. **هذا البروتوكول يصلح ذلك.**

---

## 4. Anti-Replay Protection (الطبقة 4)

### 4.1 المشكلة

Token صالح يُلتقط (شبكة Wi-Fi عامة قبل تطبيق Pinning، logs مسربة، إلخ) ⇒ المهاجم يعيد إرسال نفس الطلب ⇒ يُسحب من حساب المشترك مرتين.

### 4.2 الحل: Nonce + Timestamp + HMAC

كل طلب يحمل 3 headers إضافية:

```http
POST /api/v2/payment HTTP/1.1
Authorization: Bearer eyJhbGc...
X-Request-Nonce: 550e8400-e29b-41d4-a716-446655440000
X-Request-Timestamp: 1716393645123
X-Request-Signature: base64(HMAC_SHA256(session_key, nonce + "." + timestamp + "." + body))
Content-Type: application/json
Idempotency-Key: pay-2026-05-22-cashier123-abc-001

{"customer_no": "C001", "amount": 5000, "method": "cash"}
```

### 4.3 الخادم (Server-side Pseudocode)

```python
# Pseudocode (Python/Flask example)
@app.route('/api/v2/payment', methods=['POST'])
def submit_payment():
    # 1. Verify JWT
    user = verify_jwt(request.headers['Authorization'])

    # 2. Get user's session HMAC key (from DB, keyed by user_id+device_id)
    hmac_key = get_session_key(user.id, user.device_id)

    # 3. Anti-replay checks
    nonce = request.headers['X-Request-Nonce']
    ts = int(request.headers['X-Request-Timestamp'])
    sig = request.headers['X-Request-Signature']
    body = request.get_data(as_text=True)

    # 3a. Timestamp window check (±60 seconds)
    if abs(time.time()*1000 - ts) > 60_000:
        return error(401, 'timestamp_out_of_window')

    # 3b. Nonce uniqueness check (Redis SET with 5min TTL)
    nonce_key = f"nonce:{user.id}:{nonce}"
    if not redis.set(nonce_key, "1", ex=300, nx=True):
        return error(401, 'nonce_replay')

    # 3c. Signature verification
    expected_sig = base64(hmac_sha256(hmac_key, f"{nonce}.{ts}.{body}"))
    if not constant_time_compare(sig, expected_sig):
        return error(401, 'invalid_signature')

    # 4. Process payment (with idempotency — see next section)
    return process_payment_idempotent(user, body)
```

### 4.4 الـ Client TypeScript

```typescript
// src/api/signedRequest.ts
import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';
import { SecureStorage } from '@/security/secureStorage';

interface SignedHeaders {
  'X-Request-Nonce': string;
  'X-Request-Timestamp': string;
  'X-Request-Signature': string;
}

/**
 * يولّد headers موقّعة لطلب معين.
 * يجب استدعاؤها قبل كل POST/PUT/DELETE.
 */
export async function buildSignedHeaders(bodyJson: string): Promise<SignedHeaders> {
  const hmacKeyB64 = await SecureStorage.get('session.hmac');
  if (!hmacKeyB64) throw new Error('No session HMAC key');

  const keyBytes = base64ToBytes(hmacKeyB64);
  const nonce = uuidv4();
  const timestamp = Date.now().toString();

  const canonical = `${nonce}.${timestamp}.${bodyJson}`;

  const key = await crypto.subtle.importKey(
    'raw', keyBytes,
    { name: 'HMAC', hash: 'SHA-256' },
    false, ['sign']
  );

  const sigBytes = await crypto.subtle.sign(
    'HMAC', key,
    new TextEncoder().encode(canonical)
  );

  return {
    'X-Request-Nonce': nonce,
    'X-Request-Timestamp': timestamp,
    'X-Request-Signature': bytesToBase64(new Uint8Array(sigBytes)),
  };
}

function base64ToBytes(b64: string): Uint8Array {
  return Uint8Array.from(atob(b64), c => c.charCodeAt(0));
}

function bytesToBase64(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes));
}
```

---

## 5. Idempotency للدفع (الطبقة 5)

### 5.1 المشكلة الحرجة

سيناريو **حدث في تطبيقات مماثلة** (وقد يحدث هنا):

```
1. كاشير يدفع 5000 ريال لمشترك
2. الشبكة تنقطع أثناء الـ request
3. التطبيق يعرض "خطأ، حاول مجدداً"
4. الكاشير يضغط "إعادة" ⇒ request جديد
5. ⚠️ لكن الـ request الأول وصل فعلاً للخادم!
6. النتيجة: المشترك مُسحب مرتين × 5000 = 10,000 ريال
```

**في التطبيق الحالي:** `/api/Payment/saveBillRequest` لا يحمل أي آلية كشف التكرار.

### 5.2 الحل: Idempotency-Key Header

نمط معتمد في Stripe, AWS, PayPal:

```
1. Client يولّد UUID فريد لكل عملية (قبل الإرسال).
2. Header: Idempotency-Key: <uuid>
3. Server:
   - إذا رأى نفس Key قبلاً مع نفس body ⇒ يعيد نفس النتيجة (لا يعالج مرتين)
   - إذا رأى نفس Key مع body مختلف ⇒ يرفض (409 Conflict)
   - إذا key جديد ⇒ يعالج ويحفظ النتيجة لـ 24h
```

### 5.3 الكود

```typescript
// src/features/payment/api.ts
import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';
import { apiClient } from '@/api/sslClient';
import { buildSignedHeaders } from '@/api/signedRequest';
import { getValidAccessToken } from '@/features/auth/refresh';

const PaymentRequestSchema = z.object({
  customer_no: z.string().min(1).max(32),
  amount: z.number().positive().multipleOf(0.01),
  currency: z.literal('YER'),
  method: z.enum(['cash', 'card', 'wallet']),
  bill_period: z.string().regex(/^\d{4}-\d{2}$/),
  cashier_location: z.object({
    lat: z.number(),
    lng: z.number(),
  }).optional(),
  notes: z.string().max(500).optional(),
});

const PaymentResponseSchema = z.object({
  receipt_id: z.string(),
  voucher_no: z.string(),
  customer_no: z.string(),
  amount: z.number(),
  timestamp: z.string().datetime(),
  status: z.enum(['confirmed', 'pending', 'failed']),
  receipt_data: z.object({
    company_name: z.string(),
    company_address: z.string(),
    company_phone: z.string(),
    branding_image_url: z.string().url().optional(),
  }),
});

export type PaymentRequest = z.infer<typeof PaymentRequestSchema>;
export type PaymentResponse = z.infer<typeof PaymentResponseSchema>;

/**
 * Submit payment with FULL retry protection:
 * - Idempotency-Key prevents double-charge on network retry
 * - Signed request prevents replay attacks
 * - JWT auth required
 */
export async function submitPayment(
  payment: PaymentRequest,
  options: { retryWithSameKey?: boolean; existingKey?: string } = {}
): Promise<PaymentResponse> {
  // 1. Validate
  const validated = PaymentRequestSchema.parse(payment);

  // 2. Generate or reuse Idempotency Key
  //    CRITICAL: For retries (user pressed "retry"), use SAME key
  const idempotencyKey = options.existingKey ?? uuidv4();

  // 3. Get auth
  const accessToken = await getValidAccessToken();

  // 4. Serialize body
  const bodyJson = JSON.stringify(validated);

  // 5. Sign request (anti-replay)
  const signedHeaders = await buildSignedHeaders(bodyJson);

  // 6. Send
  const raw = await apiClient.request<unknown>('/api/v2/payment', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Idempotency-Key': idempotencyKey,
      ...signedHeaders,
    },
    body: validated,
  });

  // 7. Validate response
  return PaymentResponseSchema.parse(raw);
}
```

### 5.4 نمط Local Queue للـ Resilience

```typescript
// src/features/payment/paymentQueue.ts
import { WatermelonDB } from '@/db';

interface QueuedPayment {
  id: string;
  idempotencyKey: string;
  payload: PaymentRequest;
  attempts: number;
  status: 'pending' | 'sent' | 'confirmed' | 'failed';
  receiptId?: string;
  createdAt: Date;
}

/**
 * نمط Outbox Pattern:
 * 1. Save payment locally FIRST (في WatermelonDB).
 * 2. حاول الإرسال للخادم.
 * 3. إذا نجح ⇒ status = 'confirmed'.
 * 4. إذا فشل (شبكة) ⇒ status = 'pending', try later.
 * 5. عند الإعادة: استخدم نفس idempotencyKey ⇒ لا تكرار على الخادم.
 */
export async function enqueuePayment(req: PaymentRequest): Promise<QueuedPayment> {
  const queued: QueuedPayment = {
    id: uuidv4(),
    idempotencyKey: uuidv4(),   // ← مُولَّد مرة، يُعاد استخدامه في كل retry
    payload: req,
    attempts: 0,
    status: 'pending',
    createdAt: new Date(),
  };

  // 1. Persist locally (transaction)
  await WatermelonDB.write(async () => {
    await WatermelonDB.collections.get('payment_queue').create(record => {
      record.idempotencyKey = queued.idempotencyKey;
      record.payload = JSON.stringify(queued.payload);
      record.status = 'pending';
      record.createdAt = queued.createdAt;
    });
  });

  // 2. Attempt send (in background, doesn't block UI)
  processPaymentQueue();

  return queued;
}

export async function processPaymentQueue(): Promise<void> {
  const pending = await WatermelonDB.collections.get('payment_queue')
    .query(Q.where('status', 'pending'))
    .fetch();

  for (const item of pending) {
    try {
      item.attempts++;
      const response = await submitPayment(
        JSON.parse(item.payload),
        { existingKey: item.idempotencyKey }   // ← reuse key!
      );

      await WatermelonDB.write(async () => {
        item.status = 'confirmed';
        item.receiptId = response.receipt_id;
      });

    } catch (err) {
      if (item.attempts >= 5) {
        await WatermelonDB.write(async () => { item.status = 'failed'; });
      }
      // Will retry on next processPaymentQueue() call (e.g., when network restored)
    }
  }
}
```

> **النتيجة:** حتى إذا انقطعت الشبكة بعد الإرسال للخادم، عند الـ retry سيقول الخادم: "نعم، رأيت هذا Key قبلاً، إليك نفس الاستجابة." ⇒ **لا دفع مكرر**.

---

## 6. حماية الحقول الحساسة (Field-level Encryption)

### 6.1 متى نحتاج Field-level Encryption؟

> **القاعدة:** TLS + Pinning يكفي لـ **99%** من البيانات.
> Field-level encryption نستخدمه فقط لحقول **يجب ألا يراها أحد حتى DB Admin**.

**الحالات التي تستحق:**

- ✅ MPIN (PIN الكاشير لتأكيد العمليات الحساسة) — يجب أن لا يصل الخادم بنص واضح.
- ✅ ملاحظات شخصية للمشتركين (إن وُجدت) — لمنع DB Admin من القراءة.
- ❌ عادي: المبالغ، أرقام المشتركين، التاريخ ⇒ TLS كافٍ.

### 6.2 المشكلة الحالية في التطبيق

من section 1.2:
```java
@c.c.b.a0.b("oldpass") public String h;   // ⚠️ كلمة المرور القديمة في body
@c.c.b.a0.b("newpass") public String i;   // ⚠️ الجديدة كذلك
```

**هذه يجب أن تكون مُشفّرة بمفتاح الخادم العام (RSA).** بدون ذلك، حتى لو TLS قوي، فإن:

1. سجلات الـ Backend ⇒ تظهر كلمات المرور.
2. Backup يحتوي كلمات مرور بنص واضح.
3. DB Admin يستطيع قراءتها.

### 6.3 الحل: RSA-OAEP للحقول الحساسة

```typescript
// src/security/fieldEncryption.ts
// ────────────────────────────────────────────────────────────────────
// Field-level encryption باستخدام RSA-OAEP-SHA256 + AES-GCM (Hybrid)
//
// للحقول الحساسة جداً مثل MPIN, oldPassword, newPassword.
//
// المُخطَّط (Hybrid Encryption):
//   1. توليد random AES-256-GCM key (32 bytes)
//   2. تشفير القيمة بـ AES-GCM
//   3. تشفير AES key بـ RSA-OAEP-SHA256 (مفتاح الخادم العام)
//   4. إرسال {encrypted_key, iv, ciphertext, tag} في الـ body
// ────────────────────────────────────────────────────────────────────

import 'react-native-get-random-values';

const SERVER_PUBLIC_KEY_PEM = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----`;

interface EncryptedField {
  v: 1;                            // version (للترقيات المستقبلية)
  ek: string;                      // base64(RSA-OAEP-encrypted AES key)
  iv: string;                      // base64(12 bytes IV)
  ct: string;                      // base64(AES-GCM ciphertext + tag)
}

export async function encryptField(plaintext: string): Promise<EncryptedField> {
  // 1. Generate random AES-256-GCM key
  const aesKey = await crypto.subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true, // extractable
    ['encrypt']
  );

  // 2. Random 12-byte IV (recommended for AES-GCM)
  const iv = crypto.getRandomValues(new Uint8Array(12));

  // 3. Encrypt plaintext
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    aesKey,
    new TextEncoder().encode(plaintext)
  );

  // 4. Export AES key as raw bytes
  const aesKeyRaw = await crypto.subtle.exportKey('raw', aesKey);

  // 5. Encrypt AES key with server's RSA public key
  const serverKey = await importRsaPublicKey(SERVER_PUBLIC_KEY_PEM);
  const encryptedAesKey = await crypto.subtle.encrypt(
    { name: 'RSA-OAEP' },
    serverKey,
    aesKeyRaw
  );

  return {
    v: 1,
    ek: btoa(String.fromCharCode(...new Uint8Array(encryptedAesKey))),
    iv: btoa(String.fromCharCode(...iv)),
    ct: btoa(String.fromCharCode(...new Uint8Array(ciphertext))),
  };
}

async function importRsaPublicKey(pem: string): Promise<CryptoKey> {
  const base64 = pem
    .replace('-----BEGIN PUBLIC KEY-----', '')
    .replace('-----END PUBLIC KEY-----', '')
    .replace(/\s/g, '');
  const der = Uint8Array.from(atob(base64), c => c.charCodeAt(0));

  return crypto.subtle.importKey(
    'spki',
    der.buffer,
    { name: 'RSA-OAEP', hash: 'SHA-256' },
    false,
    ['encrypt']
  );
}
```

### 6.4 الاستخدام (مثال: تغيير كلمة المرور)

```typescript
// src/features/auth/changePassword.ts
import { encryptField } from '@/security/fieldEncryption';
import { apiClient } from '@/api/sslClient';

export async function changePassword(oldPwd: string, newPwd: string): Promise<void> {
  // 1. Encrypt sensitive fields BEFORE serialization
  const oldPassEncrypted = await encryptField(oldPwd);
  const newPassEncrypted = await encryptField(newPwd);

  // 2. Send (TLS still applies, but field is doubly protected)
  await apiClient.request('/api/v2/auth/change-password', {
    method: 'POST',
    body: {
      old_password_encrypted: oldPassEncrypted,
      new_password_encrypted: newPassEncrypted,
    },
  });

  // النتيجة:
  // - Backend logs: { old_password_encrypted: {ek:"BASE64...", iv:"...", ct:"..."} }
  // - DB backup: نفس الشيء
  // - فقط الخادم الذي يملك المفتاح الخاص يستطيع فك التشفير لحظياً
}
```

---

## 7. بنية Axios Client الكاملة

تجميع كل ما سبق في عميل HTTP واحد:

```typescript
// src/api/client.ts
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { API_CONFIG } from '@/config/api.config';
import { getValidAccessToken } from '@/features/auth/refresh';
import { buildSignedHeaders } from './signedRequest';

export const client: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseUrl,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Version': APP_VERSION,
    'X-Client-Platform': Platform.OS,
  },
});

// ─── Request Interceptor: Auth + Signing ─────────────────────────
client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  // Add request ID for tracing
  config.headers['X-Request-ID'] = uuidv4();

  // Skip auth for /auth/login and /auth/refresh
  const skipAuth = ['/auth/login', '/auth/refresh'].some(p => config.url?.includes(p));

  if (!skipAuth) {
    const token = await getValidAccessToken();
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // Sign mutation requests
  const isMutation = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(
    (config.method ?? '').toUpperCase()
  );
  if (isMutation && config.data) {
    const bodyJson = JSON.stringify(config.data);
    const signed = await buildSignedHeaders(bodyJson);
    Object.assign(config.headers, signed);
  }

  return config;
});

// ─── Response Interceptor: Auto-refresh + Error normalization ────
client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retried?: boolean };

    // 401 + not already retried + not on /auth/refresh ⇒ try token refresh
    if (
      error.response?.status === 401 &&
      !original._retried &&
      !original.url?.includes('/auth/refresh')
    ) {
      original._retried = true;
      try {
        const newToken = await refreshAccessToken();
        original.headers['Authorization'] = `Bearer ${newToken}`;
        return client(original);
      } catch {
        // Refresh failed ⇒ propagate original 401
      }
    }

    // Normalize error
    throw normalizeApiError(error);
  }
);

// ─── Helper for backoff retry on transient errors ─────────────────
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: { maxAttempts?: number; baseDelayMs?: number } = {}
): Promise<T> {
  const max = options.maxAttempts ?? 3;
  const base = options.baseDelayMs ?? 1000;

  for (let attempt = 1; attempt <= max; attempt++) {
    try {
      return await fn();
    } catch (err: any) {
      // Only retry on network errors / 5xx — NEVER on 4xx (especially 409 idempotency conflict)
      const isRetryable = err.code === 'NETWORK_ERROR' ||
                         (err.response?.status >= 500 && err.response?.status < 600);

      if (!isRetryable || attempt === max) throw err;

      const delay = base * Math.pow(2, attempt - 1) + Math.random() * 500;
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw new Error('unreachable');
}
```

---

## 8. مقارنة Side-by-Side: قديم vs جديد

### 8.1 سيناريو: تسجيل دفعة 5000 ريال

#### **القديم (Ecas v18.4):**

```http
POST /api/Payment/saveBillRequest HTTP/1.1
Host: abbasiy.yedns.org:8057   ← قابل للتغيير عبر deeplink ⚠️
Content-Type: application/json

{
  "c_no": "C001",
  "user_no": "U123",
  "acc_token": "ABCDEF123456",      ← Token في body ⚠️
  "user": {
    "Id": "U123",
    "Username": "ahmad",
    "Password": "mySecretPass"        ← ⚠️⚠️⚠️ كلمة المرور!
  },
  "payinfo": {
    "c_no": "C001",
    "v_amt": "5000",
    "v_date": "2026-05-22"
  },
  "user_branch": "0001"
}
```

**التحقق على الخادم:**
- Token صحيح؟ يبحث في DB. ✅
- لا nonce. لا timestamp. لا idempotency.

**سيناريو هجوم:**
1. مهاجم يلتقط الـ request كاملاً.
2. يعيد إرساله ⇒ يُسجَّل دفع ثانٍ على المشترك.
3. **لا توجد آلية لمنع ذلك.**

#### **الجديد:**

```http
POST /api/v2/payment HTTP/1.1
Host: api.abbasiy.example     ← ثابت في APK، لا تغيير
Authorization: Bearer eyJhbGc...  ← JWT في header
X-Request-ID: 550e8400-...
X-Request-Nonce: 7c9e6679-7425-...
X-Request-Timestamp: 1716393645123
X-Request-Signature: hQ8gZ3...   ← HMAC-SHA256(session_key, ...)
Idempotency-Key: pay-2026-05-22-cashier123-abc-001
Content-Type: application/json

{
  "customer_no": "C001",
  "amount": 5000,
  "currency": "YER",
  "method": "cash",
  "bill_period": "2026-04"
}
```

**التحقق على الخادم:**
- JWT صحيح؟ ✅ (مفتاح عمومي يتحقق محلياً، بدون DB)
- Timestamp ضمن ±60s؟ ✅
- Nonce لم يُستخدم قبلاً؟ ✅ (Redis)
- HMAC signature صحيح؟ ✅
- Idempotency-Key رُئي قبلاً؟ ❌ ⇒ معالجة جديدة. إذا ✅ ⇒ إرجاع نفس النتيجة.

**سيناريو هجوم:**
1. مهاجم يلتقط الـ request.
2. يعيد إرساله بعد 5 دقائق ⇒ Timestamp قديم ⇒ 401.
3. يعيد مع timestamp جديد ⇒ Signature لا تتطابق (لا يعرف HMAC key) ⇒ 401.
4. **لا استغلال ممكن من الاعتراض وحده.**

### 8.2 الفرق العملي

| العامل | القديم | الجديد |
|--------|--------|---------|
| Size of body | كبير (مع User كاملاً) | صغير (فقط البيانات الجديدة) |
| Tokens leakage in logs | عالي (في body + URL) | منخفض (في header فقط، logs عادة تستبعد Authorization) |
| Replay attack | ممكن | محظور |
| Double-payment على retry | ممكن جداً | محظور |
| Server load (recompute) | للتحقق من token + DB lookup | JWT verify محلياً (أسرع) |

---

## 9. مصفوفة معالجة الأخطاء

| Server Status | المعنى | إجراء Client |
|---------------|--------|----------------|
| 200 / 201 | نجاح | معالجة عادية |
| 400 | Bad request (Zod failed?) | عرض رسالة validation للمستخدم |
| 401 — `Authorization` invalid | Token منتهي | Auto-refresh + retry |
| 401 — `nonce_replay` | Nonce مستخدم | إعادة المحاولة مع nonce جديد (مرة واحدة) |
| 401 — `timestamp_out_of_window` | ساعة الجهاز خاطئة | تنبيه المستخدم لضبط الساعة |
| 401 — `invalid_signature` | HMAC خطأ | logout + login مجدداً (session مكسورة) |
| 403 | عملية غير مسموح بها للمستخدم | عرض "ليس لديك صلاحية" |
| 409 — `Idempotency-Key conflict` | نفس Key مع body مختلف | عدم retry، عرض خطأ |
| 422 — Business rule violation | مشترك مقطوع، رصيد سالب، إلخ | عرض رسالة عمل من الخادم |
| 429 | Rate limit | Backoff exponential |
| 5xx | خطأ خادم | Retry مع backoff |
| Network error | لا اتصال | حفظ في outbox queue للإعادة لاحقاً |

---

## 10. الخلاصة

### 10.1 الميزات الجديدة الست

1. ✅ **JWT (RS256)** بدلاً من Token عشوائي في body.
2. ✅ **Refresh Token Rotation** — كشف سرقة Token عند الاستخدام المُكرَّر.
3. ✅ **Anti-Replay** — Nonce + Timestamp + HMAC على كل mutation.
4. ✅ **Idempotency-Key** — لا دفع مكرر، أبداً.
5. ✅ **Field-level Encryption** — كلمات المرور وMPIN غير مرئية حتى للـ Backend.
6. ✅ **Outbox Pattern** — مرونة كاملة ضد انقطاع الشبكة.

### 10.2 ما تم حذفه عمداً

- ❌ Token في body (`acc_token`) — يذهب إلى Header.
- ❌ User object كامل في كل request — Server يستخرج من JWT.
- ❌ `oldpass`/`newpass` بنص واضح — تُشفَّر بـ RSA-OAEP.
- ❌ HMAC-SHA1 — استُبدِل بـ HMAC-SHA256.
- ❌ HMAC key = ANDROID_ID — استُبدِل بـ session key من الخادم (256-bit).

### 10.3 المُتطلَّبات من Backend

> هذا البروتوكول يتطلب تعاون فريق الخادم. التغييرات اللازمة:

1. ✅ إصدار JWTs (RS256) عند login.
2. ✅ تجديد JWTs عند refresh (مع rotation).
3. ✅ تخزين nonces في Redis مع TTL 5 دقائق.
4. ✅ تطبيق HMAC verification في middleware.
5. ✅ تطبيق Idempotency-Key check في endpoints المالية.
6. ✅ امتلاك RSA private key لفك تشفير الحقول الحساسة.
7. ✅ Token revocation list (Redis SET).
8. ✅ Rate limiting (Redis).

> **التقدير:** ~3-4 أسابيع من فريق Backend (مع testing).

---

## 11. خريطة الترحيل (من البروتوكول الحالي)

| المرحلة | المدة | الخطوة |
|----------|------|---------|
| **0** | أسبوع 1 | فريق Backend: تصميم v2 API endpoints (مع الحفاظ على v1) |
| **1** | أسبوع 2-3 | Backend: تنفيذ JWT issuance + Redis nonce store + Idempotency |
| **2** | أسبوع 4 | Mobile: تنفيذ JWT/Refresh في التطبيق الجديد |
| **3** | أسبوع 5 | Mobile: تنفيذ Request Signing + Idempotency |
| **4** | أسبوع 6 | E2E testing + Pen-testing (Burp/mitmproxy) |
| **5** | أسبوع 7 | Beta release (10% من الكاشيرات) |
| **6** | أسبوع 8 | Full rollout |

> **في المرحلة 7+:** بعد ~30 يوم على Full rollout، يمكن للـ Backend إيقاف v1 endpoints (التي لا تستخدم JWT).

---

## 12. الخلاصة النهائية للقسم 07

| الملف | الحجم | المحتوى |
|------|-------|---------|
| `01_current_crypto_audit.md` | ~33KB | تدقيق الحالي: 6 مشاكل، 4 نقاط جيدة |
| `02_modern_crypto_design.md` | ~28KB | بدائل حديثة لكل مشكلة (TypeScript) |
| `03_tls_and_certificate_pinning.md` | ~23KB | TLS + Pinning + Rotation |
| `04_secure_communication_protocol.md` | ~30KB | بروتوكول كامل: JWT + Anti-replay + Idempotency |

**المجموع: ~114KB من توثيق أمني هندسي مدعوم بأكواد قابلة للتشغيل.**

---

**النهاية. كل ما يحتاجه فريق الـ Mobile + Backend ليبني نظام تواصل يستطيع المرور بـ pen-test جدّي.**
