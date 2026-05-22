# 04 — Meter Reading Flow (تحليل محايد لقراءة العداد)

> **منهجية:** كل اكتشاف مُوثَّق بـ `file:line` من كود jadx الفعلي. لا فرضيات. التقييم: 🟢 جيد / 🟡 متوسط / 🔴 سيء.

---

## 🎯 ملخص تنفيذي

التطبيق يستخدم **شاشة موحَّدة** (`OprationsActivity`) لثلاث عمليات (دفع، قراءة عدّاد، تحديد موقع) عبر متغير `B` (1=Payment, 2=Reading, 3=Location).

**نقاط رئيسية مُكتشَفة:**
- ✅ يلتقط صورة العدّاد عبر **Intent Camera الخارجي** (لا CameraX)
- ✅ يضغط الصورة إلى PNG-70 ويُرسلها كـ **Base64** ضمن نفس طلب الـ API
- 🔴 **لا يوجد أي تخزين محلي للقراءات** — فشل الشبكة = فقدان البيانات
- 🔴 **لا توجد حدود min/max للقراءة** ولا تحقق من معقوليتها
- 🔴 يستخدم **External Storage عام** (`Environment.DIRECTORY_PICTURES`) للصور (مرئية للمستخدم)
- 🟡 يستخدم نفس DTO (`Payinfo`) للدفع والقراءة (حقل `v_amt` يُعاد استخدامه)

---

## 1. نقطة الدخول وآلية التشغيل

### 1.1 شاشة موحَّدة لثلاث عمليات

📍 **`OprationsActivity.java:430-435`**
```java
public void onCreate(Bundle bundle) {
    ...
    setContentView(R.layout.activity_oprations);
    this.S = MediaSessionCompat.C(this);  // get logged user
    this.B = getIntent().getExtras().getInt("OP_TYP");  // 1/2/3
    ...
}
```

📍 **`OprationsActivity.java:463-512`** — السلوك يتغيَّر حسب `B`:
```java
int i = this.B;
if (i == 1) {                                      // Payment
    this.I.T(getString(R.string.txt_payed_amt));
    this.L.setVisibility(8);                       // إخفاء صورة العدّاد
    digitsKeyListener = new DigitsKeyListener(false, false);  // ⚠️ بدون عشري!
}
// ...
if (i == 2) {                                      // Meter Reading
    this.I.T(getString(R.string.txt_metter_reading));
    if (TextUtils.isEmpty(S.c()) || !S.c().equals("1")) {
        this.L.setVisibility(8);
    } else {
        this.L.setVisibility(0);                   // إظهار زر التقاط صورة
    }
    digitsKeyListener = new DigitsKeyListener(false, true);   // ✅ عشري مسموح
}
if (i == 3) {                                      // Customer Location
    this.x.setInputType(1);                        // text
    digitsKeyListener = null;
}
```

**اكتشاف 🟡:** الفرق بين الدفع والقراءة في الإدخال:
- **الدفع:** `DigitsKeyListener(false, false)` → **بدون فاصلة عشرية!** (integer فقط)
- **القراءة:** `DigitsKeyListener(false, true)` → فاصلة عشرية مسموحة

---

## 2. الخطوات الفعلية لقراءة العداد (End-to-End)

### الخطوة 1: المستخدم يُدخل رقم المشترك

📍 **`OprationsActivity.java:574-578`** — addTextChangedListener على حقل `te_cust_no`:
```java
this.t.setOnClickListener(new w(this));
this.t.addTextChangedListener(new y(this));
this.t.setOnEditorActionListener(new z(this));
```

### الخطوة 2: جلب بيانات المشترك من السيرفر

📍 **`OprationsActivity.java:262-275`** — `X(String str)`:
```java
public void X(String str) {
    c.b.a.f.c cVar = new c.b.a.f.c(this);
    com.egy.webpaymentapp.webapi.models.d dVar = new com.egy.webpaymentapp.webapi.models.d();
    dVar.f2461d = MediaSessionCompat.C(this).f();
    dVar.a(MediaSessionCompat.C(this).n());
    dVar.f2458a = str;
    StringBuilder o = c.a.a.a.a.o("");
    o.append(this.B);                                  // OP_TYP
    dVar.k = o.toString();
    dVar.f2460c = "";
    cVar.b("/api/Payment/GetCustomersData", dVar,
          com.egy.webpaymentapp.webapi.models.b.class, new b(), null);
}
```

