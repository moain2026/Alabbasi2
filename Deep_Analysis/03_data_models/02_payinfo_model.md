# Payinfo Model — كائن معلومات الدفعة/القراءة

> **المصدر:** `com.egy.webpaymentapp.webapi.models.Payinfo`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/webapi/models/Payinfo.java`
> **عدد الحقول:** 15 حقل (Gson `@SerializedName`).
> **الإستخدام:** يحمل تفاصيل عملية دفعٍ واحدة أو قراءة عدّاد واحدة. يُمرَّر داخل `RequestEnvelope` (`models/d.java`) لكل من `saveBillRequest`, `saveReadingRequest`, `saveCustLocation`.

---

## 1. خريطة الحقول الكاملة (15 حقل)

| # | اسم في JSON | متغير Java | النوع | Setter مبهم | الوصف الكامل |
|---|------------|------------|-------|-------------|--------------|
| 1 | `c_no` | `f2433a` | `String` | `e()` | **رقم الحساب/المشترك** (Customer/Account No). PK في جدول العملاء. |
| 2 | `c_name` | `f2434b` | `String` | `d()` | إسم الزبون كامل (عربي). |
| 3 | `c_bal` | `f2435c` | `String` | `c()` | **رصيد الزبون قبل العملية** (الرصيد التراكمي، YER). |
| 4 | `v_amt` | `f2436d` | `String` | `h()` | **مبلغ العملية الحالية** (الذي يدفعه الزبون أو قيمة الإستهلاك في القراءة). |
| 5 | `c_note` | `f2437e` | `String` | `f()` | ملاحظة المحصِّل (نص حر يدخله الموظف). |
| 6 | `v_date` | `f` | `String` | — | تاريخ الإيصال (يُولَّد من الخادم بعد الحفظ + رد إلى التطبيق للطباعة). |
| 7 | `v_no` | `g` | `String` | — *(getter `a()`)* | **رقم الإيصال/Voucher No** — يُولَّد من الخادم بعد الحفظ. |
| 8 | `user_name` | `h` | `String` | — | إسم المحصِّل (مكرَّر مع `User.Username`). |
| 9 | `user_no` | `i` | `String` | — | رقم المحصِّل (مكرَّر مع `User.Id`). |
| 10 | `comp_name` | `j` | `String` | — | إسم الشركة (يُرسَل من الخادم لطباعة الترويسة). |
| 11 | `comp_add` | `k` | `String` | — | عنوان الشركة. |
| 12 | `comp_tel` | `l` | `String` | — | هاتف الشركة. |
| 13 | `BRD_ImgName` | `m` | `String` | `b()` | **إسم ملف صورة العدّاد** (يُولَّد محلياً عبر `MediaSessionCompat.D() + timestamp + ".jpg"`). |
| 14 | `BRD_ImgData` | `n` | `String` | `i()` | **بيانات الصورة Base64** — يُرسَل فقط عندما `User.read_save_img_online == "1"`. |
| 15 | `user_gps_loc` | `o` | `String` | `g()` | **إحداثيات GPS** بصيغة `"latitude,longitude"` (مثلاً `"15.3694,44.1910"`). |

---

## 2. مصفوفة الإستخدام حسب `OP_TYP` (نوع العملية)

تختلف الحقول المطلوبة بناءً على `OP_TYP` (يُمرَّر من `MainActivity` إلى `OprationsActivity` عبر Intent extra):

| الحقل | OP_TYP=1 (Payment) | OP_TYP=2 (Reading) | OP_TYP=3 (Location) |
|------|---------------------|---------------------|---------------------|
| `c_no` | ✅ مطلوب | ✅ مطلوب | ✅ مطلوب |
| `c_name` | ✅ يُرسل (عرض فقط) | ✅ يُرسل | ✅ يُرسل |
| `c_bal` | ✅ يُرسل (عرض) | ✅ يُرسل | ❌ غير مهم |
| `v_amt` | ✅ **مدخل** من الموظف | ✅ **يُحسب** = (القراءة الحالية − السابقة) × التعريفة | ❌ غير مهم |
| `c_note` | ✅ اختياري | ✅ اختياري | ✅ اختياري |
| `v_date` | ❌ يُولَّد بعد الحفظ | ❌ يُولَّد بعد الحفظ | ❌ غير مهم |
| `v_no` | ❌ يُولَّد بعد الحفظ | ❌ يُولَّد بعد الحفظ | ❌ غير مهم |
| `user_name` | ✅ تلقائي | ✅ تلقائي | ✅ تلقائي |
| `user_no` | ✅ تلقائي | ✅ تلقائي | ✅ تلقائي |
| `comp_name` | ❌ يُملأ بعد الحفظ | ❌ يُملأ بعد الحفظ | ❌ غير مهم |
| `comp_add` | ❌ يُملأ بعد الحفظ | ❌ يُملأ بعد الحفظ | ❌ غير مهم |
| `comp_tel` | ❌ يُملأ بعد الحفظ | ❌ يُملأ بعد الحفظ | ❌ غير مهم |
| `BRD_ImgName` | ❌ غير مستخدم | ✅ مطلوب إذا `read_must_take_img == "1"` | ❌ غير مهم |
| `BRD_ImgData` | ❌ غير مستخدم | ✅ Base64 إذا `read_save_img_online == "1"` | ❌ غير مهم |
| `user_gps_loc` | ✅ إذا `Ues_Gps == 1` | ✅ إذا `Ues_Gps == 1` | ✅ **مطلوب وحصرياً** |

---

## 3. مسار البيانات (Data Flow)

### 3.1 OP_TYP=1 (Payment)

```text
المستخدم يدخل c_no في OprationsActivity
        ↓
