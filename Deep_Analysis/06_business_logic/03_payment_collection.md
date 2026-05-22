# Business Logic — Payment Collection Flow (OP_TYP = 1)

> **File:** `06_business_logic/03_payment_collection.md`
> **Source:** `OprationsActivity.java` (lines 130–273), `e0.java` (lines 35–65), `Payinfo.java`, `models/d.java`, `User.java`
> **Endpoint:** `POST /api/Payment/saveBillRequest`
> **Mode (`OP_TYP`):** `1` (set via `Intent.putExtra("OP_TYP", 1)` from `MainActivity`)

---

## 1. Business Purpose

The **payment collection** flow is the cashier's primary daily task. Cashiers walk door-to-door (or sit at a counter) and:

1. Identify customer (by C_NO entered or scanned).
2. Show outstanding balance.
3. Take cash payment.
4. Save the payment to the backend.
5. Print a receipt on the Bixolon thermal printer.

This is the **revenue-generating** activity of the entire app. Any bug here = lost money.

---

## 2. End-to-End Flow (Happy Path)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ MainActivity                                                             │
│  ┌────────────────────────────────────────────────┐                      │
│  │ User clicks "تحصيل" (Payment Collection)        │                      │
│  └────────────────────────────────────────────────┘                      │
│         │                                                                │
│         ▼  startActivity(intent.putExtra("OP_TYP", 1))                   │
└─────────┼────────────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────────────┐
│ OprationsActivity  (B = OP_TYP = 1)                                      │
│                                                                          │
│  STEP 1: User enters/scans C_NO  → field `t` (et_cust_no)               │
│  STEP 2: User taps Search → U() → X("c_no")                              │
│                                                                          │
│    ┌────────────────────────────────────────────────────────────────┐   │
│    │ X(c_no):                                                       │   │
│    │   POST /api/Payment/GetCustomersData                            │   │
│    │   Body: { c_no, token, device_id, op_typ:"1", c_id:"" }         │   │
│    │   Response → models/b envelope → list of models/a (customers)   │   │
│    └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  STEP 3: Customer found → populate UI:                                   │
│    - field `v` (cust_name)   = a.c_name                                  │
│    - field `u` (balance)     = a.c_bal                                   │
│    - field `U` (last_read)   = a.cst_lastread                            │
│    - W = true (customer locked in)                                       │
│                                                                          │
│  STEP 4: User enters payment amount in field `x` (pay_amount)            │
│  STEP 5: User enters notes (optional) in field `w` (note)                │
│  STEP 6: User taps "Save" → U() validates → V() shows confirmation       │
│                                                                          │
│  STEP 7: Confirmation dialog "هل تريد حفظ العملية؟" → e0.onClick(OK)      │
│                                                                          │
│    ┌────────────────────────────────────────────────────────────────┐   │
│    │ e0 (B==1) builds dVar:                                          │   │
│    │   d.token = User.getToken()                                     │   │
│    │   d.user  = MediaSessionCompat.C(ctx)  ⚠️ then  user.s("")      │   │
│    │   d.payInfo = Payinfo{                                          │   │
│    │      Pay_amount   = (lastRead - currentMeter) ⚠️ see §6        │   │
│    │      C_no         = obj  (customer code)                        │   │
│    │      C_id         = obj3 (internal id from cust search)         │   │
│    │      P_amount     = obj2 (what user typed)                      │   │
│    │      Notes        = obj4                                        │   │
│    │      LocationXY   = ConfigStore.f()  (GPS)                      │   │
│    │   }                                                             │   │
│    │   POST /api/Payment/saveBillRequest                             │   │
│    │   Response → models/b → callback s(ctx)                         │   │
│    └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  STEP 8: On success (s callback): show receipt preview, print, reset UI  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. UI Field Mapping (OprationsActivity)

