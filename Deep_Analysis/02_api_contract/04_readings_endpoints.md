# 02.4 — Endpoints القراءات (Readings)

> **ملاحظة:** قراءات العدّاد فعلياً تستخدم نفس الـ endpoints الموجودة في [`03_payments_endpoints.md`](03_payments_endpoints.md):
> - الكتابة: `POST /api/Payment/saveReadingRequest`
> - القراءة: `POST /api/Payment/GetReadingListData`
>
> هذا الملف يُكرّر التفاصيل بتركيز على سيناريو القراءة، ويُضيف فوارق دقيقة عن سيناريو الدفع.

---

## السيناريو الكامل لقراءة عدّاد

```
1. المستخدم يفتح OprationsActivity مع OP_TYP=2
2. يدخل رقم المشترك (c_no)
3. يضغط زر البحث (أو يبتعد عن الحقل):
        POST /api/Payment/GetCustomersData {c_no, op_typ:"2", ...}
        ↓
        Response: {customersList:[{c_no, c_name, cst_lastread:"8742", cst_address}]}
        ↓
        UI يعرض "آخر قراءة: 8742"
   
4. المستخدم يدخل القراءة الحالية (مثلاً 9123)
   - شرط: يجب أن تكون > آخر قراءة (validation client-side)
   - شرط: إن user.read_must_take_img == "1" → يجب تصوير العداد
   
5. المستخدم يلتقط صورة العداد (إن مطلوبة):
   - DroidCameraXP يفتح كاميرا مخصصة
   - يُحفظ الملف في /storage/emulated/0/Pictures/WEBPAYMENT/
   - يضغط الصورة لـ width = user.imgWdth (default 300px)
   - يحوّل إلى Base64
   
6. المستخدم يضغط حفظ:
   - حوار تأكيد
   - عند Yes:
        if (user.read_save_img_online == "1") {
            // أرسل الصورة Base64 مع الـ payload
            BRD_ImgData = base64;
        } else {
            // اكتفِ بالاسم فقط (الصورة محفوظة محلياً)
            BRD_ImgData = null;
        }
        POST /api/Payment/saveReadingRequest
        ↓
        Response: {payinfo:{v_no, v_date}}
        ↓
        ينتقل لـ vReport.html لعرض السند
```

---

## فوارق سيناريو القراءة عن الدفع

| النقطة | الدفع (OP_TYP=1) | القراءة (OP_TYP=2) |
|---|---|---|
| الحقل المعروض بعد البحث | "الرصيد: X ريال" | "آخر قراءة: Y" |
| المُدخَل من المستخدم | المبلغ (DigitsKeyListener no decimal) | القراءة (DigitsKeyListener with decimal!) |
| التحقق من المُدخَل | `< رصيد` | `> آخر قراءة` (لا يُتحقق في الكود الحالي!) |
| الصورة | غير مطلوبة | مطلوبة إن `read_must_take_img == "1"` |
| Endpoint الحفظ | `saveBillRequest` | `saveReadingRequest` |
| `payinfo.v_amt` | مبلغ | قراءة |
| `payinfo.c_bal` | الرصيد الجديد بعد الدفع | غير مستخدم |
| الطباعة التلقائية | نعم (Bluetooth Bixolon) | لا (لكن يمكن من vReport.html) |
| قائمة العرض في WebView | `paymentList.html` | `readinglist.html` |
| الـ JS Bridge | `GetPaymentsRequest()` | `GetReadingDataRequest()` |

---

## ⚠️ Bug مُكتشف في الكود الحالي

في `OprationsActivity.java` (السطر 217-220):
```java
if (oprationsActivity.B != 2 || ... || TextUtils.isEmpty(oprationsActivity.M)) {
    if (oprationsActivity.B == 3 || oprationsActivity.S.m() <= 0) {
        return true;   // ← يسمح بحفظ القراءة بدون التحقق إن الصورة مطلوبة
    }
    return oprationsActivity.Z().booleanValue();
}
Toast.makeText(... "txt_mter_img_must" ...);
```

المنطق مكتوب بطريقة سيئة وقد يسمح في بعض الحالات بحفظ القراءة بدون صورة حتى مع `read_must_take_img == "1"`. **يجب اختبار هذا قبل الـ rebuild.**

---

## القيم الخاصة بالقراءات في User Model

| حقل User | معناه |
|---|---|
| `Cshr_AddWebRead` | "1" = مسموح للمستخدم بإضافة قراءات |
| `Cshr_AddWebMtrImg` | "1" = صورة العدّاد مفعّلة في الواجهة (مجرّد عرض الزر) |
| `read_must_take_img` | "1" = الصورة مطلوبة (إجبارية، لا حفظ بدونها) |
| `read_save_img_online` | "1" = أرسل الصورة Base64 للسيرفر، "0" = احفظ محلياً فقط |
| `imgWdth` | عرض الصورة المُضغوطة (default 300px) |

---

## المسار في المعمارية

```
OprationsActivity (B=2)
       │
       ▼
   E() static method
       │
       ▼
   ApiRequestEnvelope.payinfo = Payinfo {
     c_no, c_name, v_amt (= reading),
     c_note, BRD_ImgName, BRD_ImgData (optional)
   }
       │
       ▼
   c.b.a.f.c.b("/api/Payment/saveReadingRequest", ...)
       │
       ▼
   Volley POST with Bearer auth
       │
       ▼
   Server response → callback t(this)
       │
       ▼
   عرض رقم السند + إمكانية طباعة/مشاركة
```

---

**التالي:** [`05_error_codes.md`](05_error_codes.md) — رموز الأخطاء المُحتملة.
