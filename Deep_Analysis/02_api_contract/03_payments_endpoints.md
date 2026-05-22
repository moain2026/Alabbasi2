# 02.3 — Endpoints المدفوعات (Payment)

> 6 endpoints تحت `/api/Payment/`: البحث، حفظ دفعة، حفظ قراءة، حفظ موقع، قائمة المدفوعات، قائمة القراءات.

---

## 2.3.1 — `POST /api/Payment/GetCustomersData`

**الوظيفة:** البحث عن مشترك برقمه (أو فلترة قائمة)، وإرجاع بياناته (الاسم، الرصيد، آخر قراءة، …).

### الكود المرجعي
```java
// OprationsActivity.X()
private void X(String customerNo) {
    c cVar = new c(this);
    ApiRequestEnvelope dvr = new ApiRequestEnvelope();
    dvr.user_no    = currentUser.getId();
    dvr.user_branch = currentUser.getUserBranch();
    dvr.c_no       = customerNo;
    dvr.op_typ     = String.valueOf(this.B);   // 1, 2, or 3
    dvr.area_no    = "";
    cVar.b("/api/Payment/GetCustomersData", dvr, ApiResponseEnvelope.class, callback, null);
}
```

### Request

```http
POST /payment/api/Payment/GetCustomersData HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json; charset=utf-8

{
  "c_no": "123456",
  "findVal": null,
  "area_no": "",
  "user_no": "123",
  "user_branch": "01",
  "op_typ": "1",
  "user": null,
  "payinfo": null
}
```

### Response

```json
{
  "GEN_API_ERR_NO": 0,
  "customersList": [
    {
      "c_no": "123456",
      "c_name": "محمد عبدالله الأحمدي",
      "c_bal": "12500",
      "br": "01",
      "cst_address": "حي السبعين - شارع 30",
      "c_mobno": "777123456",
      "cst_lastread": "8742"
    }
  ]
}
```

**حقول `customersList[i]`:** (من `webapi/models/a.java`)

| حقل JSON | الوصف | النوع | مستخدم في |
|---|---|---|---|
| `c_no` | رقم المشترك | string | الكل |
| `c_name` | اسم المشترك | string | الكل |
| `c_bal` | الرصيد المتبقي عليه | string (numeric) | OP_TYP=1 |
| `br` | فرع الحساب | string | متابعة |
| `cst_address` | عنوان المشترك | string | الكل |
| `c_mobno` | هاتف المشترك | string | لزر الاتصال 📞 |
| `cst_lastread` | آخر قراءة عداد مسجّلة | string (numeric) | OP_TYP=2 |

### التعامل في التطبيق

```java
// OprationsActivity.O() — يُملأ الحقول
private static void O(OprationsActivity oa, ApiResponseEnvelope r) {
    if (r.customersList.isEmpty()) return;
    Customer first = r.customersList.get(0);
    
    cVar = new c.b.a.a.c();
    cVar.f1828a = first.c_no;
    cVar.f1829b = first.c_name;
    cVar.f1831d = first.c_bal;
    cVar.g      = first.cst_address;
    cVar.h      = first.cst_lastread;
    oa.a0(cVar);                       // يملأ الـ UI
}

// عرض UI:
private void a0(Customer c) {
    teCustNo.setText(c.f1829b);        // الاسم! (label/value swap)
    teCustName.setText(c.f1828a);      // الرقم!
    teCustAddress.setText(c.g);
    if (B == 1) {                       // Payment
        txtCustBal.setText("الرصيد: " + c.f1831d + " ريال");
    } else if (B == 2) {                // Reading
        txtCustBal.setText("آخر قراءة: " + c.h);
    }
    teAmt.requestFocus();
}
```

⚠️ **بُغة الكود الأصلي:** `f1828a` و `f1829b` يبدوان معكوسين (label vs value). هذه عادة سيئة جداً ـ يجب فهمها قبل التعديل.

---

## 2.3.2 — `POST /api/Payment/saveBillRequest`

**الوظيفة:** حفظ دفعة جديدة (OP_TYP=1).

