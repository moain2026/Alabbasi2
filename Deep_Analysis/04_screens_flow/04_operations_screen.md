# OprationsActivity — الشاشة الموحَّدة للعمليات الثلاث

> **المصدر:** `com.egy.webpaymentapp.Screens.OprationsActivity`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/Screens/OprationsActivity.java`
> **عدد الأسطر:** 624 سطر — **أكبر Activity في التطبيق**.
> **الـ Layout:** `R.layout.activity_oprations` (لاحظ الـ typo — `oprations` بدلاً من `operations`).
> **العنوان:** ⚠️ مُتغيِّر — يُعيَّن بناءً على `OP_TYP`.

---

## 1. النموذج الموحَّد: 3 شاشات في Activity واحد

التطبيق يستخدم **شاشة واحدة لثلاث عمليات** عبر متغير `B` (OP_TYP):

| `B` | الإسم | يُمرَّر من | العنوان (Action Bar) |
|-----|------|------------|----------------------|
| `1` | Payment (دفعة) | `MainActivity.q` (btnpayment) | `R.string.text_payments` |
| `2` | Reading (قراءة عداد) | `MainActivity.u` (btn_add_reading) | `R.string.text_meter_reading` |
| `3` | Location (موقع زبون) | `MainActivity.v` (btn_cust_loc) | `R.string.text_customer_location` |

### مصدر القيمة
```java
this.B = getIntent().getExtras().getInt("OP_TYP");   // line 435
```

---

## 2. مكوّنات الواجهة الكاملة

### 2.1 الحقول

| المتغير | View ID | النوع | OP_TYP=1 | OP_TYP=2 | OP_TYP=3 |
|---------|---------|-------|----------|----------|----------|
| `t` | `te_cust_no` | EditText | رقم الزبون | رقم الزبون | رقم الزبون |
| `v` | `te_cust_name` | EditText | إسم الزبون (auto-fill) | إسم الزبون | إسم الزبون |
| `u` | `te_cust_address` | EditText | العنوان (auto-fill) | العنوان | العنوان |
| `w` | `te_cst_note` | EditText | ملاحظة | ملاحظة | ⚠️ مخفي |
| `x` | `te_amt` | EditText | المبلغ (أرقام بلا فاصلة) | القراءة (أرقام مع فاصلة عشرية) | الإحداثيات (نص) |
| `U` | `txt_cust_bal` | TextView | "الرصيد: X ريال" | "القراءة السابقة: X" | — |
| `V` | `txt_note` | TextView | ملاحظات إضافية | — | — |

### 2.2 الأزرار

| المتغير | View ID | الوظيفة | OP_TYP=1 | OP_TYP=2 | OP_TYP=3 |
|---------|---------|---------|----------|----------|----------|
| `y` | `btn_save` | حفظ العملية | ✅ | ✅ | ✅ |
| `z` | `btn_cust_print_inv` | طباعة فاتورة سابقة | ✅ | ❌ | ❌ |
| `A` | `btn_call_cust` | اتصال بالزبون | ✅ | ✅ | ❌ |
| `Q` | `bnt_add_img` | إلتقاط صورة العدّاد | ❌ | ✅ (شرطي) | ❌ |
| `G` | `btn_print` | طباعة الإيصال الحالي | ✅ | ✅ | ❌ |
| `F` | `btn_share` | مشاركة PDF | ✅ | ✅ | ❌ |
| `H` | `btn_new` | عملية جديدة (تفريغ) | ✅ | ✅ | ✅ |

### 2.3 التخطيطات (Layouts)
| المتغير | View ID | الوظيفة |
|---------|---------|---------|
| `C` | `lyout_input_data` | حاوية مدخلات قبل الحفظ |
| `D` | `lyout_op_stat` | حاوية ظاهرة بعد الحفظ (للطباعة) |
| `L` | `tak_image_ly` | حاوية إلتقاط الصورة (مخفية لـ OP_TYP=1,3) |
| `K` | `img_view_meter_image` | عرض الصورة المُلتقَطة |
| `E` | `text_op_id` | عرض رقم الإيصال بعد الحفظ |

---

## 3. تخصيص الـ UI حسب `OP_TYP` (السطور 464-513)

```java
int i = this.B;
if (i == 1) {  // Payment
  this.I.T(getString(R.string.txt_payed_amt));   // "المبلغ المدفوع"
  this.L.setVisibility(8);                        // إخفاء حاوية الصورة
  editText = this.x;
  digitsKeyListener = new DigitsKeyListener(false, false);  // أرقام صحيحة فقط
} else {
  if (i != 2) {
    if (i == 3) {  // Location
      this.I.T(getString(R.string.text_customer_location));
      this.L.setVisibility(8);
      this.J.setVisibility(8);     // إخفاء ملاحظة
      this.x.setInputType(1);       // نص عادي
      editText = this.x;
      digitsKeyListener = null;
    }
    // … باقي الإعدادات المشتركة
  }
  // Reading (OP_TYP=2)
  this.I.T(getString(R.string.txt_metter_reading));
  if (TextUtils.isEmpty(S.c()) || !S.c().equals("1")) {  // !Cshr_AddWebMtrImg
    this.L.setVisibility(8);  // إخفاء الصورة إن لم يكن مسموحاً
  } else {
    this.L.setVisibility(0);
  }
  editText = this.x;
  digitsKeyListener = new DigitsKeyListener(false, true);  // ⚠️ يسمح بفاصلة عشرية
}
editText.setKeyListener(digitsKeyListener);
```

⚠️ **عيب في الـ JADX:** الأسطر 480-487 تتكرر مرتين بسبب decompilation غير دقيق (لاحظ `Removed duplicated region for block`). الفهم الصحيح: الـ click listeners تُربط مرة واحدة فقط بعد الـ switch.

---

## 4. الدوال الجوهرية

### 4.1 `X(String)` — البحث عن زبون (السطور 263-274)

```java
private void X(String custNo) {
  d req = new d();
  req.f2461d = MediaSessionCompat.C(this).f();  // user_no
  req.a(MediaSessionCompat.C(this).n());        // user_branch
  req.f2458a = custNo;                          // c_no
  req.k = "" + this.B;                          // op_typ
  req.f2460c = "";                              // area_no (فارغ)
  
  c.b.a.f.c cVar = new c.b.a.f.c(this);
  cVar.b("/api/Payment/GetCustomersData", req, b.class, new b(), null);
}
```

⇒ POST إلى `GetCustomersData` ⇒ في الإستجابة يُستدعى `O()` (السطور 157-172):

### 4.2 `O()` — تعبئة UI من نتائج البحث (السطور 157-172)

```java
public static void O(OprationsActivity self, b response) {
  Iterator<a> it = response.c().iterator();   // customersList
  if (it.hasNext()) {
    a next = it.next();
    c.b.a.a.c cVar = new c.b.a.a.c();
    cVar.f1828a = next.c();  // c_name → label
    cVar.f1829b = next.d();  // c_no → value (للعرض)
    cVar.f1831d = next.a();  // c_bal
    cVar.g = next.e();        // cst_address
    cVar.h = next.f();        // cst_lastread
    self.a0(cVar);            // تعبئة الـ UI
  }
}
```

⚠️ **مفاجأة:** `f1828a` يحمل **الإسم** و `f1829b` يحمل **الرقم** — عكس المتوقع! ثم في `a0()`:

```java
private void a0(c.b.a.a.c cVar) {
  this.t.setText(cVar.f1829b);  // ⚠️ te_cust_no يأخذ "الرقم" (صحيح)
  this.v.setText(cVar.f1828a);  // ⚠️ te_cust_name يأخذ "الإسم" (صحيح)
  this.u.setText(cVar.g);        // العنوان
  this.W = true;                  // علم "تم العثور على الزبون"
}
```

⇒ النموذج `c.b.a.a.c` يُستخدم بطريقتين متضاربتين عبر الكلاسات ⇒ مصدر تشويش يجب توحيده.

### 4.3 `U()` — التحقق قبل الحفظ (السطور 204-230) ⚠️ منطق معقد

```java
public static boolean U(OprationsActivity self) {
  if (TextUtils.isEmpty(self.t.getText())) {
    Toast: "txt_cust_no"
    self.t.requestFocus();
    return false;
  }
  
  if (TextUtils.isEmpty(self.v.getText()) || !self.W) {
    self.X(self.t.getText());   // إعادة بحث
  } else {
    if (TextUtils.isEmpty(self.x.getText())) {  // المبلغ/القراءة فارغ
      if (self.B != 3) {        // ليس Location
        self.x.setError(...);
        return false;
      }
    }
    
    // ⚠️ هذا الشرط مُلتوي — تحليل دقيق:
    if (self.B != 2 || isEmpty(S.c()) || !S.c().equals("1") ||
        !isEmpty(self.M)  || isEmpty(S.i()) || !S.i().equals("1") ||
        !isEmpty(self.M)) {
      
      if (self.B == 3 || S.m() <= 0) {
        return true;   // ✅ مقبول
      }
      return self.Z().booleanValue();   // فحص GPS
    }
    
    Toast: "txt_mter_img_must"  // الصورة مطلوبة
  }
  return false;
}
```

⚠️ **التحليل الدقيق للشرط الكبير:**
- `B != 2` ⇒ ليس قراءة ⇒ تجاوز فحص الصورة
- `S.c() != "1"` ⇒ Cshr_AddWebMtrImg غير مفعَّل ⇒ تجاوز
- `!isEmpty(M)` ⇒ الصورة موجودة فعلاً (`M` = Base64) ⇒ تجاوز
- `S.i() != "1"` ⇒ read_must_take_img غير مفعَّل ⇒ تجاوز
- ⇒ **رسالة "الصورة مطلوبة" تظهر فقط عند:** `B==2 && Cshr_AddWebMtrImg=="1" && imageEmpty && read_must_take_img=="1" && imageEmpty`
- المتغير `!isEmpty(M)` يظهر مرتين متطابقتين ⇒ **bug تكرار في الشرط**.

⇒ تأكيد للملاحظة السابقة في `02_api_contract/04_readings_endpoints.md`: **يحتاج تحقق Production**.

### 4.4 `V()` — بناء رسالة التأكيد (السطور 233-260)

```java
public static void V(OprationsActivity self) {
  String str = "";
  if (self.B == 1) {
    StringBuilder sb = new StringBuilder();
    sb.append("الزبون: ");
    if (self.s != null) {  // c.b.a.a.c من البحث
      sb.append(self.s.f1829b).append("\n");
      sb.append(self.s.f1828a);
    } else {
      sb.append(self.t.getText());
    }
    sb.append(" \nالمبلغ المدفوع: ");
    sb.append(self.x.getText());
    sb.append(" ريال");
    sb.append("\n\n");
    sb.append(self.V.getText());
    str = sb.toString();
  }
  // OP_TYP=2 و 3 ⇒ str فارغ في رسالة التأكيد!
  
  c.b.a.d.d(str + "\nتأكيد العملية", self, new e0(self));
  //      ↑ يفتح AlertDialog (نعم/لا) → e0.onClick يُنفِّذ الحفظ
}
```

⚠️ **عيب UX:** لـ OP_TYP=2 و 3 لا يعرض المستخدم تأكيد محتوى ⇒ يمكن أن يحفظ بالخطأ.

### 4.5 `Z()` — فحص جاهزية GPS (السطور 351-367)

```java
public Boolean Z() {
  c.b.a.b.d gpsService = this.T;
  if (gpsService == null || !gpsService.a()) {
    // GPS غير مفعَّل
    return S.m() > 0 ? FALSE : TRUE;
    //          ↑ Ues_Gps - إذا مفعَّل في الإعدادات ⇒ يجب أن يكون متاحاً
  }
  
  if (isEmpty(getPref(APP_USER_LOC_KEY))) {
    // GPS مفعَّل لكن لم يلتقط موقعاً بعد
    new CountDownTimer(S.h(), 1000, progressDialog).start();
    return FALSE;
  }
  
  if (B == 3) {
    self.x.setText(getPref(APP_USER_LOC_KEY));
  }
  return TRUE;
}
```

⇒ يُجبر المستخدم على الإنتظار حتى يأتي fix GPS قبل الحفظ.

### 4.6 `y()` — التقاط صورة العدّاد (السطور 308-349)

```java
public static void y(OprationsActivity self, String filename, int requestCode) {
  String format = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
  String fileName = "CUSTMETER-1-" + User.Id + "-" + custNo + "-" + format + ".png";
  
  File dir = new File(EXTERNAL_PICTURES, "WEBPAYMENT");
  if (!dir.exists()) dir.mkdirs();
  
  File outFile = new File(dir, fileName);
  self.R = outFile.getAbsolutePath();
  
  // SDK 24+: FileProvider لتجنب FileUriExposedException
  if (Build.VERSION.SDK_INT >= 24) {
    FileProvider.b(self, "com.egy.webpaymentapp", outFile);
  }
  
  // DroidCameraXP API
  a.b builder = new a.b();
  builder.n(true);    // showFlash
  builder.t(1);       // facing (1 = back camera)
  builder.p("WEBPAYMENT");  // folder
  builder.s(fileName.replace(".png", ""));  // file name
  builder.q("png");
  builder.o(70);      // quality
  builder.r(S.g() > 0 ? S.g() : 300);  // width = imgWdth (default 300)
  c.d.a.a camera = builder.m(self);
  self.r = camera;
  try {
    camera.c();   // افتح الكاميرا
  } catch (Exception e) {
    e.printStackTrace();
  }
}
```

### 4.7 `onActivityResult()` — معالجة الصورة (السطور 369-419)

```java
public void onActivityResult(int requestCode, int resultCode, Intent data) {
  super.onActivityResult(...);
  
  if (requestCode != c.d.a.a.o) {  // ليس طلب كاميرا
    if (requestCode == 299) {       // إعدادات الطابعة
      c.b.a.c.e(this);
      return;
    }
    if (this.q != null) q.g(requestCode, resultCode);  // BixlonPrinterManger
    return;
  }
  
  // طلب كاميرا
  if (r.a() == null) {
    Toast: "Picture not taken!";
    return;
  }
  
  String path = this.R;
  int targetWidth = S.g();
  
  try {
    Bitmap bmp = BitmapFactory.decodeFile(path);
    int w = bmp.getWidth();
    int h = bmp.getHeight();
    if (targetWidth <= 0) targetWidth = 300;
    
    ByteArrayOutputStream bos = new ByteArrayOutputStream();
    if (w > targetWidth) {
      Bitmap.createScaledBitmap(bmp, targetWidth, h / (w / targetWidth), false)
            .compress(Bitmap.CompressFormat.PNG, 70, bos);
    }
    
    Bitmap scaled = BitmapFactory.decodeStream(new ByteArrayInputStream(bos.toByteArray()));
    File f = new File(path);
    if (f.exists()) f.delete();
    scaled.compress(Bitmap.CompressFormat.PNG, 80, new FileOutputStream(new File(path)));
    bos.flush(); bos.close();
  } catch (Exception e) {
    e.printStackTrace();
  }
  
  Bitmap finalBmp = BitmapFactory.decodeFile(this.R);
  ByteArrayOutputStream bos2 = new ByteArrayOutputStream();
  finalBmp.compress(Bitmap.CompressFormat.PNG, 100, bos2);
  
  this.K.setImageBitmap(finalBmp);
  this.K.setVisibility(0);
  this.M = Base64.encodeToString(bos2.toByteArray(), 0);  // ← يُحفظ كـ Base64
}
```

⚠️ **عيوب الكود:**
1. `Bitmap.createScaledBitmap()` يرجع Bitmap **جديد** لكن لا يُحفظ مرجع له ⇒ مُحتمل OOM.
2. الحساب `h / (w / targetWidth)` يستخدم قسمة `int` ⇒ خسارة دقة الإرتفاع.
3. مفتاح `c.d.a.a.o` (طلب الكاميرا) قد يساوي قيمة `299` (إعدادات الطابعة) ⇒ تصادم محتمل.
4. تتم compress إلى PNG ثم compress مرة أخرى ⇒ ضياع وقت.

### 4.8 `E()` — حفظ القراءة (السطور 130-154)

```java
public static void E(self, c_no, c_name, c_note, BRD_ImgName, BRD_ImgData, gpsLoc) {
  c cVar = new c.b.a.f.c(self);
  d req = new d();
  req.a(MediaSessionCompat.C(self).n());  // user_branch
  
  User C = MediaSessionCompat.C(self);
  req.g = C;
  C.s("");  // ⚠️ يمسح Token من نسخة User المرسلة!
  req.f2461d = req.g.f();  // user_no
  
  Payinfo p = new Payinfo();
  req.f = p;
  p.e(c_no);
  p.d(c_name);
  p.f(c_note);
  p.b(BRD_ImgName);
  req.k = "" + self.B;  // op_typ
  
  if (!isEmpty(S.j()) && S.j().equals("1")) {  // read_save_img_online
    p.i(BRD_ImgData);  // يضيف Base64 فقط إذا مسموح
  }
  
  p.h(currentReadingValue);  // v_amt = ⚠️ مرسل كـ str3 ⇒ يجب التحقق
  p.g(getPref(APP_USER_LOC_KEY));  // user_gps_loc
  
  cVar.b("/api/Payment/saveReadingRequest", req, b.class, new t(self), null);
}
```

⚠️ **سؤال:** ما الذي يحدث للـ Token عند `C.s("")`؟
- `C` هو نفس الكائن المعاد من `MediaSessionCompat.C(self)` (cached؟ أم نسخة منفصلة؟).
- لو cached ⇒ كل الإستدعاءات اللاحقة تفشل بسبب فقدان الـ Token.
- يحتاج تحقق ⇒ يبدو bug خطير.

---

## 5. القوائم (Menu)

### 5.1 `onCreateOptionsMenu()` (السطور 538-553)

```java
inflate(R.menu.connect_printer_menu, menu);