| Field    | Resource ID (assumed) | Purpose                                | OP_TYP=1 visibility |
|----------|-----------------------|----------------------------------------|---------------------|
| `t`      | `et_cust_no`          | Customer number (C_NO) — user input    | ✅ visible          |
| `v`      | `et_cust_name`        | Customer name (filled by search)       | ✅ visible (readonly?)|
| `u`      | `tv_balance`          | Balance (filled by search)             | ✅ visible          |
| `U`      | `tv_last_read`        | Last meter reading                     | ✅ visible          |
| `V`      | `tv_extra_info`       | Extra info / debt history              | ✅ visible          |
| `x`      | `et_pay_amount`       | Payment amount entered by cashier      | ✅ visible          |
| `w`      | `et_notes`            | Notes                                  | ✅ visible          |
| `t (Button)` (this.t) | btOk            | "Save" button                          | ✅ visible          |
| `z`/`A`  | image holders          | Customer photo / capture area          | ❌ hidden (B=1)     |
| `K`      | `iv_meter`             | Meter image                            | ❌ hidden (B=1)     |

> ⚠️ Note: Field names `t`, `u`, `v`, `w`, `x` are post-obfuscation. Original ids are inferred from `R.id.*` references already in the code (see `04_screens_flow/04_operations_screen.md` for the full table).

---

## 4. Source: `e0.onClick(B==1)` — Payment Save (lines 36–65)

```java
if (this.f2365b.B == 1) {
    OprationsActivity self = this.f2365b;
    EditText editText6 = self.t;                       // et_cust_no
    String obj  = editText6.getText().toString();      // C_NO
    String obj2 = self.x.getText().toString();         // payment amount
    String obj3 = self.O;                              // last meter reading (from search)
    EditText editText7 = self.v;                       // et_cust_name
    String obj4 = editText7.getText().toString();      // ⚠ unused below as cust name
    EditText editText8 = self.w;                       // et_notes
    String obj5 = editText8.getText().toString();      // notes
    
    // Build request envelope
    c.b.a.f.c cVar  = new c.b.a.f.c(self);
    com.egy.webpaymentapp.webapi.models.d dVar = new com.egy.webpaymentapp.webapi.models.d();
    
    dVar.a(MediaSessionCompat.C(self).n());           // d.token = User.token
    User C = MediaSessionCompat.C(self);              // 2nd call to .C → may be cached
    dVar.g = C;                                        // d.user  = User
    C.s("");                                           // ⚠ CRITICAL BUG: clears token on User obj
    
    int parseInt = Integer.parseInt(obj3) - Integer.parseInt(obj2);
    //                       ^ last read       ^ amount entered
    //  ⚠ This is semantically WRONG for payments — see §6
    
    Payinfo p = new Payinfo();
    dVar.f = p;
    p.c(String.valueOf(parseInt));   // ⚠ p.Pay_amount = (lastRead - amount)
    dVar.f.e(obj);                    // p.C_no
    dVar.f.d(obj3);                   // p.C_id    ⚠ MISLABEL: actually obj3 = last meter read?
    dVar.f.h(obj2);                   // p.P_amount
    dVar.f.f(obj5);                   // p.Notes
    dVar.f.g(c.b.a.c.d(self).f());    // p.LocationXY (from SharedPrefs APP_USER_LOC_KEY)
    
    cVar.b(
        "/api/Payment/saveBillRequest",
        dVar,
        com.egy.webpaymentapp.webapi.models.b.class,
        new s(self),                   // success listener
        null                           // no error listener override
    );
}
```

---

## 5. Outbound Request (HTTP)

### 5.1 Endpoint
```
POST {BASE_URL}/api/Payment/saveBillRequest
Content-Type: application/json
Headers: token: <RSA-encrypted-password-of-User-from-login>  ← actually it's User.token
         device_id: <Settings.Secure.ANDROID_ID via MediaSessionCompat.D()>
```

### 5.2 Body (`models/d` envelope)

```jsonc
{
  "device_id":  "<android_id>",
  "token":      "<user_token_from_login>",
  "c_no":       "",                  // not used in save (cleared via dVar.f2458a)
  "c_id":       "",                  // not used in save
  "op_typ":     "1",                 // NOT SET in save flow — k field
                                     // ⚠ but in this code path dVar.k is NOT set, only X() sets it
  "user":       { /* full User object — see User.java */ },
  "payInfo": {
    "C_no":        "<customer-code>",
    "C_id":        "<last-meter-read>",   // ⚠ field misuse — see §6
    "Pay_amount":  "<lastRead - amount>",  // ⚠ semantically wrong, see §6
    "P_amount":    "<amount-entered>",
    "Notes":       "<notes-text>",
    "LocationXY":  "<lat,lon>"
  }
}
```