🟡 **ملاحظة:** نفس endpoint `GetCustomersData` للدفع والقراءة — الفرق فقط في الحقل `k` (= OP_TYP). السيرفر يُرجع بيانات مختلفة بناءً على ذلك.

### الخطوة 3: استلام بيانات المشترك + القراءة السابقة

📍 **`OprationsActivity.java:285-303`** — `a0(c.b.a.a.c cVar)`:
```java
public void a0(c.b.a.a.c cVar) {
    this.s = cVar;
    if (cVar != null) {
        this.t.setText(cVar.f1829b);          // رقم المشترك
        this.v.setText(cVar.f1828a);          // اسم المشترك
        this.u.setText(cVar.g);               // العنوان
        this.P = cVar.i;
        this.W = true;
        int i = this.B;
        if (i == 1) {
            this.U.setText(... cust_bal + " : " + cVar.f1831d + " ريال  ");
            this.O = cVar.f1831d;
            this.z.setVisibility(0);
        } else if (i == 2) {
            // 🔍 عرض القراءة السابقة فقط — لا حد min/max
            this.U.setText(... prev_reading + " : " + cVar.h);
        }
        this.x.requestFocus();
    }
}
```

🔴 **اكتشاف خطير:** يعرض القراءة السابقة `cVar.h` كـ "هاديء" فقط — **لا توجد أي validation تمنع إدخال قراءة أقل من السابقة، ولا حد أعلى منطقي**.

### الخطوة 4: المستخدم يُدخل القراءة الجديدة

اكتشاف من سطر 469 vs 512:
- حقل القراءة يقبل أرقاماً عشرية (مثلاً `12345.5` مسموح)
- 🔴 **لا يوجد setError() على قيم غير منطقية** — فقط على الفارغة:

📍 **`OprationsActivity.java:209-214`** — التحقق الوحيد:
```java
if (TextUtils.isEmpty(oprationsActivity.x.getText().toString())) {
    if (oprationsActivity.B != 3) {
        oprationsActivity.x.setError(... R.string.enter_filed_data);
        editText = oprationsActivity.x;
    }
}
```

### الخطوة 5: التقاط صورة العدّاد (اختياري حسب config المشترك)

📍 **`OprationsActivity.java:498-506`** — التحقق من إلزامية الصورة:
```java
if (oprationsActivity.B != 2 ||
    TextUtils.isEmpty(oprationsActivity.S.c()) ||
    !oprationsActivity.S.c().equals("1") ||
    !TextUtils.isEmpty(oprationsActivity.M) ||
    TextUtils.isEmpty(oprationsActivity.S.i()) ||
    !oprationsActivity.S.i().equals("1") ||
    !TextUtils.isEmpty(oprationsActivity.M)) {
    // image not required OR already taken
}
Toast.makeText(oprationsActivity,
    oprationsActivity.getString(R.string.txt_mter_img_must), 1).show();
```

🟡 **ملاحظة:** إلزامية الصورة تعتمد على حقلَين في كائن User:
- `User.c()` (الحقل i في User.java) = "1" → الصورة إلزامية
- `User.i()` (الحقل j) = "1" → الصورة إلزامية

### الخطوة 6: استدعاء الكاميرا الخارجية

📍 **`OprationsActivity.java:306-348`** — `y(OprationsActivity oprationsActivity, String str, int i)`:
```java
String format = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.ENGLISH).format(new Date());
StringBuilder o = c.a.a.a.a.o("CUSTMETER-1-");
o.append(MediaSessionCompat.C(oprationsActivity).f());  // user_no
o.append("-");
o.append(str);                                          // cust_no
o.append("-");
o.append(format);                                       // timestamp
o.append(".png");
oprationsActivity.N = o.toString();
// مثال: CUSTMETER-1-USER001-CUST123-20260522_140530.png

File file = new File(
    Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES),
    "WEBPAYMENT");
if (!file.exists()) {
    file.mkdirs();
}
File file2 = new File(file.getAbsolutePath() + File.separator + oprationsActivity.N);
String absolutePath = file2.getAbsolutePath();
oprationsActivity.R = absolutePath;
Log.i("xmy", absolutePath);   // 🟡 logging full path to logcat
...
a.b bVar = new a.b();
bVar.n(true);
bVar.t(1);
bVar.p("WEBPAYMENT");
bVar.s(oprationsActivity.N.replace(".png", ""));
bVar.q("png");
bVar.o(70);                                              // quality 70
bVar.r(oprationsActivity.S.g() > 0 ? oprationsActivity.S.g() : 300);  // max width
c.d.a.a m = bVar.m(oprationsActivity);
oprationsActivity.r = m;
m.c();   // → c.d.a.a.c() → external camera intent
```

