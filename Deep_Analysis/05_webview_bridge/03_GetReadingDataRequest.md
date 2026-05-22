# `mobile.GetReadingDataRequest(String)` — جلب قائمة القراءات

> **التوقيع:** `@JavascriptInterface public void GetReadingDataRequest(String str)`
> **الموقع:** `web/i.java` السطر 25-28
> **المُستدعَى من:** `readinglist.html` / `readinglist.js`

---

## 1. الكود

```java
@JavascriptInterface
public void GetReadingDataRequest(String str) {
  WebviewActivity.w(str, this.f2415a);
}
```

⇒ يفوِّض إلى `WebviewActivity.w(String, Activity)` — نظير `v()` لكن للقراءات.

---

## 2. المُعامِل `String str`

JSON مماثل لـ GetPaymentsRequest:
```json
{
  "c_no": "12345",
  "findVal": "",
  "area_no": "A001",
  "fromDate": "2024-01-01",
  "toDate": "2024-12-31"
}
```

---

## 3. `WebviewActivity.w()` (مُعاد بناؤه)

```java
public static void w(String json, Activity activity) {
  User user = MediaSessionCompat.C(activity);
  
  d req = new Gson().fromJson(json, d.class);
  req.f2461d = user.f();
  req.f2462e = user.l();
  req.a(user.n());
  req.k = "2";   // ⚠️ op_typ = Reading (الفرق الوحيد عن v())
  
  c.b.a.f.c client = new c.b.a.f.c(activity);
  client.b(
    "/api/Payment/GetReadingListData",   // ⚠️ endpoint مختلف
    req,
    b.class,
    response -> {
      String json2 = new Gson().toJson(response.f());
      WebviewActivity.u.loadUrl(
        "javascript:showpayList('" + json2 + "');"  // ⚠️ نفس function!
      );
    },
    null
  );
}
```

⚠️ **مفاجأة:** الإستجابة تستدعي `showpayList()` (وليس `showReadingList()` كما كنا نتوقع) — لأن الـ JS في `readinglist.html` يستخدم **نفس الإسم** كأن الـ Frontend يتعامل معها كنوع موحَّد.

---

## 4. الإختلاف عن `GetPaymentsRequest`

| البُعد | GetPaymentsRequest | GetReadingDataRequest |
|------|-------------------|----------------------|
| Endpoint | `/api/Payment/GetPaymentsReportData` | `/api/Payment/GetReadingListData` |
| `op_typ` | `"1"` | `"2"` |
| نموذج الإستجابة | `List<c>` (12 حقل) | `List<c>` (نفس النموذج) |
| الـ JS function | `showpayList()` | `showpayList()` ⚠️ (نفس الإسم) |
| HTML page | `paymentList.html` | `readinglist.html` |

---

## 5. ملاحظة على إستخدام نفس النموذج

نظراً لأن استجابتي Endpoints الـ Reading و Payment تشتركان في:
- نفس النموذج (`models/c`).
- نفس JS function لعرض البيانات.

⇒ التطبيق يعامل القراءات كأنها "إيصالات قراءة" مع `v_amt` يحمل قيمة الإستهلاك بدلاً من المبلغ المدفوع.

**هذا يؤكّد الفرضية في `03_data_models/05_reading_record.md`** — Backend واحد يخدِم النوعين بمخطط جدول موحَّد.

---

## 6. التدفُّق

```text
[JS in readinglist.html]
   window.mobile.GetReadingDataRequest(JSON.stringify(filters));
         ↓
[Native: i.java]
   GetReadingDataRequest(String str) {
     WebviewActivity.w(str, activity);
   }
         ↓
[Native: WebviewActivity.w static]
   d req = parse(str);
   req.k = "2";
   POST /api/Payment/GetReadingListData
         ↓
[Response: List<c>]
         ↓
[Native: callback]
   webview.loadUrl("javascript:showpayList('" + json + "');");
         ↓
[JS: same showpayList function]
   JSON.parse + render
```

---

## 7. المخاطر

نفس مخاطر `GetPaymentsRequest`:
- حقن JS عبر loadUrl.
- لا validation للـ JSON المُدخَل.
- لا rate-limiting.

**إضافي:** الـ JS لا يفرّق بين Reading و Payment ⇒ قد يحدث خلط بصري للمستخدم.

---

## 8. التوصيات للإعادة

- ✅ **فصل النموذجين:** `Payment` و `Reading` كنماذج مختلفة في الـ Native + الـ JS.
- ✅ **JS functions منفصلة:** `showPaymentList()` و `showReadingList()`.
- ✅ **اعتمد على API typed** بدلاً من JSON غير منضبط.

```ts
// React Native
case 'GetReadings': {
  const filters = readingFiltersSchema.parse(payload);
  const records: Reading[] = await api.readings.list(filters);
  const json = JSON.stringify(records).replace(/[\\'"]/g, '\\$&');
  webView.injectJavaScript(`showReadingList(${json}); true;`);
  break;
}
```

---

> **يربط هذا الملف بـ:**
> - `02_api_contract/04_readings_endpoints.md` (GetReadingListData).
> - `03_data_models/05_reading_record.md` (نموذج البيانات).
> - `09_assets_resources/02_javascript_files.md` (readinglist.js).