if (B == 1 || B == 2) {
  if (B == 1) menu.findItem(action_connect).setVisible(true);   // اتصال طابعة
  else        menu.findItem(action_connect).setVisible(false);  // ⚠️ Reading لا اتصال طابعة!
  menu.findItem(printer_seting).setVisible(true);
} else {
  // OP_TYP=3
  menu.findItem(action_connect).setVisible(false);
  menu.findItem(printer_seting).setVisible(false);
}
```

⚠️ **عيب:** القراءة (OP_TYP=2) لا يمكن طباعتها كإيصال (`action_connect` مخفي) ⇒ متعارض مع منطق `G` (btn_print) المرئي عند الحفظ.

### 5.2 `onOptionsItemSelected()` (السطور 583-597)

| Item ID | الإجراء |
|---------|---------|
| `action_connect` | `q.l(new v(this))` ⇒ يفتح حوار اختيار طابعة Bluetooth |
| `add_cust` | `new d(this, B!=1, B).k(new o(this))` ⇒ إضافة زبون جديد |
| `printer_seting` | `startActivityForResult(Setting_Printer_Activity, 299)` |

---

## 6. حلقة الحياة (Lifecycle)

### 6.1 `onCreate` (السطور 429-535)
- تهيئة الـ Views
- قراءة `OP_TYP`
- ربط Listeners
- استدعاء `Y()` ⇒ بدء GPS service إذا `Ues_Gps > 0`

### 6.2 `onStart` (السطور 601-606)
- إذا الطابعة موجودة ⇒ `q.h()` (إعادة الإتصال)

### 6.3 `onStop` (السطور 610-617)
- إذا الطابعة موجودة ⇒ `q.i()` (قطع الإتصال)

### 6.4 `onDestroy` (السطور 557-580)
- إيقاف GPS Service
- إيقاف Printer Manager
- إيقاف PDF Builder

### 6.5 `u()` (السطور 619-623)
- زر Home (Action Bar) ⇒ `finish()` بدون تأكيد.

---

## 7. ASCII لتدفُّق العملية الكاملة (OP_TYP=1)

```text
MainActivity btnpayment.click
        ↓