زر "بحث" ⇒ X() ⇒ POST /api/Payment/GetCustomersData
        ↓
استجابة: payinfo {c_no, c_name, c_bal} ← من الخادم
        ↓
المستخدم يُدخِل v_amt + c_note + يلتقط GPS اختيارياً
        ↓
زر "حفظ" ⇒ e0.onClick(yes) [B==1] ⇒ POST /api/Payment/saveBillRequest
        ↓
استجابة: payinfo {…+ v_date, v_no, comp_name, comp_add, comp_tel}
        ↓
تُخزَّن في localStorage عبر WebView (vReport.html) للطباعة
```

### 3.2 OP_TYP=2 (Reading)

```text
المستخدم يدخل c_no
        ↓
GetCustomersData (نفسها) ⇒ ترجع cst_lastread (آخر قراءة)
        ↓
المستخدم يُدخِل القراءة الحالية
        ↓
الحساب: v_amt = (currentReading − cst_lastread) × tariff  [في الـ WebView]
        ↓
إذا read_must_take_img=="1" ⇒ التقاط صورة ⇒ BRD_ImgName + BRD_ImgData(Base64)
        ↓
زر "حفظ" ⇒ e0.onClick(yes) [B==2] ⇒ OprationsActivity.E()
        ↓
POST /api/Payment/saveReadingRequest
```

### 3.3 OP_TYP=3 (Location Update)

```text
المستخدم يدخل c_no
        ↓
GetCustomersData
        ↓
الإنتظار لخدمة GPS ⇒ user_gps_loc = "lat,lng"
        ↓