### الكود المرجعي
```java
// Screens/e0.java — onClick(yes) في حوار التأكيد
if (this.f2365b.B == 1) {
    String c_no   = teCustNo.getText().toString();
    String v_amt  = teAmt.getText().toString();
    String c_bal  = O;   // الرصيد قبل
    String c_name = teCustName.getText().toString();
    String c_note = teCstNote.getText().toString();
    
    c cVar = new c(this);
    ApiRequestEnvelope dvr = new ApiRequestEnvelope();
    dvr.user_branch = user.getUserBranch();
    dvr.user = user;
    user.setToken("");                              // يُفرغ الـ Token قبل التضمين
    
    int newBalance = Integer.parseInt(c_bal) - Integer.parseInt(v_amt);  // الرصيد بعد
    
    Payinfo p = new Payinfo();
    dvr.payinfo = p;
    p.setC_bal(String.valueOf(newBalance));         // الرصيد الجديد
    p.setC_no(c_no);
    p.setC_name(c_name);
    p.setV_amt(v_amt);
    p.setC_note(c_note);
    p.setUser_gps_loc(SharedPrefs["APP_USER_LOC_KEY"]);
    
    cVar.b("/api/Payment/saveBillRequest", dvr, ApiResponseEnvelope.class, s(this), null);
}
```

### Request

```http
POST /payment/api/Payment/saveBillRequest HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json; charset=utf-8

{
  "c_no": null,
  "findVal": null,
  "area_no": null,
  "user_no": null,
  "user_branch": "01",
  "user": {
    "Id": "123",
    "Username": "ahmad.cashier",
    "Token": "",
    "user_branch": "01",
    /* …  باقي حقول المستخدم … */
  },
  "payinfo": {
    "c_no": "123456",
    "c_name": "محمد عبدالله الأحمدي",
    "c_bal": "9500",
    "v_amt": "3000",
    "c_note": "دفع جزئي",
    "user_gps_loc": "15.349,44.207",
    "v_date": null,
    "v_no": null,
    "user_name": null,
    "user_no": null,
    "comp_name": null,
    "comp_add": null,
    "comp_tel": null,
    "BRD_ImgName": null,
    "BRD_ImgData": null
  },
  "op_typ": null
}
```

### Response — نجاح

```json
{
  "GEN_API_ERR_NO": 0,
  "payinfo": {
    "c_no": "123456",
    "c_name": "محمد عبدالله الأحمدي",
    "c_bal": "9500",
    "v_amt": "3000",
    "v_no": "EC-2025-00012345",
    "v_date": "2025-11-20 14:32:01",
    "user_name": "أحمد علي - متحصل ميداني",
    "user_no": "123",
    "comp_name": "شركة عبّاس للتحصيل",
    "comp_add": "صنعاء - شارع الزبيري",
    "comp_tel": "+967-1-234567"
  }
}
```

### ما يحدث بعد النجاح

1. التطبيق يحوّل الـ `payinfo` إلى JSON.
2. يخزّن في `localStorage["report"]` (لـ `vReport.html`).
3. ينتقل لـ `vReport.html` لعرض الإيصال.
4. يطبع تلقائياً إن متصل بطابعة.

---

## 2.3.3 — `POST /api/Payment/saveReadingRequest`

**الوظيفة:** حفظ قراءة عدّاد جديدة (OP_TYP=2)، مع صورة العدّاد اختيارياً.

### الكود المرجعي

```java
// OprationsActivity.E() — Called by e0.onClick when B==2
static void E(OprationsActivity oa, String c_no, String c_name, String v_amt,
              String c_note, String imgName, String imgBase64) {
    c cVar = new c(oa);
    ApiRequestEnvelope dvr = new ApiRequestEnvelope();
    dvr.user_branch = user.getUserBranch();
    dvr.user_no     = user.getId();
    dvr.user        = user;
    user.setToken("");
    
    Payinfo p = new Payinfo();
    dvr.payinfo = p;
    p.setC_no(c_no);
    p.setC_name(c_name);
    p.setV_amt(v_amt);                    // المعنى هنا: قيمة القراءة الحالية
    p.setC_note(c_note);
    p.setBRD_ImgName(imgName);            // اسم ملف الصورة (للسيرفر يحفظه)
    
    dvr.op_typ = String.valueOf(oa.B);    // "2"
    
    // فقط إن السيرفر يطلب رفع الصور online:
    if (user.getRead_save_img_online().equals("1")) {
        p.setBRD_ImgData(imgBase64);      // الصورة Base64
    }
    
    p.setUser_gps_loc(SharedPrefs["APP_USER_LOC_KEY"]);
    
    cVar.b("/api/Payment/saveReadingRequest", dvr, ApiResponseEnvelope.class, t(oa), null);
}
```