### 5.3 Response (`models/b` envelope)

```jsonc
{
  "success":   true,
  "message":   "تمت العملية بنجاح",
  "data":      "<receipt-id>",
  "code":      "200",
  "PrintData": "<base64-or-html-of-receipt>",
  "Custs":     null,
  "PayList":   null,
  "ReadingList": null
}
```

The success callback `s(oprationsActivity)` then:
1. Builds the receipt locally (`c.b.a.d.b()` formats the HTML).
2. Loads the receipt into the secondary WebView (`j.java`).
3. Triggers Bluetooth print via `j.c.printRImage`.
4. Calls `OprationsActivity.P(self)` to **clear the UI** for the next customer.

---

## 6. ⚠️ Critical Bugs Found

### 6.1 `Pay_amount = lastRead - amount` (line 55)

```java
int parseInt = Integer.parseInt(obj3) - Integer.parseInt(obj2);
//                       ^ obj3 = self.O = last meter reading
//                       ^ obj2 = self.x = payment amount entered
p.c(String.valueOf(parseInt));   // Payinfo.Pay_amount = parseInt
```

**This is nonsensical for a payment flow.** `last_meter_read - cash_amount` produces an arbitrary integer that has no business meaning. Possibilities:
- **a)** Backend ignores `Pay_amount` for OP_TYP=1 and only uses `P_amount`. Then this is dead code with a confusing name.
- **b)** Backend interprets `Pay_amount` as "remaining balance after payment" → but `last_read` is in kWh, not YER. Type mismatch.
- **c)** Field misnomer from code reuse: same code path was once used for meter readings (where `parseInt` = consumption in kWh).

> 🟠 **Verdict:** Most likely (a) — dead computation. But the field is sent over the wire, so backend logs may contain garbage data. Confirm with server team.

### 6.2 `C_id` field overloaded (line 60)

```java
dVar.f.d(obj3);   // setter d() → C_id = obj3 = last meter reading
```

`Payinfo.C_id` is documented as **internal customer ID** in the model (see `03_data_models/02_payinfo_model.md`). Here it's being set to the **last meter reading number**. Either:
- The server doesn't validate `C_id` for OP_TYP=1, OR
- This is a bug that overwrites the intended ID.

> 🟠 **Action:** Trace `dVar.f.d(...)` in successful payment payloads from network logs to determine actual behavior.

### 6.3 `C.s("")` Token-Clear (line 54)

```java
User C = MediaSessionCompat.C(self);   // returns User from SharedPrefs
dVar.g = C;                             // assign to envelope
C.s("");                                // setter s() → User.Token = ""
```

After this line, the in-memory `User` object has its Token cleared. Since `dVar.g` references the same object (Java is pass-by-reference), the **outbound request now has `user.Token = ""`**.

But `dVar.a(MediaSessionCompat.C(self).n())` on line 51 (= `dVar.token = User.token`) was set **before** the clear, so the **envelope-level `token`** still has the value. Backend may use either:
- The envelope `token` → works fine.
- The `user.Token` field → request will be rejected.

> 🔴 **Critical:** If backend checks `user.Token`, every payment save will fail with auth error. Likely the **envelope `token` is what's checked**, making the clear a no-op for security but a leak risk.
> 
> **Why was this written?** Likely to **prevent the token from being persisted back to disk** when the same `User` object is saved by some other code path. Defensive programming gone wrong.

### 6.4 No Optimistic UI / No Local Persistence

If the network request fails (timeout, server down, no signal), the payment is **lost**. There is no:
- Local SQLite table of "pending payments".
- Retry queue.
- Offline mode.

For door-to-door cashiers in areas with patchy connectivity (Yemen has frequent outages), this is a **major UX flaw**. Cashier collects cash → can't save → has to write on paper → reconciliation nightmare.