🔴 **اكتشاف أمني:** الصور تُحفَظ في:
- `Environment.getExternalStoragePublicDirectory(DIRECTORY_PICTURES)/WEBPAYMENT/`
- هذا المجلد **مرئي للمستخدم في معرض الصور** ومتاح لكل التطبيقات (قبل Android 11)
- اسم الملف يحوي معرّفات حساسة (`user_no` + `cust_no`)

### الخطوة 7: آلية الكاميرا

📍 **`c/d/a/a.java:292-321`** — `c()`:
```java
public void c() {
    Fragment fragment;
    Intent intent = new Intent("android.media.action.IMAGE_CAPTURE");
    int ordinal = this.m.ordinal();
    if (ordinal == 0) {
        if (intent.resolveActivity(this.f2267b.getPackageManager()) == null) {
            throw new IllegalAccessException("Unable to open camera");
        }
        b(intent);
        this.f2267b.startActivityForResult(intent, o);  // o = 1234
        return;
    }
    ...
}
```

🟡 **ملاحظة:** يستخدم **External Camera Intent** (`ACTION_IMAGE_CAPTURE`) — ليس CameraX/Camera2 المُدمج. هذا يعني:
- ✅ بسيط ومتوافق مع كل الأجهزة
- 🔴 يعتمد على تطبيق كاميرا خارجي (قد يكون رديئاً)
- 🔴 لا يوجد تحكم في الإضاءة/التركيز للأرقام الدقيقة
- 🔴 لا OCR لاستخراج الرقم تلقائياً من الصورة

### الخطوة 8: معالجة الصورة بعد الالتقاط

📍 **`OprationsActivity.java:382-418`** — `onActivityResult()`:
```java
if (i != c.d.a.a.o) { ... return; }
if (this.r.a() == null) {
    Toast.makeText(getApplicationContext(), "Picture not taken!", 0).show();
    return;
}
String str = this.R;
int g = this.S.g();                              // max width from User config
try {
    Bitmap decodeFile = BitmapFactory.decodeFile(str);
    int width = decodeFile.getWidth();
    int height = decodeFile.getHeight();
    if (g <= 0) {
        g = 300;                                 // default max width = 300px
    }
    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
    if (width > g) {
        Bitmap.createScaledBitmap(decodeFile, g, height / (width / g), false)
              .compress(Bitmap.CompressFormat.PNG, 70, byteArrayOutputStream);
    }
    Bitmap decodeStream = BitmapFactory.decodeStream(new ByteArrayInputStream(byteArrayOutputStream.toByteArray()));
    File file = new File(str);
    file.getName();
    if (file.exists()) {
        file.delete();
    }
    decodeStream.compress(Bitmap.CompressFormat.PNG, 80,
                          new FileOutputStream(new File(str)));
    byteArrayOutputStream.flush();
    byteArrayOutputStream.close();
} catch (Exception e2) {
    e2.printStackTrace();                        // 🔴 يبتلع الخطأ بدون feedback للمستخدم
}
Bitmap decodeFile2 = BitmapFactory.decodeFile(this.R);
ByteArrayOutputStream byteArrayOutputStream2 = new ByteArrayOutputStream();
decodeFile2.compress(Bitmap.CompressFormat.PNG, 100, byteArrayOutputStream2);
this.K.setImageBitmap(decodeFile2);
this.K.setVisibility(0);
this.M = Base64.encodeToString(byteArrayOutputStream2.toByteArray(), 0);
```

🟡 **اكتشافات معالجة الصورة:**
1. **عرض أقصى 300px** (إذا لم يُحدَّد في User config) — صغير جداً للأرقام الدقيقة!
2. **ضغط مرتَين** PNG-70 ثم PNG-80 (مزدوج، يُتلف الجودة)
3. **PNG-100** للترميز Base64 النهائي
4. **OutOfMemoryError محتمل**: تحميل 3 Bitmap في الذاكرة في نفس الوقت (`decodeFile`, `decodeStream`, `decodeFile2`)
5. `Base64.encodeToString(..., 0)` — flag=0 = DEFAULT (يُضيف newlines!) 🔴