### Request

```http
POST /payment/api/Payment/saveReadingRequest HTTP/1.1
Authorization: Bearer {token}

{
  "user_no": "123",
  "user_branch": "01",
  "user": { /* ... */ },
  "payinfo": {
    "c_no": "123456",
    "c_name": "محمد عبدالله الأحمدي",
    "v_amt": "9123",
    "c_note": "",
    "user_gps_loc": "15.349,44.207",
    "BRD_ImgName": "CUSTMETER-1-123-123456-20251120_143201.png",
    "BRD_ImgData": "iVBORw0KGgoAAAANSUhEUgAAA...  (Base64 PNG, ~50KB)",
    "c_bal": null,
    "v_amt": "9123",
    /* ... */
  },
  "op_typ": "2"
}
```

**ملاحظات على الـ Payload:**

| الحقل | الملاحظة |
|---|---|
| `v_amt` | هنا يعني "قيمة القراءة الحالية"، ليس مبلغاً مالياً. سوء تسمية. |
| `BRD_ImgName` | تنسيق ثابت: `CUSTMETER-1-{user_id}-{c_no}-{yyyyMMdd_HHmmss}.png` |
| `BRD_ImgData` | Base64 PNG، مضغوطة إلى `imgWdth` من User (default 300px) |
| `user_gps_loc` | بصيغة `lat,lon` (مفصول بفاصلة) |
| `read_must_take_img` | شرط من User: إن `"1"` لا يقبل save بدون صورة |
| `read_save_img_online` | إن `"0"` لا تُرسل `BRD_ImgData` (تُحفظ محلياً فقط) |

### Response

```json
{
  "GEN_API_ERR_NO": 0,
  "payinfo": {
    "v_no": "RD-2025-00056789",
    "v_date": "2025-11-20 14:32:01"
  }
}
```

---

## 2.3.4 — `POST /api/Payment/saveCustLocation`

**الوظيفة:** حفظ إحداثيات GPS فقط (OP_TYP=3) — لتحديث موقع المشترك في DB.

### الكود المرجعي

```java
// Screens/e0.java (B==3)
String c_no    = teCustNo.getText().toString();
String c_name  = teCustName.getText().toString();
String gps     = teAmt.getText().toString();   // هنا حقل المبلغ يحتوي إحداثيات

c cVar = new c(oa);
ApiRequestEnvelope dvr = new ApiRequestEnvelope();
dvr.user_branch = user.getUserBranch();
dvr.user = user;
user.setToken("");

Payinfo p = new Payinfo();
dvr.payinfo = p;
p.setC_no(c_no);
p.setC_name(c_name);
p.setUser_gps_loc(gps);

cVar.b("/api/Payment/saveCustLocation", dvr, ApiResponseEnvelope.class, u(oa), null);
```

### Request

```json
{
  "user_branch": "01",
  "user": { /* … */ },
  "payinfo": {
    "c_no": "123456",
    "c_name": "محمد عبدالله الأحمدي",
    "user_gps_loc": "15.349,44.207"
  }
}
```

### Response

```json
{"GEN_API_ERR_NO": 0, "GEN_API_ERR_MSG": "تم تحديث الموقع"}
```

### ملاحظة UX

في الـ UI، شاشة OperationsActivity تستخدم نفس حقل "المبلغ" (`teAmt`) لإدخال الإحداثيات في وضع OP_TYP=3. هذا تصميم مُربك جداً ـ يجب فصلهما في الـ rebuild.

---

## 2.3.5 — `POST /api/Payment/GetPaymentsReportData`

**الوظيفة:** جلب قائمة المدفوعات للمستخدم (للعرض في `paymentList.html`).