Intent.putExtra("OP_TYP", 1)
        ↓
OprationsActivity.onCreate
        ↓ setContentView(activity_oprations)
        ↓ B = 1
        ↓ Render UI for Payment mode:
        ↓   - hide L (image layout)
        ↓   - DigitsKeyListener(int only)
        ↓   - title = "إضافة دفعة"
        ↓ Y() ⇒ start GPS if needed
        ↓
المستخدم يُدخل c_no في t (te_cust_no)
        ↓
المستخدم يضغط زر بحث (أو IME Action)
        ↓
X(c_no) ⇒ POST /api/Payment/GetCustomersData
        ↓
b.callback ⇒ O(self, response)
        ↓
a0(item) ⇒ تعبئة t, v, u, U + W=true + z visible
        ↓
المستخدم يُدخل v_amt في x (te_amt)
        ↓
المستخدم يضغط y (btn_save)
        ↓
a0(this).onClick ⇒ U(self) فحص ⇒ V(self)
        ↓
V(self) ⇒ AlertDialog تأكيد
        ↓
e0.onClick(yes):
   if B==1: POST /api/Payment/saveBillRequest
   if B==2: E(...) ⇒ POST /api/Payment/saveReadingRequest
   if B==3: POST /api/Payment/saveCustLocation
        ↓