### الخطوة 9: التأكيد ثم الإرسال

📍 **`OprationsActivity.java:240-260`** — `V()` تبني نص تأكيد:
```java
sb.append("\n\n");
sb.append(oprationsActivity.V.getText().toString());
str = sb.toString() + ... ;
c.b.a.d.d(str + "\n" + R.string.txt_op_confirmation,
          oprationsActivity, new e0(oprationsActivity));
```

📍 **`Screens/e0.java:66-78`** — عند تأكيد المستخدم لعملية القراءة:
```java
if (this.f2365b.B == 2) {
    OprationsActivity oprationsActivity2 = this.f2365b;
    String obj5 = oprationsActivity2.t.getText().toString();  // cust_no
    String obj6 = oprationsActivity2.v.getText().toString();  // cust_name
    String obj7 = oprationsActivity2.x.getText().toString();  // reading value
    String obj8 = oprationsActivity2.w.getText().toString();  // note
    String str = oprationsActivity2.N;                        // image filename
    String str2 = oprationsActivity2.M;                        // image base64
    OprationsActivity.E(oprationsActivity2, obj5, obj6, obj7, obj8, str, str2);
}
```

### الخطوة 10: بناء طلب الإرسال

📍 **`OprationsActivity.java:129-153`** — `E()`:
```java
public static void E(OprationsActivity oprationsActivity,
                     String cust_no, String cust_name, String reading,
                     String note, String img_name, String img_base64) {
    c.b.a.f.c cVar = new c.b.a.f.c(oprationsActivity);
    com.egy.webpaymentapp.webapi.models.d dVar = new com.egy.webpaymentapp.webapi.models.d();
    dVar.a(MediaSessionCompat.C(oprationsActivity).n());  // acc_token
    User C = MediaSessionCompat.C(oprationsActivity);
    dVar.g = C;
    C.s("");                                              // ✅ يمسح Password قبل الإرسال
    dVar.f2461d = dVar.g.f();                             // user_no

    Payinfo payinfo = new Payinfo();
    dVar.f = payinfo;
    payinfo.e(cust_no);                                   // c_no
    dVar.f.d(cust_name);                                  // c_name
    dVar.f.f(note);                                       // c_note
    dVar.f.b(img_name);                                   // BRD_ImgName
    dVar.k = "" + oprationsActivity.B;                    // OP_TYP = "2"
    if (!TextUtils.isEmpty(oprationsActivity.S.j()) && S.j().equals("1")) {
        dVar.f.i(img_base64);                             // BRD_ImgData (Base64)
    }
    dVar.f.h(reading);                                    // v_amt ← القراءة هنا!
    dVar.f.g(c.b.a.c.d(oprationsActivity).f());           // user_gps_loc
    cVar.b("/api/Payment/saveReadingRequest", dVar,
          com.egy.webpaymentapp.webapi.models.b.class, new t(oprationsActivity), null);
}
```

🟡 **اكتشاف ضعيف:** القراءة تُرسَل في حقل اسمه `v_amt` (variable amount) — نفس الحقل الذي يحمل المبلغ في عملية الدفع. هذا يُعقِّد understanding السيرفر.

🟢 **نقطة إيجابية:** يمسح Password (`C.s("")`) قبل الإرسال — لكن لاحظ: في هذا السياق User يُعاد بناؤه من `MediaSessionCompat.C()` فقد يكون السبب أن Password يُمسح فقط من نسخة الإرسال (وما يزال في الذاكرة).

---

## 3. البيانات المُرسَلة فعلياً في طلب القراءة

📍 من **`webapi/models/Payinfo.java`** + **`webapi/models/d.java`**:

```json
POST /api/Payment/saveReadingRequest
Content-Type: application/json

{
  "acc_token": "...",
  "user_no": "USER001",
  "user": {  ← كائن User كامل (مع Password = "" بعد المسح)
    "user_no": "USER001",
    "user_name": "...",
    ...
  },
  "k": "2",
  "payinfo": {
    "c_no": "CUST123",
    "c_name": "...",
    "v_amt": "12345.5",          ← القراءة (string!)
    "c_note": "...",
    "BRD_ImgName": "CUSTMETER-1-USER001-CUST123-20260522_140530.png",
    "BRD_ImgData": "iVBORw0KGgo...",   ← Base64 PNG (kilobyte+!)
    "user_gps_loc": "lat:15.349&lng:44.205"
  }
}
```