زر "حفظ" ⇒ e0.onClick(yes) [B==3] ⇒ POST /api/Payment/saveCustLocation
```

---

## 4. ملاحظات حرجة

### 4.1 الحقل `BRD_ImgName` غير ثابت الإسم
- يتم توليده من `MediaSessionCompat.D(context) + "_" + System.currentTimeMillis() + ".jpg"` (في `OprationsActivity` حول الأسطر 320–340).
- مثال: `EMUI_1A2B3C4D_1716301234567.jpg`
- **مشكلة:** إذا فقد الجهاز إتصاله ⇒ إعادة المحاولة قد تولّد اسماً جديداً ⇒ ازدواج في الـ DB.

### 4.2 `BRD_ImgData` بحجم كبير
- صورة 300px (default) ⇒ ~30–60 KB ⇒ Base64 ⇒ ~40–80 KB ⇒ Payload طلب POST ضخم.
- **توصية:** رفع الصورة في طلب منفصل (`multipart/form-data`) إلى endpoint مخصص، ثم تخزين الرابط فقط في `BRD_ImgName`.

### 4.3 `c_bal` و `v_amt` كنصوص
- جميع الأرقام المالية محفوظة كـ `String` ⇒ مخاطر:
  - تنسيقات مختلفة (`"100"`, `"100.0"`, `"100,000"`).
  - مقارنة نصية بدلاً من رقمية ⇒ أخطاء UI.
- **في الإعادة:** استخدم `BigDecimal`/`Decimal.js` لكل المبالغ + Validation صارم.

### 4.4 ازدواجية `user_name` و `user_no`
- موجودة في `User` (للمصادقة) وأيضاً في `Payinfo` (لطباعة الفاتورة).
- السبب: تأكيد ربط الإيصال بالموظف حتى لو غُيِّر اسمه لاحقاً.
- **في الإعادة:** اجعل هذا snapshot جزء من جدول `transactions` على الخادم.

### 4.5 الحقل `user_gps_loc` بصيغة `"lat,lng"`
- نص بفاصلة بدلاً من Object ⇒ يجب pars-ه عند العرض في الخريطة.
- **في الإعادة:** `{ lat: number, lng: number }` كنوع منفصل.

---

## 5. مقابل TypeScript

```ts
// src/types/api/payinfo.ts
export interface PayinfoApi {
  c_no: string;
  c_name: string;
  c_bal: string;          // ⚠️ نص — يحتاج تحويل
  v_amt: string;          // ⚠️ نص
  c_note: string;
  v_date: string;         // ⚠️ ISO؟ تحقّق من تنسيق الخادم
  v_no: string;
  user_name: string;
  user_no: string;
  comp_name: string;
  comp_add: string;
  comp_tel: string;
  BRD_ImgName: string;
  BRD_ImgData: string;    // Base64
  user_gps_loc: string;   // "lat,lng"
}

// النموذج النظيف الداخلي
export interface Payinfo {
  customer: {
    no: string;
    name: string;
    balance: Decimal;
  };
  transaction: {
    amount: Decimal;
    note: string;
    date?: string;     // ISO 8601
    voucherNo?: string;
  };
  user: {
    no: string;
    name: string;
  };
  company: {
    name: string;
    address: string;
    phone: string;
  };
  meterImage?: {
    fileName: string;
    base64?: string;    // اختياري — قد يكون رابط بدلاً منه
    url?: string;       // (مُحسَّن بعد التحديث)
  };
  gpsLocation?: {
    latitude: number;
    longitude: number;
  };
}
```

---

## 6. توافقية إعادة الإستخدام (UX)

- في الـ WebView (`paymentList.html`, `readinglist.html`)، تُحوَّل قائمة `Payinfo[]` إلى JSON ⇒ تُحقن عبر `webview.loadUrl("javascript:showpayList('...')")`.
- **مخاطرة:** إذا كان أحد الحقول يحتوي على `'` (apostrophe) في الإسم العربي ⇒ كسر JavaScript.
- مرجع الكسر المحتمل: `WebviewActivity.v()` السطر ~370 — JSON escaping غير كامل.

---

> **يربط هذا الملف بـ:**
> - `02_api_contract/03_payments_endpoints.md` (الإستخدام في الطلبات).
> - `04_screens_flow/04_operations_screen.md` (تدفّق التعبئة).
> - `06_business_logic/03_payment_collection.md` (منطق العمل).
> - `10_rebuild_blueprint/03_data_models_typescript.md` (المقابل الكامل).
