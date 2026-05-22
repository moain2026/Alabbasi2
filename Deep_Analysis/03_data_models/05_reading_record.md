# Reading Record — سجل قراءة العداد

> **الحالة المُفاجِئة:** ⚠️ **لا يوجد كلاس مستقل لـ ReadingRecord في AbbasiyCashiers.**
> القراءات تُعالَج بنفس البنى المستخدمة للدفعات:
> - **عند الإرسال** (`saveReadingRequest`): تُستخدم `Payinfo` (نفس 15 حقل).
> - **عند الإستقبال** (`GetReadingListData`): تُستخدم `List<c>` (`models/c.java`) — **نفس كلاس الدفعات!**

---

## 1. الدليل من الكود

### 1.1 إرسال قراءة جديدة
في `OprationsActivity.E()` (السطر ~480):

```java
// تقريباً
public void E() {
  Payinfo p = new Payinfo();
  p.e(this.E.getText().toString());  // c_no
  p.d(this.F.getText().toString());  // c_name
  p.h(this.G.getText().toString());  // v_amt = استهلاك محسوب
  p.f(this.H.getText().toString());  // c_note = ملاحظة
  p.b(imgFileName);                   // BRD_ImgName
  p.i(imgBase64);                     // BRD_ImgData
  p.g(gpsLocation);                   // user_gps_loc
  
  c.b.a.f.c.l(this, p, user);  // ⇒ POST /api/Payment/saveReadingRequest
}
```

⇒ **نفس كائن `Payinfo`** يُرسَل لكل من saveBillRequest و saveReadingRequest. الفرق فقط في الـ Endpoint.

### 1.2 إستقبال قائمة القراءات
في `WebviewActivity.w()` (السطر ~395):

```java
// POST /api/Payment/GetReadingListData
c.b.a.f.c.j(this, params, response -> {
  String json = new Gson().toJson(response.f());  // ⇒ List<c>
  webview.loadUrl("javascript:showpayList('" + json + "');");
});
```

⇒ نفس `response.f()` (`payList`) → نفس `List<c>` (12 حقل).

---

## 2. لماذا هذا التصميم؟

### 2.1 الأسباب الممكنة
| السبب | التفسير |
|------|---------|
| **توفير وقت التطوير** | المطوّر استخدم نفس الكلاس بدلاً من تكرار البنية. |
| **إعتبار القراءة "دفعة افتراضية"** | في الواقع التجاري، عملية قراءة العدّاد تُولِّد دفعة (فاتورة) ⇒ نفس المخطّط يخدم الإثنين. |
| **عدم اختلاف الـ Backend الفعلي** | الجدول في الـ DB على الأغلب جدول واحد (`transactions`) مع `tx_type` (1=payment, 2=reading). |

### 2.2 المخاطر
- **عدم وضوح النوع:** لا يمكن من قراءة استجابة API تمييز ما إذا كانت دفعة أم قراءة — يجب الإعتماد على الـ Endpoint المُستدعى.
- **هدر الحقول:** بعض الحقول لا معنى لها في القراءة (مثل `v_amt` كمبلغ مدفوع — في القراءة هو "إستهلاك") لكنها مُحمَّلة بنفس الإسم.

---

## 3. الحقول الإضافية الخاصة بالقراءات (تخمين)

ربما الـ Backend يُرجع حقولاً إضافية في `payList` الخاص بـ `GetReadingListData`، لكن لأن الكلاس `c` لا يحوي getters ⇒ يتم تجاهلها بصمت إن وُجدت.

من البنية المتوقّعة لتطبيق قراءات عدّادات، الحقول المنطقية للقراءة:

| الحقل المتوقّع | الإستخدام |
|----------------|-----------|
| `prev_read` | القراءة السابقة (من جدول readings) |
| `curr_read` | القراءة الحالية المُدخَلة |
| `consumption` | الإستهلاك = curr − prev |
| `tariff_rate` | سعر الوحدة (YER/kWh مثلاً) |
| `meter_no` | رقم العدّاد |
| `read_type` | عادي / تقريبي / مغلق |

⇒ كل هذه يبدو أنها **غير مُمَرَّرة** للتطبيق حالياً.

---

## 4. الحقول المُستخدَمة فعلياً في القراءات (داخل Payinfo)

| الحقل | الإستخدام في القراءة |
|------|---------------------|
| `c_no` | رقم الزبون |
| `c_name` | إسم الزبون |
| `c_bal` | الرصيد الحالي (قبل القراءة) |
| `v_amt` | **قيمة الإستهلاك أو القراءة الجديدة** — حسب تنفيذ الـ Backend |
| `c_note` | ملاحظة |
| `BRD_ImgName` | إسم صورة العدّاد |
| `BRD_ImgData` | بيانات الصورة Base64 |
| `user_gps_loc` | الإحداثيات |
| الباقي (`v_date`, `v_no`, …) | يُولَّد بعد الحفظ |

---

## 5. تدفّق إلتقاط صورة العداد