🟡 **حجم الطلب:** صورة 300×400 PNG-100 Base64 ≈ **50-150KB لكل طلب**. لشبكات ضعيفة في اليمن، قد يفشل التحميل.

---

## 4. التحقق من صحة القراءة

### 4.1 ما **يُتحقَّق منه فعلياً** في الكود

📍 **`OprationsActivity.java:200-225`** — `U()`:

| العنصر | التحقق | الموقع |
|---|---|---|
| رقم المشترك فارغ؟ | ✅ `Toast.makeText(... R.string.txt_cust_no)` | سطر 220 |
| اسم المشترك (تم جلبه من السيرفر)؟ | ✅ `!W` يمنع المتابعة | سطر 204 |
| قيمة القراءة فارغة؟ | ✅ `setError("ادخل البيانات")` | سطر 211 |
| إلزامية صورة العدّاد؟ | ✅ Toast إن كانت مطلوبة وغير ملتقطة | سطر 217 |
| GPS موقع المستخدم؟ | ✅ يُنتَظَر `S.h()` ميلي ثانية ثم timeout | `Z()` |

### 4.2 ما **لا يُتحقَّق منه** (🔴 خطير)

| العنصر | الحالة |
|---|---|
| القراءة الجديدة ≥ القراءة السابقة؟ | 🔴 **لا يوجد** |
| القراءة في نطاق معقول (min/max)؟ | 🔴 **لا يوجد** |
| فرق القراءة عن السابقة معقول (لا قفزة ضخمة)؟ | 🔴 **لا يوجد** |
| الصورة فيها فعلاً عدّاد (OCR)؟ | 🔴 **لا يوجد** |
| GPS داخل منطقة المنطقة المُكلَّف بها؟ | 🔴 **لا يوجد** |
| الوقت معقول (لا قراءتان في دقيقة)؟ | 🔴 **لا يوجد** |

**الاستنتاج:** كل التحقق منطقياً يُترَك للسيرفر. التطبيق يُرسل أي قيمة يُدخلها المستخدم.

---

## 5. سلوك التطبيق عند انقطاع الإنترنت 🔴

### 5.1 ما يحدث عند فشل الشبكة

📍 **`c/b/a/f/c.java:90-145`** — `q.a` (Volley error listener):
```java
public void a(u uVar) {
    uVar.printStackTrace();
    this.f1903a.dismiss();                       // أخفِ ProgressDialog
    l lVar = uVar.f1779b;
    if ((uVar instanceof s) && lVar != null) {
        try {
            new JSONObject(new String(lVar.f1755b, ...));  // محاولة قراءة body
        } catch (...) {}
    }
    l lVar2 = uVar.f1779b;
    if (lVar2 != null && lVar2.f1754a == 401) {
        new f0(c.this.f1900a, null).h();         // unauthorized → logout
        return;
    }
    ...
    String message = uVar.getMessage();
    if (!TextUtils.isEmpty(message) && message.toLowerCase().contains("failed to connect to")) {
        message = "فشل الاتصال بالخادم";          // ← الرسالة العربية الوحيدة!
    }
    ...
    c.b.a.d.e(message, c.this.f1900a);           // عرض Dialog
}
```

### 5.2 ما **لا يحدث** بعد الفشل 🔴

| السلوك المتوقع | الواقع |
|---|---|
| حفظ القراءة محلياً للإرسال لاحقاً | 🔴 **لا يوجد** |
| Retry تلقائي مع backoff | 🔴 **لا يوجد** |
| Queue للعمليات المُعلَّقة | 🔴 **لا يوجد** |
| Outbox pattern لضمان عدم التكرار | 🔴 **لا يوجد** |
| WorkManager للمزامنة في الخلفية | 🔴 **لا يوجد** |
| إبلاغ المستخدم بضرورة إعادة الإدخال | 🟡 يظهر فقط Dialog بالرسالة |

**اكتشاف خطير:** الصورة `M = Base64...` تبقى في الذاكرة حتى تُمسَح بـ `P(oprationsActivity)` — لكنها تُمسَح **حتى عند الفشل**! لاحظ سطر 187-188:
```java
oprationsActivity.K.setImageBitmap(null);
oprationsActivity.K.setVisibility(8);
```
يُستدعى عند نجاح إرسال — وفي بعض حالات الفشل أيضاً.

### 5.3 البحث في الكود عن SQLite/Room/Database

