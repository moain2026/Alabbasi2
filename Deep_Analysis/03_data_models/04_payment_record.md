# Payment Record — نموذج سجل الدفعة المُعروض في الـ WebView

> **المصدر:** `com.egy.webpaymentapp.webapi.models.c` (إسم مبهم — كان `PaymentRecord` قبل ProGuard).
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/webapi/models/c.java`
> **عدد الحقول:** 12 حقل.
> **الإستخدام:** عنصر واحد ضمن `List<c>` المُسماة `payList` في الإستجابة. كل سجل يمثّل **إيصال دفعة سابقة** مُعروضاً في صفحة `paymentList.html` و `vReport.html`.

---

## 1. خريطة الحقول (12 حقل)

| # | إسم في JSON | متغير Java | النوع | الوصف |
|---|------------|------------|-------|--------|
| 1 | `c_no` | `f2453a` | `String` | رقم الزبون |
| 2 | `c_name` | `f2454b` | `String` | إسم الزبون |
| 3 | `c_bal` | `f2455c` | `String` | الرصيد عند وقت الدفعة |
| 4 | `v_amt` | `f2456d` | `String` | المبلغ المدفوع |
| 5 | `v_date` | `f2457e` | `String` | تاريخ الإيصال |
| 6 | `v_no` | `f` | `String` | رقم الإيصال (PK) |
| 7 | `user_name` | `g` | `String` | إسم المحصِّل وقت الإيصال |
| 8 | `user_no` | `h` | `String` | رقم المحصِّل |
| 9 | `comp_name` | `i` | `String` | إسم الشركة |
| 10 | `comp_add` | `j` | `String` | عنوان الشركة |
| 11 | `comp_tel` | `k` | `String` | هاتف الشركة |
| 12 | `brD_ImgName` | `l` | `String` | إسم ملف صورة العداد (لاحظ الـ `b` صغيرة) |

---

## 2. ⚠️ اختلاف خطير: حساسية حالة الأحرف

في `Payinfo.java` الحقل يُسمَّى **`BRD_ImgName`** (كل الأحرف الثلاثة الأولى Capital).

في `models/c.java` (هذا الملف) الحقل يُسمَّى **`brD_ImgName`** (أول حرفين lowercase والثالث capital).

```java
// Payinfo.java line 47
@c.c.b.a0.b("BRD_ImgName")
private String m;

// models/c.java line 44
@c.c.b.a0.b("brD_ImgName")  // ⚠️ مختلف!
private String l;
```

### الأثر:
- لو حاول مطوّر الـ Backend أو Frontend الرجوع للحقل بنفس الإسم في كلا الـ Endpoints ⇒ **سيفشل في أحدهما**.
- في `saveBillRequest` تُرسل صورة العداد بإسم `BRD_ImgName`.
- في `GetPaymentsReportData` تُستقبل بإسم `brD_ImgName`.
- **هذا يدل على أن الـ Backend مكتوب يدوياً (وليس Auto-mapping)** + احتمال أن المطوّر استخدم منطقَين مختلفَين.
- **في الإعادة:** يجب توحيد الإسم إلى `meterImageFileName` في DTO الجديد، مع طبقة تحويل من/إلى أسماء الخادم القديمة.

---

## 3. ما الحقل المفقود؟

مقارنة بـ `Payinfo`:

| الحقل في Payinfo | هل في `c.java`؟ | ملاحظة |
|------------------|----------------|--------|
| `c_no` | ✅ | |
| `c_name` | ✅ | |
| `c_bal` | ✅ | |
| `v_amt` | ✅ | |
| `c_note` | ❌ **مفقود** | الملاحظة لا تُرجَع في قائمة التقارير |
| `v_date` | ✅ | |
| `v_no` | ✅ | |
| `user_name` | ✅ | |
| `user_no` | ✅ | |
| `comp_name` | ✅ | |
| `comp_add` | ✅ | |
| `comp_tel` | ✅ | |
| `BRD_ImgName` | ✅ (مختلف الإسم) | |
| `BRD_ImgData` | ❌ **مفقود** | البيانات لا تُرجَع في القائمة — توفير bandwidth |
| `user_gps_loc` | ❌ **مفقود** | الإحداثيات لا تُرجَع في التقرير |

### تفسير الفروق
- **`c_note` غير موجود:** الـ Backend لا يُرجع ملاحظات المحصِّل في قائمة التقارير ⇒ خصوصية / تقليل الحجم.
- **`BRD_ImgData` غير موجود:** صور Base64 ثقيلة جداً ⇒ تُرجَع بإسم الملف فقط ⇒ Frontend يطلبها لاحقاً بـ Endpoint مخصّص.
- **`user_gps_loc` غير موجود:** الإحداثيات تُحفظ لأغراض رقابية فقط ⇒ لا تُعرض للمحصِّل.

---

## 4. ⚠️ أيضاً: الكلاس بدون Getters

```java
// models/c.java كاملاً (12 حقل)
public class c {
  @c.c.b.a0.b("c_no")
  private String f2453a;
  // ... 11 حقل آخر، كلها private
  // ❌ لا يوجد أي getter!
}
```

### الإشكال
- الحقول `private` بلا getters ⇒ **مستحيل قراءتها من خارج الكلاس** بالطرق العادية.
- إذن كيف تُستخدم؟ — **عبر Gson فقط** (يستخدم Reflection للقراءة ⇒ يتجاوز `private`).
- ⇒ هذا يعني أن `payList` بعد deserialization يُحوَّل **مباشرة إلى JSON** ويُحقَن في WebView دون قراءة الحقول في Java.

### كيف يحدث ذلك في `WebviewActivity.v()`:

```java
// تقريباً (بعد فك التعمية)
private void v() {
  // POST /api/Payment/GetPaymentsReportData
  c.b.a.f.c.h(this, params, response -> {
    String json = new Gson().toJson(response.f());  // f() ⇒ payList
    webview.loadUrl("javascript:showpayList('" + json + "');");
  });
}
```

⇒ Gson يحوّل `List<c>` إلى JSON ⇒ يُحقن في WebView ⇒ JavaScript يَستخدم أسماء الحقول الأصلية (`c_no`, `c_name`, …).

---

## 5. النموذج الفعلي في الـ WebView (JavaScript)

في `paymentList.js` (المُفكَّك من تشفير `_$_fNNN`):

```js
function showpayList(jsonStr) {
  var list = JSON.parse(jsonStr);
  // كل عنصر: {c_no, c_name, c_bal, v_amt, v_date, v_no, user_name, user_no, comp_name, comp_add, comp_tel, brD_ImgName}
  for (var i = 0; i < list.length; i++) {
    var rec = list[i];
    // عرض في الجدول
    html += '<tr>';
    html += '<td>' + rec.v_no + '</td>';
    html += '<td>' + rec.c_no + '</td>';
    html += '<td>' + rec.c_name + '</td>';
    html += '<td>' + rec.v_amt + '</td>';
    html += '<td>' + rec.v_date + '</td>';
    html += '</tr>';
  }
}
```

### المخاطر الأمنية في هذا الكود
- **`innerHTML` بدون escape** ⇒ XSS إذا كان `c_name` يحوي `<script>`.
- **JSON تُحقن عبر `loadUrl("javascript:…'" + json + "');")`:** أي `'` في الإسم ⇒ كسر JavaScript ⇒ تنفيذ كود غير مقصود.
- مرجع كامل: `05_webview_bridge/01_bridge_overview.md`.

