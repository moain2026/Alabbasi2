# 02.6 — أمثلة Request/Response جاهزة (Curl + Postman)

> أمثلة قابلة للنسخ مباشرة لاختبار الـ API. تعتمد على البيانات المُستخلصة من الكود.
> ⚠️ هذه أمثلة **تمثيلية** ـ الأمثلة الفعلية ستظهر بمراقبة الشبكة الحقيقية (mitmproxy/Charles).

---

## 1. getAppPK

### Curl
```bash
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Users/getAppPK' \
  -H 'Content-Type: application/json' \
  --data 'null'
```
(الـ `-k` لأن الشهادة self-signed.)

### Response مُتوقع
```json
{
  "GEN_API_ERR_NO": 0,
  "GEN_API_ERR_MSG": "",
  "apppk": "ANxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==&AQAB"
}
```

---

## 2. Login

### Curl (سيكون كلمة السر مُشفّرة فعلياً ـ هنا مثال)
```bash
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Users/Login' \
  -H 'Content-Type: application/json' \
  -d '{
    "Username": "ahmad.cashier",
    "user_branch": "01",
    "Password": "<RSA_encrypted_password_base64>",
    "mob_srl": "<RSA_encrypted_android_id_base64>"
  }'
```

### Response — نجاح
```json
{
  "GEN_API_ERR_NO": 0,
  "GEN_API_ERR_MSG": "",
  "user": {
    "Id": "123",
    "FirstName": "أحمد",
    "LastName": "علي",
    "Username": "ahmad.cashier",
    "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "Password": null,
    "mob_srl": "...",
    "restpass": "0",
    "Cshr_AddWebPay": "1",
    "Cshr_AddWebRead": "1",
    "Cshr_AddWebMtrImg": "1",
    "Cshr_AddWebCstUpDate": "1",
    "webview_url": "",
    "open_url_out_app": 0,
    "Ues_Gps": 1,
    "loc_up_interval": 30000,
    "imgWdth": "300",
    "Cshr_AddWOtherOpr": "0",
    "read_must_take_img": "1",
    "read_save_img_online": "1",
    "user_branch": "01"
  },
  "AreaList": [
    {"f1828a": "كل المناطق", "f1829b": "0", "f1830c": 1},
    {"f1828a": "حي السبعين", "f1829b": "01", "f1830c": 1},
    {"f1828a": "حي الستين",  "f1829b": "02", "f1830c": 1},
    {"f1828a": "شارع الزبيري", "f1829b": "03", "f1830c": 1}
  ]
}
```

### Response — فشل
```json
{
  "GEN_API_ERR_NO": 100,
  "GEN_API_ERR_MSG": "اسم المستخدم أو كلمة المرور غير صحيحة"
}
```

---

## 3. ChangePassword

### Curl
```bash
TOKEN="eyJhbGciOiJIUzI1NiI..."
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Users/changePasswordRequest' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "user_no": "123",
    "user_branch": "01",
    "user": {
      "Id": "123",
      "Username": "ahmad.cashier",
      "Token": "",
      "mob_srl": "<RSA_encrypted_android_id>",
      "user_branch": "01"
    },
    "oldpass": "<RSA_encrypted_oldpassword>",
    "newpass": "<RSA_encrypted_newpassword>"
  }'
```

### Response
```json
{
  "GEN_API_ERR_NO": 0,
  "user": { /* … user object … */ }
}
```

---

## 4. GetCustomersData

### Curl
```bash
TOKEN="..."
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Payment/GetCustomersData' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "c_no": "123456",
    "op_typ": "1",
    "user_no": "123",
    "user_branch": "01",
    "area_no": ""
  }'
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

---

## 5. saveBillRequest (دفع)

### Curl
```bash
TOKEN="..."
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Payment/saveBillRequest' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "user_branch": "01",
    "user": {
      "Id": "123",
      "Username": "ahmad.cashier",
      "Token": "",
      "user_branch": "01"
    },
    "payinfo": {
      "c_no": "123456",
      "c_name": "محمد عبدالله الأحمدي",
      "c_bal": "9500",
      "v_amt": "3000",
      "c_note": "دفع جزئي",
      "user_gps_loc": "15.349,44.207"
    }
  }'
```

### Response
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

---

## 6. saveReadingRequest (قراءة عدّاد)

### Curl
```bash
TOKEN="..."
# الصورة Base64 يجب إنشاؤها قبل الإرسال:
IMG_B64=$(base64 -w0 meter.png)

curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Payment/saveReadingRequest' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d @- <<EOF
{
  "user_no": "123",
  "user_branch": "01",
  "user": {"Id":"123","Username":"ahmad.cashier","Token":"","user_branch":"01"},
  "op_typ": "2",
  "payinfo": {
    "c_no": "123456",
    "c_name": "محمد عبدالله الأحمدي",
    "v_amt": "9123",
    "c_note": "",
    "BRD_ImgName": "CUSTMETER-1-123-123456-20251120_143201.png",
    "BRD_ImgData": "${IMG_B64}",
    "user_gps_loc": "15.349,44.207"
  }
}
EOF
```

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

## 7. saveCustLocation

### Curl
```bash
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Payment/saveCustLocation' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "user_branch": "01",
    "user": {"Id":"123","Username":"ahmad.cashier","Token":""},
    "payinfo": {
      "c_no": "123456",
      "c_name": "محمد عبدالله الأحمدي",
      "user_gps_loc": "15.349,44.207"
    }
  }'