### الكود المرجعي
```java
// WebviewActivity.v()
public static void v(String searchText, Activity activity) {
    c cVar = new c(activity);
    ApiRequestEnvelope dvr = new ApiRequestEnvelope();
    dvr.user        = currentUser;
    dvr.user_branch = currentUser.getUserBranch();
    currentUser.setToken("");
    dvr.findVal     = searchText;
    
    cVar.b("/api/Payment/GetPaymentsReportData", dvr, ApiResponseEnvelope.class,
        response -> {
            String json = new Gson().toJson(response.getPayList());
            webView.loadUrl("javascript:showpayList('" + json + "');");
        }, null);
}
```

### Request

```json
{
  "user": { /* user object */ },
  "user_branch": "01",
  "findVal": "محمد"
}
```

**ملاحظة:** الـ `findVal` يدعم البحث server-side (لكن الـ frontend أيضاً يبحث client-side في القائمة المُحمّلة).

### Response

```json
{
  "GEN_API_ERR_NO": 0,
  "payList": [
    {
      "c_no": "123456",
      "c_name": "محمد عبدالله الأحمدي",
      "c_bal": "9500",
      "v_amt": "3000",
      "v_date": "2025-11-20 14:32",
      "v_no": "EC-2025-00012345",
      "user_name": "أحمد علي",
      "user_no": "123",
      "comp_name": "شركة عبّاس للتحصيل",
      "comp_add": "صنعاء",
      "comp_tel": "+967-1-234567",
      "brD_ImgName": null
    },
    /* … المزيد … */
  ]
}
```

**حقول `payList[i]`:** (من `webapi/models/c.java`)

| الحقل | الوصف |
|---|---|
| `c_no, c_name, c_bal` | معلومات المشترك |
| `v_amt, v_date, v_no` | معلومات السند |
| `user_name, user_no` | المتحصل |
| `comp_name, comp_add, comp_tel` | معلومات الشركة (لرأس الإيصال) |
| `brD_ImgName` | (lowercase b!) اسم صورة العدّاد إن وُجدت |

⚠️ **bug في تسمية:** `brD_ImgName` بحرف `b` صغير، بينما في `Payinfo` تُسمى `BRD_ImgName` بحرف كبير. السيرفر يتعامل مع الحالتين أم تطبيق case-insensitive؟ يجب الاختبار.

---

## 2.3.6 — `POST /api/Payment/GetReadingListData`

**الوظيفة:** جلب قائمة قراءات العدّاد (للعرض في `readinglist.html`).

### الكود المرجعي
```java
// WebviewActivity.w() — مماثل تماماً لـ v()
public static void w(String searchText, Activity activity) {
    ApiRequestEnvelope dvr = ...;
    cVar.b("/api/Payment/GetReadingListData", dvr, ApiResponseEnvelope.class,
        response -> {
            webView.loadUrl("javascript:showReadingList('" + json + "');");
        }, null);
}
```

### Request

```json
{
  "user": { /* … */ },
  "user_branch": "01",
  "findVal": ""
}
```

### Response

```json
{
  "GEN_API_ERR_NO": 0,
  "payList": [
    {
      "c_no": "123456",
      "c_name": "محمد عبدالله الأحمدي",
      "v_amt": "9123",
      "v_date": "2025-11-20 14:32",
      "v_no": "RD-2025-00056789",
      "user_name": "أحمد علي",
      "brD_ImgName": "CUSTMETER-1-123-123456-20251120_143201.png"
    }
  ]
}
```

**ملاحظة:** نفس بنية `payList` لكن `v_amt` هنا = القراءة وليس مبلغاً. النموذج (`c.java`) لا يُفرّق ـ هذا مصدر التباس.

---

## ملخّص العمليات

| العملية | OP_TYP | Endpoint الكتابة | Endpoint القراءة |
|---|---|---|---|
| دفع مبلغ | 1 | `/api/Payment/saveBillRequest` | `/api/Payment/GetPaymentsReportData` |
| قراءة عدّاد | 2 | `/api/Payment/saveReadingRequest` | `/api/Payment/GetReadingListData` |
| تحديث GPS | 3 | `/api/Payment/saveCustLocation` | — (لا قائمة منفصلة) |

والبحث قبل كل عملية يستخدم `/api/Payment/GetCustomersData`.

---

**التالي:** [`05_error_codes.md`](05_error_codes.md) — رموز الأخطاء.