📍 **بحث grep في `com/egy/webpaymentapp/`:**
```
SQLite     → 0 matches
Room       → 0 matches
Database   → 1 match (WebView.setDatabaseEnabled — للـ JS storage فقط)
offline    → 0 matches
```

**النتيجة الموثَّقة:** لا يوجد أي تخزين محلي للقراءات في التطبيق. كل البيانات إمَّا في الذاكرة (مؤقتاً) أو في `SharedPreferences` (للجلسة فقط).

---

## 6. التخزين المؤقت (في SharedPreferences)

### 6.1 ما يُحفَظ فعلياً

📍 **`c/b/a/c.java`** — `c.b.a.c` (SharedPreferences wrapper) يحفظ:
- `APP_USER_LOC_KEY` ← آخر إحداثيات GPS (`"lat:15.349&lng:44.205"`)
- `APP_PAYMENT_SELECTED_AREA_KEY` ← آخر منطقة مختارة للدفع
- `APP_READING_SELECTED_AREA_KEY` ← آخر منطقة مختارة للقراءة
- `APP_PRINTERADREES_KEY` ← MAC address للطابعة
- `USER_DETAILS_PREF` ← بيانات المستخدم (User serialized)

### 6.2 ما **لا** يُحفَظ

- قائمة المشتركين (يجب طلبها من السيرفر في كل مرة)
- القراءات السابقة (موجودة مع كل استجابة `GetCustomersData`)
- القراءات المُعلَّقة (التي فشل إرسالها) 🔴

---

## 7. حالات الفشل والاسترداد

### 7.1 ما يحدث عند نقاط فشل مختلفة

| اللحظة | إذا فشل | تأثير على المستخدم | تأثير على البيانات |
|---|---|---|---|
| التقاط الصورة | "Picture not taken!" Toast | يُعيد المحاولة | لا فقدان |
| ضغط الصورة | `e2.printStackTrace()` صامت | لا feedback! 🔴 | الصورة المعالجة قد تكون فاسدة |
| تحويل Base64 | OutOfMemoryError محتمل | crash | فقدان الصورة |
| إرسال HTTP | Dialog "فشل الاتصال" | يجب إعادة كل العملية يدوياً 🔴 | فقدان: القراءة + الصورة (إن لم يُحفظ نسخة خارجية) |
| استجابة 401 | Auto-logout | فقدان كل البيانات | فقدان كل شيء |
| استجابة 500 | عرض رسالة السيرفر | يجب إعادة العملية يدوياً | فقدان |
| Timeout (Volley default) | بعد ~30 ثانية | عرض رسالة | فقدان البيانات في الذاكرة |

### 7.2 الصورة على القرص

📍 **`OprationsActivity.java:402-404`**:
```java
File file = new File(str);
if (file.exists()) {
    file.delete();          // تُحذف الصورة الأصلية بعد المعالجة!
}
```

ثم تُكتَب نسخة مضغوطة بنفس الاسم. لكن:
- 🟡 الصورة المضغوطة تبقى على الـ External Storage إلى الأبد (لا cleanup)
- 🔴 إذا فشل الإرسال، الصورة موجودة على القرص لكن **لا يوجد آلية لإعادة قراءتها لإعادة المحاولة**

---

## 8. مزامنة القراءات مع الـ Backend

### 8.1 العملية الكاملة

```
[User Input] → [Memory only] → [HTTP POST] → [Server]
                  ↓ (loss on crash/timeout)
                  ✗ no persistence
```

### 8.2 لا توجد قائمة قراءات معلّقة محلية

`saveReadingRequest` هو endpoint **fire-and-forget**:
- ✅ السيرفر يستجيب بـ `b` model يحوي `errorCode` و `errorMsg`
- 🔴 إن فشل الـ HTTP → لا تكرار محلي

### 8.3 قائمة القراءات تُجلَب من السيرفر فقط

📍 **`Screens/web/WebviewActivity.java:257`**:
```java
cVar.b("/api/Payment/GetReadingListData", dVar, ..., new b(activity), null);
```

📍 **`Screens/i.java:22-23`**:
```java
intent.putExtra("page", "file:///android_asset/myweb/readinglist.html");
intent.putExtra("title", this.f2378b.getString(R.string.reading_list));
```

→ كل قائمة القراءات تُعرَض في WebView بعد جلبها من السيرفر، **بدون cache محلي**.

---

## 9. مقارنة Reading vs Payment (نفس الشاشة)