---

## 6. مقابل TypeScript

```ts
// src/types/api/payment-record.ts
export interface PaymentRecordApi {
  c_no: string;
  c_name: string;
  c_bal: string;
  v_amt: string;
  v_date: string;
  v_no: string;
  user_name: string;
  user_no: string;
  comp_name: string;
  comp_add: string;
  comp_tel: string;
  brD_ImgName: string;       // ⚠️ ملاحظة الإسم
}

// النموذج النظيف الداخلي
export interface PaymentRecord {
  voucher: {
    no: string;
    date: Date;
    amount: Decimal;
  };
  customer: {
    no: string;
    name: string;
    balanceAtTime: Decimal;
  };
  cashier: {
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
    url?: string;       // تُحسب من baseUrl + fileName
  };
}

// Mapper
export const mapPaymentRecord = (dto: PaymentRecordApi): PaymentRecord => ({
  voucher: {
    no: dto.v_no,
    date: new Date(dto.v_date),
    amount: new Decimal(dto.v_amt || '0'),
  },
  customer: {
    no: dto.c_no,
    name: dto.c_name,
    balanceAtTime: new Decimal(dto.c_bal || '0'),
  },
  cashier: { no: dto.user_no, name: dto.user_name },
  company: { name: dto.comp_name, address: dto.comp_add, phone: dto.comp_tel },
  meterImage: dto.brD_ImgName ? {
    fileName: dto.brD_ImgName,
    url: `${API_BASE}/images/${dto.brD_ImgName}`,
  } : undefined,
});
```

---

## 7. مصفوفة Endpoints التي تُرجِع هذا النوع

| Endpoint | الإستخدام |
|----------|----------|
| `POST /api/Payment/GetPaymentsReportData` | قائمة دفعات المستخدم الحالي |
| `POST /api/Payment/saveBillRequest` | الإستجابة بعد الحفظ تحوي **سجلاً واحداً** كـ `payinfo` (وليس `payList`) |

⚠️ لاحظ: استجابة `saveBillRequest` تستخدم `Payinfo` (15 حقل)، بينما `GetPaymentsReportData` تستخدم هذا الكلاس (12 حقل). إختلاف 3 حقول!

---

## 8. توصيات قبل الإعادة

- [ ] توحيد إسم الحقل: `meterImageFileName` فقط.
- [ ] إضافة الحقول المفقودة (`c_note`, `user_gps_loc`) للقائمة إذا كانت مطلوبة للتقارير الإدارية.
- [ ] إضافة `id` رقمي مستقل (PK) بدلاً من الإعتماد على `v_no` كنص.
- [ ] التحقق من timezone في `v_date` — الأرجح UTC لكن قد يكون Asia/Aden.
- [ ] رفع الصور إلى CDN/S3 ⇒ `url` بدلاً من `fileName`.
- [ ] إضافة فلترة من/إلى تاريخ على endpoint للتقارير (حالياً يُرجع كل السجلات).

---

> **يربط هذا الملف بـ:**
> - `02_api_contract/03_payments_endpoints.md` (Endpoint).
> - `04_screens_flow/05_webview_screen.md` (العرض).
> - `09_assets_resources/01_html_pages.md` (`paymentList.html`).
> - `06_business_logic/05_receipt_generation.md` (طباعة الإيصال).