> 🔴 **Rebuild requirement:** Use **WatermelonDB** (already in app1's stack) for offline-first payment queue with eventual sync.

---

## 7. Success Callback (`s` class, not yet read but inferred)

Based on the response envelope (`models/b`) and the `WebviewActivity.v()` injection pattern:

```java
class s implements Response.Listener<b> {
    final OprationsActivity ctx;
    s(OprationsActivity ctx) { this.ctx = ctx; }

    @Override
    public void onResponse(b response) {
        if (response.success) {
            // 1. Inject PrintData into secondary WebView for receipt rendering
            ctx.someWebView.loadUrl("javascript:showpayList('" + escape(response.PrintData) + "')");
            // 2. Auto-print after a short delay
            //    (Once the JS finishes rendering, j.c.printRImage(base64) is invoked)
            // 3. Toast success
            Toast.makeText(ctx, response.message, Toast.LENGTH_LONG).show();
            // 4. Reset UI
            OprationsActivity.P(ctx);
        } else {
            Toast.makeText(ctx, response.message, Toast.LENGTH_LONG).show();
        }
    }
}
```

> 📝 Verify by reading `OprationsActivity$s.java` in JADX output (not yet read this session).

---

## 8. Sequence Diagram

```
Cashier       UI(OprationsActivity)   Volley   Server   SharedPrefs   WebView(j)   BixolonPrinter
  │                  │                  │        │           │            │              │
  │ enter C_NO       │                  │        │           │            │              │
  │─────────────────▶│                  │        │           │            │              │
  │ tap Search       │                  │        │           │            │              │
  │─────────────────▶│ U() → X(c_no)    │        │           │            │              │
  │                  │─────────────────▶│        │           │            │              │
  │                  │                  │ POST /GetCustomersData          │              │
  │                  │                  │───────▶│           │            │              │
  │                  │                  │  models/b (with Custs[])        │              │
  │                  │                  │◀───────│           │            │              │
  │                  │ populate v,u,U,V │        │           │            │              │
  │                  │◀─────────────────│        │           │            │              │
  │                  │ W = true         │        │           │            │              │
  │ enter amount     │                  │        │           │            │              │
  │─────────────────▶│                  │        │           │            │              │
  │ enter notes      │                  │        │           │            │              │
  │─────────────────▶│                  │        │           │            │              │
  │ tap Save         │                  │        │           │            │              │
  │─────────────────▶│ U()→V()→Dialog   │        │           │            │              │
  │                  │ "هل تريد حفظ؟"   │        │           │            │              │
  │ tap OK           │                  │        │           │            │              │
  │─────────────────▶│ e0.onClick(-1)   │        │           │            │              │
  │                  │ build dVar       │        │           │            │              │
  │                  │ read User from prefs      │           │            │              │
  │                  │─────────────────────────────────────▶ │            │              │
  │                  │ ⚠ C.s("") clears token in memory      │            │              │
  │                  │ POST /saveBillRequest              │              │              │
  │                  │─────────────────▶│        │           │            │              │
  │                  │                  │───────▶│           │            │              │
  │                  │                  │ models/b success                │              │
  │                  │                  │◀───────│           │            │              │
  │                  │ s.onResponse     │        │           │            │              │
  │                  │ Inject PrintData → showpayList(html)               │              │
  │                  │────────────────────────────────────────────────▶  │              │
  │                  │                  │        │           │            │              │
  │                  │                  │        │           │ render     │              │
  │                  │                  │        │           │            │              │
  │                  │                  │        │           │ printRImage(base64)       │
  │                  │                  │        │           │            │─────────────▶│
  │                  │                  │        │           │            │              │ print
  │                  │ P() reset UI     │        │           │            │              │
  │ next customer    │                  │        │           │            │              │
```

---

## 9. Validation Logic (`U()` method, lines 204–230)

```java
public static boolean U(OprationsActivity self) {
    if (!TextUtils.isEmpty(self.t.getText())) {              // C_NO not empty
        if (TextUtils.isEmpty(self.v.getText()) || !self.W) { // no customer locked
            self.X(self.t.getText().toString());              // → trigger search
        } else {
            if (TextUtils.isEmpty(self.x.getText())) {        // amount empty
                if (self.B != 3) {                            // not Location mode
                    self.x.setError("...");
                    editText = self.x;
                }
            }
            // ⚠ For Payment (B=1), the IF below is OP_TYP=2 specific.
            //     Path falls through to `return true`.
            if (self.B != 2 || ... meter image checks ...) {
                if (self.B == 3 || self.S.m() <= 0) {
                    return true;          // ← Payment with valid amount returns here
                }
                return self.Z().booleanValue();
            }
            Toast.makeText(self, "صورة العداد مطلوبة", ...).show();
        }
        return false;
    }
    Toast.makeText(self, "أدخل رقم المشترك", ...).show();
    editText = self.t;
    editText.requestFocus();
    return false;
}
```

For OP_TYP=1, validation requires:
1. `C_NO` is non-empty.
2. Customer was found (`W = true` AND `v` (name field) populated).
3. Payment amount (`x`) is non-empty.
4. Returns `true` → V() shows confirmation dialog.

> 🟡 **Missing validations:**
> - No numeric check on amount (accepts letters!).
> - No range check (could pay -100 or 999999999).
> - No GPS/location verification.
> - No duplicate-prevention (rapid double-tap could create two payments).

---

## 10. Rebuild Recommendations

| Issue                                | Fix                                                                                                                  |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Confusing `Pay_amount = lastRead - paid` | Remove. Send only `amount` (cleanly named, numeric).                                                                |
| `C_id` carrying meter read           | Use proper distinct fields: `customerId` and `lastMeterReading`.                                                     |
| Token clearing side effect           | Send fresh DTO (TypeScript `interface PaymentRequest`) — never mutate the User object.                               |
| No offline persistence               | WatermelonDB table `pending_payments` with `synced: false` flag. Sync on connectivity.                               |
| No duplicate prevention              | Add idempotency key (UUID generated on Save button press, sent in header `X-Idempotency-Key`).                       |
| No numeric/range validation          | Zod schema: `amount: z.number().int().positive().max(10_000_000)`.                                                   |
| No undo / void                       | Add "void payment" flow (within 5 minutes, before sync).                                                              |
| Cash drawer reconciliation           | End-of-day report: sum of payments vs cash in hand. Already partially implemented via `04_ShareReport` bridge.        |

---

## 11. TypeScript Migration Sketch

```ts
// src/features/payment/types.ts
import { z } from 'zod';

export const PaymentRequestSchema = z.object({
  customerCode:  z.string().min(1),
  customerId:    z.string(),
  amount:        z.number().int().positive().max(10_000_000),  // YER
  notes:         z.string().max(500).optional(),
  locationXY:    z.string().regex(/^-?\d+\.\d+,-?\d+\.\d+$/),  // "lat,lon"
  idempotencyKey: z.string().uuid(),
});

export type PaymentRequest = z.infer<typeof PaymentRequestSchema>;
```

```ts
// src/features/payment/api.ts
import { apiClient } from '@/api/client';
import { PaymentRequest, PaymentRequestSchema } from './types';

export async function savePayment(req: PaymentRequest) {
  PaymentRequestSchema.parse(req);          // throws if invalid
  return apiClient.post('/api/Payment/saveBillRequest', {
    headers: { 'X-Idempotency-Key': req.idempotencyKey },
    json: req,
  });
}
```

```ts
// src/features/payment/store.ts  (WatermelonDB)
import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export class PendingPayment extends Model {
  static table = 'pending_payments';

  @field('customer_code') customerCode!: string;
  @field('customer_id')   customerId!: string;
  @field('amount')        amount!: number;
  @field('notes')         notes?: string;
  @field('location_xy')   locationXY!: string;
  @field('idempotency')   idempotencyKey!: string;
  @field('synced')        synced!: boolean;
  @readonly @date('created_at') createdAt!: Date;
}
```

---

## 12. Cross-References

- 📄 `04_screens_flow/04_operations_screen.md` — Full activity walkthrough.
- 📄 `05_webview_bridge/02_GetPaymentsRequest.md` — Receipt rendering & print.
- 📄 `06_business_logic/04_meter_reading.md` — Sibling flow (OP_TYP=2).
- 📄 `06_business_logic/05_receipt_generation.md` — How receipt HTML is built.
- 📄 `03_data_models/02_payinfo_model.md` — Payinfo field semantics.
- 📄 `02_api_contract/02_payment_endpoints.md` — Endpoint contract.

---

> *End of `06_business_logic/03_payment_collection.md`*