| العنصر | Payment (B=1) | Reading (B=2) |
|---|---|---|
| Endpoint إرسال | `/api/Payment/saveBillRequest` | `/api/Payment/saveReadingRequest` |
| Endpoint جلب | `/api/Payment/GetCustomersData?k=1` | `/api/Payment/GetCustomersData?k=2` |
| القائمة (history) | `paymentList.html` | `readinglist.html` |
| الحقل الرئيسي | المبلغ (`v_amt`) | القراءة (`v_amt`) — نفس الحقل! |
| الفاصلة العشرية | 🔴 ممنوعة (`DigitsKeyListener(false, false)`) | ✅ مسموحة |
| صورة | 🔴 لا تُلتقط | ✅ تُلتقَط (إن كان `User.c()=="1"`) |
| التحقق من الرصيد | ✅ `Double.parseDouble(balance) < Double.parseDouble(paid)` | 🔴 لا يوجد |
| الحساب | `int parseInt = balance - paid` (Integer!) | لا حساب |
| Bixolon Printer | ✅ مُهيَّأ | 🔴 غير مُهيَّأ (سطر 491) |

**اكتشاف صادم:** سطر 491 من `OprationsActivity.java`:
```java
if (this.B == 1) {
    r().m(R.string.text_payments);
    this.q = new com.egy.webpaymentapp.BixlonPrinterManger.a(this);  // ← Bixolon فقط للدفع!
}
if (this.B == 2) {
    r().m(R.string.text_meter_reading);
    // ⚠️ لا يوجد إنشاء printer manager — لا يمكن طباعة إيصال للقراءة
}
```

→ **لا يمكن طباعة إيصال لعملية قراءة العدّاد** (فقط للدفع).

---

## 10. ملخص الاكتشافات والتقييم

### 🟢 نقاط إيجابية

| # | النقطة | الموقع |
|---|---|---|
| 1 | فصل واضح بين 3 عمليات في شاشة واحدة (logic clean) | `OprationsActivity.java:463-512` |
| 2 | تسمية ملف الصورة تحوي معرّفات مفيدة للتتبع | `OprationsActivity.java:311-319` |
| 3 | DigitsKeyListener يفصل بين integer (دفع) و decimal (قراءة) | `OprationsActivity.java:469, 512` |
| 4 | GPS يُجمع تلقائياً ويُرسَل مع كل قراءة | `c/b/a/b/d.java` + `Payinfo.user_gps_loc` |
| 5 | Password يُمسح من User object قبل الإرسال | `OprationsActivity.java:138` (`C.s("")`) |

### 🟡 نقاط متوسطة

| # | الملاحظة | الموقع |
|---|---|---|
| 1 | استخدام `Payinfo` لكل العمليات (نفس DTO للدفع/القراءة/الموقع) | `webapi/models/Payinfo.java` |
| 2 | اعتماد External Camera Intent (لا CameraX) | `c/d/a/a.java:294` |
| 3 | حجم الصورة Default صغير (300px) | `OprationsActivity.java:388` |
| 4 | ضغط مزدوج للصورة يُتلف الجودة | `OprationsActivity.java:395-407` |
| 5 | Base64 flag=0 (DEFAULT) يُضيف newlines في النص | `OprationsActivity.java:417` |
| 6 | لا cleanup للصور القديمة على External Storage | — |

### 🔴 نقاط سيئة (مشاكل حقيقية)

| # | المشكلة | الموقع | الأثر |
|---|---|---|---|
| 1 | **لا يوجد أي تخزين محلي للقراءات** | كل الكود | فقدان البيانات عند فشل الشبكة |
| 2 | **لا توجد حدود min/max للقراءة** | `OprationsActivity.java:U()` | يقبل أي رقم (سلبي/ضخم/أقل من السابق) |
| 3 | **لا تحقق من تسلسل القراءة** (الجديدة ≥ السابقة) | — | قراءة 12345 ثم 50 ستُقبل! |
| 4 | **Retry غير موجود** | `c/b/a/f/c.java` | فشل HTTP = إعادة العملية يدوياً |
| 5 | **External Storage عام للصور** | `OprationsActivity.java:316-319` | الصور مرئية لكل التطبيقات (قبل Android 11) |
| 6 | **اسم ملف الصورة يكشف معرّفات** (user_no + cust_no) | `OprationsActivity.java:313-317` | معلومات شخصية في metadata الملف |
| 7 | **بلع الاستثناءات** صامتاً (`printStackTrace`) | `OprationsActivity.java:411` | المستخدم لا يعرف لماذا فشلت العملية |
| 8 | **لا OCR** للأرقام من الصورة | — | يُعتمد على دقة المستخدم في الإدخال اليدوي |
| 9 | **لا يمكن طباعة إيصال قراءة** | `OprationsActivity.java:493-494` | (تصميمي — قد يكون مقصوداً) |
| 10 | **OutOfMemoryError محتمل** (3 Bitmaps في الذاكرة) | `OprationsActivity.java:391-413` | crash على أجهزة ضعيفة |
| 11 | **حجم Request ضخم** (Base64 PNG 50-150KB) | حسابات | فشل على شبكات ضعيفة |