```

### Response
```json
{ "GEN_API_ERR_NO": 0, "GEN_API_ERR_MSG": "تم تحديث الموقع" }
```

---

## 8. GetPaymentsReportData (قائمة المدفوعات)

### Curl
```bash
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Payment/GetPaymentsReportData' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "user_branch": "01",
    "user": {"Id":"123","Username":"ahmad.cashier","Token":""},
    "findVal": ""
  }'
```

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
    {
      "c_no": "654321",
      "c_name": "علي سعيد المهري",
      "c_bal": "5000",
      "v_amt": "5000",
      "v_date": "2025-11-20 13:15",
      "v_no": "EC-2025-00012344",
      "user_name": "أحمد علي",
      "user_no": "123",
      "comp_name": "شركة عبّاس للتحصيل",
      "comp_add": "صنعاء",
      "comp_tel": "+967-1-234567",
      "brD_ImgName": null
    }
  ]
}
```

---

## 9. GetReadingListData

```bash
curl -k -X POST 'https://abbasiy.yedns.org:8057/payment/api/Payment/GetReadingListData' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "user_branch": "01",
    "user": {"Id":"123","Token":""},
    "findVal": ""
  }'
```

Response مماثل لـ `GetPaymentsReportData` لكن مع `brD_ImgName` غير null أحياناً.

---

## Postman Collection (يمكن استيرادها)

```json
{
  "info": { "name": "AbbasiyCashiers API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "variable": [
    { "key": "baseUrl", "value": "https://abbasiy.yedns.org:8057/payment" },
    { "key": "token",   "value": "" },
    { "key": "userNo",  "value": "123" },
    { "key": "userBranch", "value": "01" }
  ],
  "item": [
    {
      "name": "getAppPK",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/Users/getAppPK",
        "header": [{ "key": "Content-Type", "value": "application/json" }]
      }
    },
    {
      "name": "Login (after RSA encryption)",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/Users/Login",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"Username\": \"<user>\",\n  \"user_branch\": \"<branch>\",\n  \"Password\": \"<RSA-encrypted>\",\n  \"mob_srl\": \"<RSA-encrypted>\"\n}"
        }
      }
    },
    {
      "name": "GetCustomersData",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/Payment/GetCustomersData",
        "header": [
          { "key": "Authorization", "value": "Bearer {{token}}" },
          { "key": "Content-Type", "value": "application/json" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"c_no\": \"123456\",\n  \"op_typ\": \"1\",\n  \"user_no\": \"{{userNo}}\",\n  \"user_branch\": \"{{userBranch}}\",\n  \"area_no\": \"\"\n}"
        }
      }
    }
  ]
}
```

---

## Python helper script لتوليد RSA-encrypted password

```python
# الكود التالي يحاكي MediaSessionCompat.a()
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend

def encrypt_password_for_login(apppk: str, plain_password: str) -> str:
    """
    يحاكي MediaSessionCompat.a() في التطبيق الأصلي.
    apppk بصيغة "modulus_base64&exponent_base64"
    """
    parts = apppk.split("&")
    n = int.from_bytes(base64.b64decode(parts[0]), "big")
    e = int.from_bytes(base64.b64decode(parts[1]), "big")
    
    public_key = RSAPublicNumbers(e, n).public_key(default_backend())
    ciphertext = public_key.encrypt(
        plain_password.encode("utf-8"),
        padding.PKCS1v15()      # ⚠️ تطابق RSA/ECB/PKCS1PADDING في Java
    )
    return base64.b64encode(ciphertext).decode("ascii").replace("\n", "").replace("\r", "")

# مثال:
apppk = "AN.......==&AQAB"  # من response getAppPK
encrypted = encrypt_password_for_login(apppk, "my_real_password")
print(encrypted)
```

---

## Bash one-liner كامل (للاختبار الميداني)

```bash
#!/bin/bash
# اختبار كامل لمسار Login

BASE="https://abbasiy.yedns.org:8057/payment"

# 1) جلب PK
echo "=== Get PK ==="
PK=$(curl -ks -X POST "$BASE/api/Users/getAppPK" -H 'Content-Type: application/json' -d 'null' | jq -r '.apppk')
echo "PK length: ${#PK}"

# 2) تشفير كلمة المرور (يحتاج بايثون)
ENC_PASS=$(python3 -c "
import base64, sys
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
apppk = sys.argv[1]
pw    = sys.argv[2]
parts = apppk.split('&')
n = int.from_bytes(base64.b64decode(parts[0]), 'big')
e = int.from_bytes(base64.b64decode(parts[1]), 'big')
pk = RSAPublicNumbers(e, n).public_key(default_backend())
ct = pk.encrypt(pw.encode('utf-8'), padding.PKCS1v15())
print(base64.b64encode(ct).decode().replace('\n','').replace('\r',''))
" "$PK" "MY_REAL_PASSWORD")

# 3) Login
echo "=== Login ==="
RESPONSE=$(curl -ks -X POST "$BASE/api/Users/Login" \
  -H 'Content-Type: application/json' \
  -d "{\"Username\":\"u1\",\"user_branch\":\"01\",\"Password\":\"$ENC_PASS\",\"mob_srl\":\"$ENC_PASS\"}")
echo "$RESPONSE" | jq .

TOKEN=$(echo "$RESPONSE" | jq -r '.user.Token')

# 4) Get a customer
echo "=== GetCustomersData ==="
curl -ks -X POST "$BASE/api/Payment/GetCustomersData" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"c_no":"123456","op_typ":"1","user_no":"123","user_branch":"01","area_no":""}' | jq .
```

---

**التالي:** [`../03_data_models/01_user_model.md`](../03_data_models/01_user_model.md)