في الإستجابة الناجحة:
   - عرض رقم الإيصال في E (text_op_id)
   - إخفاء C (lyout_input_data)
   - إظهار D (lyout_op_stat)
   - إظهار G (btn_print) + F (btn_share) + H (btn_new)
   - الطباعة عبر Bixolon q.printReceipt(payinfo)
```

---

## 8. خلاصة العيوب الحرجة

| # | العيب | الموقع | الشدة |
|---|------|--------|------|
| 1 | شرط فحص الصورة معقد ومُحتمل خطأ | `U()` السطر 216 | 🔴 |
| 2 | `C.s("")` يمسح Token من Cached object | `E()` السطر 139 | 🔴 |
| 3 | لا تأكيد لـ OP_TYP=2 و 3 (str فارغ) | `V()` السطر 256 | 🟡 |
| 4 | عدم cleanup في compress Bitmap | `onActivityResult` 399-407 | 🟡 |
| 5 | تخصيص قسمة عدد صحيح لإرتفاع الصورة | السطر 399 | 🟢 |
| 6 | `getIntent().getExtras().getInt("OP_TYP")` بدون null check | السطر 435 | 🔴 |
| 7 | لا يوجد debounce على Save button | عام | 🟡 |
| 8 | `_pdftools` و `MediaSession` ينظَّفان في `onDestroy` لكن قد تكون static refs | السطر 563-579 | 🟡 |
| 9 | الـ JADX warnings (`Code decompiled incorrectly`) | عدة مواضع | 🟢 (مشكلة في الفهم) |
| 10 | لا offline support — كل عملية تتطلب اتصال | عام | 🟡 |

---

> **يربط هذا الملف بـ:**
> - `02_api_contract/03_payments_endpoints.md` (Endpoints).
> - `03_data_models/02_payinfo_model.md` (Payinfo).
> - `06_business_logic/03_payment_collection.md` و `04_meter_reading.md`.
> - `10_rebuild_blueprint/02_recommended_architecture.md` (إعادة التصميم).