---

## 11. توصيات الإصلاح (للنسخة الحالية، ليس البناء الجديد)

### الأولوية الحرجة (P0)

1. **إضافة Outbox محلي للقراءات**
   - استخدم SQLite (Room) لحفظ كل قراءة قبل الإرسال
   - WorkManager لإعادة المحاولة في الخلفية مع backoff
   - عرض الحالة للمستخدم: "في انتظار الإرسال" / "أُرسلت بنجاح"

2. **التحقق من تسلسل القراءة**
   ```java
   double prev = Double.parseDouble(cVar.h);     // previous reading
   double curr = Double.parseDouble(x.getText().toString());
   if (curr < prev) {
       x.setError("القراءة الجديدة أقل من السابقة (" + prev + ")");
       return false;
   }
   if (curr - prev > prev * 0.5) {  // قفزة > 50%
       // اطلب تأكيد إضافي
   }
   ```

### الأولوية العالية (P1)

3. **استخدام Scoped Storage للصور** (Android 11+)
   - استبدال `getExternalStoragePublicDirectory` بـ `context.getExternalFilesDir(null)`
   - الصور تُحذَف تلقائياً عند uninstall

4. **اختزال حجم الصورة قبل الإرسال**
   - استهداف 100-200KB max (JPEG quality 80 بدل PNG)
   - تغيير اسم الحقل من `BRD_ImgData` (PNG) إلى يدعم JPEG في الـ DTO

5. **تحسين معالجة الأخطاء**
   - استبدال `printStackTrace()` بـ Snackbar/Toast مع رسالة واضحة
   - تسجيل الـ stack trace في Crashlytics (مع filtering للبيانات الشخصية)

### الأولوية المتوسطة (P2)

6. **OCR للأرقام** (اختياري)
   - استخدم ML Kit Text Recognition
   - عرض الرقم المُستخرَج للمستخدم للتأكيد قبل الإرسال

7. **CameraX بدلاً من Intent**
   - تحكم أفضل بالإضاءة والتركيز
   - معاينة مباشرة قبل الالتقاط

---

## 12. مصادر التحقق

كل الاكتشافات أعلاه قابلة للتحقق من الملفات التالية في `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/`:

| الملف | الأسطر المهمة |
|---|---|
| `com/egy/webpaymentapp/Screens/OprationsActivity.java` | 100-624 (الكامل) |
| `com/egy/webpaymentapp/Screens/e0.java` | 66-78 (Reading branch) |
| `com/egy/webpaymentapp/Screens/x.java` | 28 (balance check) |
| `com/egy/webpaymentapp/Screens/y.java` | text watcher |
| `com/egy/webpaymentapp/Screens/i.java` | 22-23 (reading list webview) |
| `com/egy/webpaymentapp/Screens/web/WebviewActivity.java` | 257 (GetReadingListData) |
| `com/egy/webpaymentapp/Screens/web/i.java` | 26-28 (GetReadingDataRequest JS bridge) |
| `com/egy/webpaymentapp/webapi/models/Payinfo.java` | full (DTO with `v_amt`, `BRD_ImgData`) |
| `c/d/a/a.java` | 294-321 (camera intent) |
| `c/b/a/b/d.java` | full (GPS manager) |
| `c/b/a/f/c.java` | 90-145 (error handler) |

---

**🔑 الخلاصة:** ميزة قراءة العدّاد **تعمل في الحالة المثالية فقط** (شبكة سليمة + مستخدم يُدخل قيمة معقولة + لا أخطاء في الكاميرا). أي انحراف عن هذا المسار → فقدان بيانات صامت أو تجربة سيئة. أولوية الإصلاح: **بناء طبقة Outbox محلية + Retry + Validation منطقي**.