```text
المستخدم يضغط زر "📷 إلتقاط"
         ↓
يتم فحص User.read_must_take_img == "1" ؟
   ✅ نعم ⇒ إلزامي
   ❌ لا ⇒ اختياري
         ↓
فتح كاميرا عبر DroidCameraXP (c.d.a.a)
         ↓
الصورة تأتي كـ Bitmap كبير
         ↓
تُضغط إلى User.imgWdth (default 300px) عبر OprationsActivity.compressBitmap()
         ↓
تُحوَّل إلى Base64 ⇒ BRD_ImgData
         ↓
يُولَّد إسم: BRD_ImgName = D(context) + "_" + ts + ".jpg"
         ↓
عند الحفظ:
   إذا User.read_save_img_online == "1"
       ⇒ تُرسَل ضمن payload الـ JSON
   وإلا
       ⇒ تُحفظ محلياً في /data/data/.../files/ مع رفعها لاحقاً (لكن لا توجد آلية رفع لاحق فعلية في الكود!)
```

⚠️ **عيب حرج:** إذا `read_save_img_online == "0"` ⇒ تُحفظ الصورة محلياً ⇒ **لا توجد آلية رفع لاحق مكتشفة في الكود!** ⇒ الصور تَضيع عند مسح الذاكرة.

---

## 6. مقابل TypeScript للقراءات (مُحسَّن)

```ts
// src/types/api/reading-record.ts

// النموذج النظيف
export interface ReadingRecord {
  voucher: {
    no: string;
    date: Date;
  };
  customer: {
    no: string;
    name: string;
    previousReading?: Decimal;
  };
  reading: {
    currentValue: Decimal;
    consumption: Decimal;        // مُحسَّب
    estimatedAmount: Decimal;    // التعريفة × الإستهلاك
    type: 'normal' | 'estimated' | 'closed';
    meterImage?: {
      fileName: string;
      url: string;
    };
  };
  cashier: { no: string; name: string };
  gpsLocation?: { lat: number; lng: number };
  note?: string;
}

// النموذج المُتوافِق مع الـ Backend الحالي
export interface ReadingRecordLegacyApi {
  c_no: string;
  c_name: string;
  c_bal: string;
  v_amt: string;          // ⚠️ هنا هو القراءة الحالية لا المبلغ
  c_note: string;
  v_date: string;
  v_no: string;
  user_name: string;
  user_no: string;
  comp_name: string;
  comp_add: string;
  comp_tel: string;
  BRD_ImgName: string;    // ⚠️ Capital
  BRD_ImgData?: string;
  user_gps_loc?: string;
}
```

---

## 7. أخطاء محتملة في منطق التحقق

من `OprationsActivity.U()` (السطور 217-220 تقريباً) — منطق التحقق من إجبار الصورة:

```java
// تقريباً (شبه pseudo)
if ("1".equals(user.i())) {  // read_must_take_img == "1"
  if (imgFileName == null || imgFileName.isEmpty()) {
    // ❌ هنا — في النص الفعلي، الفحص قد يكون مع " " (مسافة) بدلاً من ""
    // ⇒ ممكن السماح بحفظ بدون صورة
  }
}
```

⚠️ **هذا التحقق يحتاج تأكيداً** عبر قراءة دقيقة للنص. ⇒ ممكن أن يكون ثغرة تسمح بحفظ قراءة بدون صورة رغم إلزاميتها.

**في الإعادة:** Validation صارم بـ Zod/Yup + double-check في الـ Backend.

---

## 8. توصيات للإعادة

### 8.1 فصل النوعين بوضوح
- `payments` و `readings` ⇒ جدولان مستقلان في الـ DB.
- DTOs منفصلة في الـ API.
- استدعاءات API ذات نوع دقيق:

```ts
api.payments.create(payload: CreatePaymentDto): Promise<Payment>
api.readings.create(payload: CreateReadingDto): Promise<Reading>
api.payments.list(filters: PaymentFilters): Promise<Payment[]>
api.readings.list(filters: ReadingFilters): Promise<Reading[]>
```

### 8.2 معالجة الصور
- Upload في طلب منفصل عبر `multipart/form-data` (وليس Base64).
- نظام **rety mechanism** إذا فشلت — لا تضيع الصورة.
- queue محلي بإستخدام WatermelonDB (كما في تطبيق `app1`).

### 8.3 حساب الإستهلاك على الخادم
- لا تثق بـ `v_amt` المُحسَب من الـ Frontend ⇒ يجب على الـ Backend إعادة الحساب باستخدام:
  - القراءة السابقة من جدول `readings` (آخر سجل بنفس `c_no`).
  - التعريفة من جدول `tariffs` المرتبط بالـ branch/area.

---

## 9. خلاصة

| نقطة | القيمة |
|------|--------|
| كلاس مستقل للقراءة؟ | ❌ لا — يُعاد إستخدام `Payinfo` و `c` |
| عدد الحقول الفعلي عند الإرسال | 15 (نفس Payinfo) |
| عدد الحقول الفعلي عند الإستقبال | 12 (نفس `c`) |
| الإختلاف عن الدفعة | الـ Endpoint فقط + معنى `v_amt` (إستهلاك بدلاً من مبلغ مدفوع) |
| المخاطر الرئيسية | (1) ثغرة التحقق من إجبار الصورة. (2) لا rety لرفع الصور المحلية. (3) لا فلترة تاريخية |

---

> **يربط هذا الملف بـ:**
> - `03_data_models/02_payinfo_model.md` (البنية المُعاد إستخدامها).
> - `03_data_models/04_payment_record.md` (الإستقبال).
> - `02_api_contract/04_readings_endpoints.md` (الـ Endpoint).
> - `06_business_logic/04_meter_reading.md` (المنطق).
> - `04_screens_flow/04_operations_screen.md` (الواجهة).
