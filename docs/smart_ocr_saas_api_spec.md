# API 設計規範 (API Design Specification) - Smart OCR SaaS

---

**文件版本 (Document Version):** `v1.0.0`

**最後更新 (Last Updated):** `2025-12-24`

**主要作者/設計師 (Lead Author/Designer):** `技術架構團隊`

**審核者 (Reviewers):** `API 設計委員會、核心開發團隊`

**狀態 (Status):** `草稿 (Draft)`

**相關 SD 文檔:** `[smart_ocr_saas_architecture.md](./smart_ocr_saas_architecture.md)`

**OpenAPI (Swagger) 定義文件:** `/api/v1/openapi.json` (由 FastAPI 自動生成)

---

## 目錄 (Table of Contents)

1.  [引言 (Introduction)](#1-引言-introduction)
2.  [設計原則與約定 (Design Principles and Conventions)](#2-設計原則與約定-design-principles-and-conventions)
3.  [認證與授權 (Authentication and Authorization)](#3-認證與授權-authentication-and-authorization)
4.  [通用 API 行為 (Common API Behaviors)](#4-通用-api-行為-common-api-behaviors)
5.  [錯誤處理 (Error Handling)](#5-錯誤處理-error-handling)
6.  [安全性考量 (Security Considerations)](#6-安全性考量-security-considerations)
7.  [API 端點詳述 (API Endpoint Definitions)](#7-api-端點詳述-api-endpoint-definitions)
8.  [資料模型/Schema 定義 (Data Models / Schema Definitions)](#8-資料模型schema-定義-data-models--schema-definitions)
9.  [WebSocket 規範 (WebSocket Specification)](#9-websocket-規範-websocket-specification)
10. [API 生命週期與版本控制 (API Lifecycle and Versioning)](#10-api-生命週期與版本控制-api-lifecycle-and-versioning)
11. [附錄 (Appendix)](#11-附錄-appendix)

---

## 1. 引言 (Introduction)

### 1.1 目的 (Purpose)

本文件為 Smart OCR SaaS 系統的 RESTful API 和 WebSocket 接口提供完整的設計規範與契約定義。旨在為前端開發者、後端實現者及第三方整合者提供統一、明確的 API 使用指南。

### 1.2 目標讀者 (Target Audience)

- 前端開發者 (Next.js)
- 後端開發者 (FastAPI)
- 測試工程師
- 第三方整合開發者
- 技術文件撰寫者

### 1.3 快速入門 (Quick Start)

**第 1 步: 獲取訪問令牌 (Access Token)**

使用本地帳號登入取得 JWT Token：

```bash
curl --request POST \
  --url https://api.smartocr.example.com/api/v1/auth/login \
  --header 'Content-Type: application/json' \
  --data '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**預期回應:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**第 2 步: 發送 OCR 請求**

上傳圖片進行 OCR 辨識：

```bash
curl --request POST \
  --url https://api.smartocr.example.com/api/v1/ocr/upload \
  --header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  --form 'file=@/path/to/image.png'
```

---

## 2. 設計原則與約定 (Design Principles and Conventions)

### 2.1 API 風格 (API Style)

- **風格:** RESTful
- **核心原則:**
  - 資源導向 (Resource-Oriented)
  - 無狀態 (Stateless)
  - 標準 HTTP 方法 (GET, POST, PUT, DELETE)
  - 統一接口 (Uniform Interface)

### 2.2 基本 URL (Base URL)

| 環境 | Base URL |
|:-----|:---------|
| **生產環境 (Production)** | `https://api.smartocr.example.com/api/v1` |
| **預備環境 (Staging)** | `https://staging-api.smartocr.example.com/api/v1` |
| **開發環境 (Development)** | `http://localhost:8000/api/v1` |

### 2.3 請求與回應格式 (Request and Response Formats)

- **格式:** `application/json` (UTF-8 編碼)
- **檔案上傳:** `multipart/form-data`
- **檔案下載:** 對應的 MIME 類型 (如 `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)

**請求標頭要求:**

```
Content-Type: application/json
Accept: application/json
```

### 2.4 標準 HTTP Headers

#### 所有請求 (All Requests)

| Header | 必要性 | 說明 |
|:-------|:-------|:-----|
| `Authorization` | 必要 (除公開端點) | Bearer Token 認證憑證 |
| `Content-Type` | 必要 | 請求內容類型 |
| `Accept` | 建議 | 期望回應類型 |
| `X-Request-ID` | 可選 | 唯一請求 ID (UUID)，用於追蹤 |
| `Accept-Language` | 可選 | 期望回應語言 (e.g., `zh-TW`, `en-US`) |
| `Idempotency-Key` | 可選 | 冪等性金鑰 (用於 POST/PUT/DELETE) |

#### 所有回應 (All Responses)

| Header | 說明 |
|:-------|:-----|
| `X-Request-ID` | 請求唯一標識 (從請求傳入或伺服器生成) |
| `Content-Type` | 回應內容類型 |
| `RateLimit-Limit` | 速率限制上限 |
| `RateLimit-Remaining` | 剩餘請求次數 |
| `RateLimit-Reset` | 限制重置時間 (Unix timestamp) |

### 2.5 命名約定 (Naming Conventions)

| 類別 | 約定 | 範例 |
|:-----|:-----|:-----|
| **資源路徑** | 小寫，連字符分隔，名詞複數 | `/ocr-tasks`, `/users` |
| **查詢參數** | snake_case | `page_size`, `created_after` |
| **JSON 欄位** | snake_case | `user_id`, `extracted_text` |
| **HTTP Headers** | 標準格式或 X- 前綴 | `X-Request-ID` |

### 2.6 日期與時間格式 (Date and Time Formats)

- **標準格式:** ISO 8601，UTC 時區
- **範例:** `2025-12-24T10:30:00Z`

---

## 3. 認證與授權 (Authentication and Authorization)

### 3.1 認證機制 (Authentication Mechanism)

Smart OCR SaaS 支援兩種認證方式：

#### 3.1.1 本地帳號認證 (Local Authentication)

- **機制:** JWT (JSON Web Token)
- **傳遞方式:** HTTP-only Cookie 或 `Authorization: Bearer <token>` Header
- **Token 有效期:** 24 小時 (可配置)
- **演算法:** HS256

#### 3.1.2 LDAP/AD 認證 (Enterprise Authentication)

- **機制:** LDAP Bind 驗證 + JWT
- **支援:** Active Directory, OpenLDAP
- **連線安全:** 支援 LDAPS (SSL/TLS)

#### JWT Token 結構

```json
{
  "sub": "user_id",
  "username": "john.doe",
  "role": "user",
  "auth_type": "local",
  "exp": 1735084800,
  "iat": 1735041600
}
```

### 3.2 授權模型 (Authorization Model)

基於角色的訪問控制 (RBAC)：

| 角色 | 說明 |
|:-----|:-----|
| `admin` | 系統管理員，可管理所有使用者和資料 |
| `user` | 一般使用者，僅可存取自己的資料 |

#### 授權矩陣

| 端點 | 一般使用者 (user) | 管理員 (admin) |
|:-----|:------------------|:---------------|
| `POST /auth/login` | ✓ (無需認證) | ✓ (無需認證) |
| `GET /auth/me` | ✓ | ✓ |
| `GET /ocr/*` | 自己的資料 | 所有資料 |
| `POST /ocr/*` | ✓ | ✓ |
| `DELETE /ocr/*` | 自己的資料 | 所有資料 |
| `GET /admin/users` | ✗ (403) | ✓ |
| `POST /admin/users` | ✗ (403) | ✓ |
| `PUT /admin/users/*` | ✗ (403) | ✓ |
| `DELETE /admin/users/*` | ✗ (403) | ✓ |

---

## 4. 通用 API 行為 (Common API Behaviors)

### 4.1 分頁 (Pagination)

**策略:** 基於偏移量 (Offset-based) 的分頁

**查詢參數:**

| 參數 | 類型 | 預設值 | 說明 |
|:-----|:-----|:-------|:-----|
| `page` | integer | 1 | 頁碼 (從 1 開始) |
| `page_size` | integer | 20 | 每頁筆數 (最大 100) |

**回應結構:**

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### 4.2 排序 (Sorting)

**查詢參數:** `sort_by`

**格式:**
- 升序: `sort_by=field_name`
- 降序: `sort_by=-field_name`

**範例:** `GET /api/v1/ocr/tasks?sort_by=-created_at`

### 4.3 過濾 (Filtering)

**策略:** 直接使用欄位名作為查詢參數

**範例:**
- `GET /api/v1/ocr/tasks?status=completed`
- `GET /api/v1/ocr/tasks?created_at[gte]=2025-01-01T00:00:00Z`

**支援的操作符:**

| 操作符 | 說明 | 範例 |
|:-------|:-----|:-----|
| (無) | 等於 | `status=completed` |
| `[gte]` | 大於等於 | `created_at[gte]=2025-01-01` |
| `[lte]` | 小於等於 | `created_at[lte]=2025-12-31` |
| `[like]` | 模糊匹配 | `filename[like]=invoice` |

### 4.4 冪等性 (Idempotency)

**適用範圍:** POST, PUT, DELETE 請求

**機制:**
1. 客戶端在請求 Header 中傳遞 `Idempotency-Key: <unique-key>`
2. 伺服器快取首次請求結果
3. 24 小時內相同 Key 的請求返回快取結果

**範例:**

```bash
curl --request POST \
  --url /api/v1/ocr/upload \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000' \
  --form 'file=@image.png'
```

---

## 5. 錯誤處理 (Error Handling)

### 5.1 標準錯誤回應格式 (Standard Error Response Format)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "檔案格式不支援",
    "details": {
      "field": "file",
      "allowed_types": ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 5.2 通用 HTTP 狀態碼

#### 成功回應 (2xx)

| 狀態碼 | 說明 | 使用場景 |
|:-------|:-----|:---------|
| 200 OK | 請求成功 | GET, PUT 成功 |
| 201 Created | 資源創建成功 | POST 創建資源成功 |
| 202 Accepted | 請求已接受處理 | 非同步任務已排程 |
| 204 No Content | 成功但無內容回傳 | DELETE 成功 |

#### 客戶端錯誤 (4xx)

| 狀態碼 | 說明 | 使用場景 |
|:-------|:-----|:---------|
| 400 Bad Request | 請求格式錯誤 | 參數驗證失敗 |
| 401 Unauthorized | 未認證 | Token 無效或過期 |
| 403 Forbidden | 無權限 | 無權存取該資源 |
| 404 Not Found | 資源不存在 | 指定 ID 的資源不存在 |
| 409 Conflict | 資源衝突 | 重複創建資源 |
| 413 Payload Too Large | 請求體過大 | 檔案超過大小限制 |
| 415 Unsupported Media Type | 不支援的媒體類型 | 檔案格式不支援 |
| 429 Too Many Requests | 請求過於頻繁 | 超出速率限制 |

#### 伺服器錯誤 (5xx)

| 狀態碼 | 說明 | 使用場景 |
|:-------|:-----|:---------|
| 500 Internal Server Error | 內部錯誤 | 未預期的伺服器錯誤 |
| 503 Service Unavailable | 服務不可用 | 外部服務 (OpenAI/LDAP) 無法連線 |

### 5.3 錯誤碼字典 (Error Code Dictionary)

| 錯誤碼 | HTTP 狀態碼 | 說明 |
|:-------|:------------|:-----|
| `VALIDATION_ERROR` | 400 | 請求參數驗證失敗 |
| `UNAUTHORIZED` | 401 | 未認證或 Token 過期 |
| `FORBIDDEN` | 403 | 無權限存取 |
| `NOT_FOUND` | 404 | 資源不存在 |
| `CONFLICT` | 409 | 資源衝突 (如用戶名已存在) |
| `FILE_TOO_LARGE` | 413 | 檔案超過大小限制 (最大 10MB) |
| `UNSUPPORTED_FORMAT` | 415 | 不支援的檔案格式 |
| `RATE_LIMITED` | 429 | 請求過於頻繁 |
| `INTERNAL_ERROR` | 500 | 伺服器內部錯誤 |
| `SERVICE_UNAVAILABLE` | 503 | 外部服務不可用 |
| `LDAP_CONNECTION_ERROR` | 503 | LDAP 服務連線失敗 |
| `OPENAI_API_ERROR` | 503 | OpenAI API 呼叫失敗 |

---

## 6. 安全性考量 (Security Considerations)

### 6.1 傳輸層安全 (TLS)

- 所有 API 端點強制使用 HTTPS (TLS 1.2+)
- 生產環境禁用 HTTP 連線

### 6.2 HTTP 安全 Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-XSS-Protection: 1; mode=block
```

### 6.3 速率限制 (Rate Limiting)

| 端點類別 | 限制 | 時間視窗 |
|:---------|:-----|:---------|
| 認證端點 (`/auth/*`) | 10 次 | 1 分鐘 |
| OCR 處理 (`/ocr/process`) | 30 次 | 1 分鐘 |
| 一般 API | 100 次 | 1 分鐘 |

**超出限制回應:**

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "請求過於頻繁，請稍後再試",
    "details": {
      "retry_after": 45
    }
  }
}
```

### 6.4 檔案上傳安全

| 控制項 | 設定 |
|:-------|:-----|
| **檔案大小限制** | 最大 10MB |
| **允許格式** | image/jpeg, image/png, image/webp, application/pdf |
| **儲存隔離** | 檔案儲存於 MinIO，與應用程式隔離 |
| **檔案名稱清理** | 移除特殊字元，防止路徑遍歷攻擊 |

### 6.5 密碼安全

- 密碼使用 bcrypt 雜湊儲存
- 最小密碼長度: 8 字元
- 帳號鎖定: 連續失敗 5 次後鎖定 15 分鐘

---

## 7. API 端點詳述 (API Endpoint Definitions)

### 7.1 認證模組 (Auth Module)

#### `POST /api/v1/auth/login` - 本地帳號登入

**描述:** 使用本地帳號密碼進行身份驗證

**認證:** 不需要

**請求體:**

```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**成功回應 (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john.doe",
    "display_name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "auth_type": "local"
  }
}
```

**錯誤回應:**

| 狀態碼 | 錯誤碼 | 說明 |
|:-------|:-------|:-----|
| 400 | VALIDATION_ERROR | 缺少必要欄位 |
| 401 | UNAUTHORIZED | 帳號或密碼錯誤 |
| 429 | RATE_LIMITED | 登入嘗試過於頻繁 |

---

#### `POST /api/v1/auth/login/ldap` - LDAP 登入

**描述:** 使用企業 LDAP/AD 帳號進行身份驗證

**認證:** 不需要

**請求體:**

```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**成功回應 (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "507f1f77bcf86cd799439012",
    "username": "jdoe",
    "display_name": "John Doe",
    "email": "jdoe@company.com",
    "role": "user",
    "auth_type": "ldap",
    "ldap_dn": "CN=John Doe,OU=Users,DC=company,DC=com"
  }
}
```

**錯誤回應:**

| 狀態碼 | 錯誤碼 | 說明 |
|:-------|:-------|:-----|
| 401 | UNAUTHORIZED | LDAP 驗證失敗 |
| 503 | LDAP_CONNECTION_ERROR | LDAP 服務不可用 |

---

#### `POST /api/v1/auth/logout` - 登出

**描述:** 登出當前使用者 (清除 Session)

**認證:** 必要

**成功回應 (204 No Content):** 無內容

---

#### `GET /api/v1/auth/me` - 取得當前使用者資訊

**描述:** 取得當前已認證使用者的詳細資訊

**認證:** 必要

**成功回應 (200 OK):**

```json
{
  "id": "507f1f77bcf86cd799439011",
  "username": "john.doe",
  "display_name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "auth_type": "local",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-12-24T08:00:00Z",
  "usage": {
    "monthly_count": 45,
    "last_reset": "2025-12-01T00:00:00Z"
  }
}
```

---

### 7.2 OCR 模組 (OCR Module)

#### `POST /api/v1/ocr/upload` - 上傳檔案

**描述:** 上傳圖片或 PDF 檔案進行 OCR 處理

**認證:** 必要

**Content-Type:** `multipart/form-data`

**請求參數:**

| 參數 | 類型 | 必要 | 說明 |
|:-----|:-----|:-----|:-----|
| `file` | file | 是 | 上傳的檔案 |

**檔案限制:**
- 最大檔案大小: 10MB
- 支援格式: JPEG, PNG, WEBP, PDF
- PDF 最大頁數: 10 頁

**成功回應 (201 Created):**

```json
{
  "task_id": "507f1f77bcf86cd799439013",
  "original_filename": "invoice.png",
  "file_type": "image",
  "file_size": 256000,
  "page_count": 1,
  "status": "uploaded",
  "created_at": "2025-12-24T10:30:00Z"
}
```

**錯誤回應:**

| 狀態碼 | 錯誤碼 | 說明 |
|:-------|:-------|:-----|
| 413 | FILE_TOO_LARGE | 檔案超過 10MB |
| 415 | UNSUPPORTED_FORMAT | 檔案格式不支援 |

---

#### `POST /api/v1/ocr/process/{task_id}` - 執行 OCR 辨識

**描述:** 對已上傳的檔案執行 OCR 辨識

**認證:** 必要

**路徑參數:**

| 參數 | 類型 | 說明 |
|:-----|:-----|:-----|
| `task_id` | string | OCR 任務 ID |

**成功回應 (202 Accepted):**

```json
{
  "task_id": "507f1f77bcf86cd799439013",
  "status": "processing",
  "message": "OCR 處理已開始，請透過 WebSocket 追蹤進度"
}
```

**錯誤回應:**

| 狀態碼 | 錯誤碼 | 說明 |
|:-------|:-------|:-----|
| 404 | NOT_FOUND | 任務不存在 |
| 409 | CONFLICT | 任務已在處理中或已完成 |

---

#### `GET /api/v1/ocr/tasks` - 取得 OCR 任務列表

**描述:** 取得使用者的 OCR 任務列表 (支援分頁)

**認證:** 必要

**查詢參數:**

| 參數 | 類型 | 預設值 | 說明 |
|:-----|:-----|:-------|:-----|
| `page` | integer | 1 | 頁碼 |
| `page_size` | integer | 20 | 每頁筆數 |
| `status` | string | - | 過濾狀態 (uploaded/processing/completed/failed) |
| `sort_by` | string | -created_at | 排序欄位 |

**成功回應 (200 OK):**

```json
{
  "data": [
    {
      "task_id": "507f1f77bcf86cd799439013",
      "original_filename": "invoice.png",
      "file_type": "image",
      "status": "completed",
      "progress": 100,
      "created_at": "2025-12-24T10:30:00Z",
      "updated_at": "2025-12-24T10:30:05Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

#### `GET /api/v1/ocr/result/{task_id}` - 取得 OCR 結果

**描述:** 取得指定任務的 OCR 辨識結果

**認證:** 必要

**路徑參數:**

| 參數 | 類型 | 說明 |
|:-----|:-----|:-----|
| `task_id` | string | OCR 任務 ID |

**成功回應 (200 OK):**

```json
{
  "task_id": "507f1f77bcf86cd799439013",
  "status": "completed",
  "results": [
    {
      "page_number": 1,
      "extracted_text": "發票號碼: AB-12345678\n日期: 2025/12/24\n...",
      "structured_data": {
        "type": "發票",
        "fields": [
          { "key": "發票號碼", "value": "AB-12345678", "confidence": 0.98 },
          { "key": "日期", "value": "2025/12/24", "confidence": 0.95 }
        ],
        "tables": []
      },
      "confidence": 0.92
    }
  ],
  "created_at": "2025-12-24T10:30:00Z",
  "completed_at": "2025-12-24T10:30:05Z"
}
```

---

#### `PUT /api/v1/ocr/result/{task_id}` - 編輯 OCR 結果

**描述:** 手動編輯 OCR 辨識結果

**認證:** 必要

**請求體:**

```json
{
  "results": [
    {
      "page_number": 1,
      "extracted_text": "修正後的文字內容...",
      "structured_data": {
        "type": "發票",
        "fields": [
          { "key": "發票號碼", "value": "AB-12345678", "confidence": 1.0 }
        ]
      }
    }
  ]
}
```

**成功回應 (200 OK):** 返回更新後的完整結果

---

#### `DELETE /api/v1/ocr/result/{task_id}` - 刪除 OCR 結果

**描述:** 刪除指定的 OCR 任務及其結果

**認證:** 必要

**成功回應 (204 No Content):** 無內容

---

### 7.3 匯出模組 (Export Module)

#### `GET /api/v1/export/{task_id}` - 匯出辨識結果

**描述:** 將 OCR 辨識結果匯出為指定格式

**認證:** 必要

**路徑參數:**

| 參數 | 類型 | 說明 |
|:-----|:-----|:-----|
| `task_id` | string | OCR 任務 ID |

**查詢參數:**

| 參數 | 類型 | 預設值 | 可選值 | 說明 |
|:-----|:-----|:-------|:-------|:-----|
| `format` | string | json | json, csv, xlsx | 匯出格式 |

**成功回應:**

- **JSON (200 OK):** `Content-Type: application/json`
- **CSV (200 OK):** `Content-Type: text/csv; charset=utf-8-sig`
- **XLSX (200 OK):** `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**回應 Headers:**

```
Content-Disposition: attachment; filename="ocr_result_507f1f77bcf86cd799439013.xlsx"
```

---

### 7.4 管理員模組 (Admin Module)

#### `GET /api/v1/admin/users` - 取得使用者列表

**描述:** 取得系統所有使用者列表 (僅限管理員)

**認證:** 必要 (admin 角色)

**查詢參數:**

| 參數 | 類型 | 預設值 | 說明 |
|:-----|:-----|:-------|:-----|
| `page` | integer | 1 | 頁碼 |
| `page_size` | integer | 20 | 每頁筆數 |
| `auth_type` | string | - | 過濾認證類型 (local/ldap) |
| `is_active` | boolean | - | 過濾啟用狀態 |

**成功回應 (200 OK):**

```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439011",
      "username": "john.doe",
      "display_name": "John Doe",
      "email": "john@example.com",
      "auth_type": "local",
      "role": "user",
      "is_active": true,
      "created_at": "2025-01-15T10:30:00Z",
      "last_login": "2025-12-24T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 100,
    "total_pages": 5
  }
}
```

---

#### `POST /api/v1/admin/users` - 新增使用者

**描述:** 新增本地使用者帳號 (僅限管理員)

**認證:** 必要 (admin 角色)

**請求體:**

```json
{
  "username": "string (required, unique)",
  "password": "string (required, min 8 chars)",
  "display_name": "string (required)",
  "email": "string (optional, email format)",
  "role": "user | admin (default: user)"
}
```

**成功回應 (201 Created):** 返回創建的使用者物件

---

#### `PUT /api/v1/admin/users/{user_id}` - 更新使用者

**描述:** 更新使用者資訊 (僅限管理員)

**認證:** 必要 (admin 角色)

**請求體:**

```json
{
  "display_name": "string (optional)",
  "email": "string (optional)",
  "role": "user | admin (optional)",
  "is_active": "boolean (optional)"
}
```

**成功回應 (200 OK):** 返回更新後的使用者物件

---

#### `DELETE /api/v1/admin/users/{user_id}` - 停用使用者

**描述:** 停用指定使用者 (軟刪除)

**認證:** 必要 (admin 角色)

**成功回應 (204 No Content):** 無內容

---

### 7.5 歷史紀錄模組 (History Module)

#### `GET /api/v1/history` - 取得辨識歷史

**描述:** 取得使用者的 OCR 辨識歷史紀錄

**認證:** 必要

**查詢參數:**

| 參數 | 類型 | 預設值 | 說明 |
|:-----|:-----|:-------|:-----|
| `page` | integer | 1 | 頁碼 |
| `page_size` | integer | 20 | 每頁筆數 |
| `created_after` | string | - | 起始日期 (ISO 8601) |
| `created_before` | string | - | 結束日期 (ISO 8601) |

**成功回應 (200 OK):** 同 `/api/v1/ocr/tasks` 回應格式

---

#### `DELETE /api/v1/history/{task_id}` - 刪除歷史紀錄

**描述:** 刪除指定的歷史紀錄

**認證:** 必要

**成功回應 (204 No Content):** 無內容

---

## 8. 資料模型/Schema 定義 (Data Models / Schema Definitions)

### 8.1 `User` - 使用者

```json
{
  "id": "string (ObjectId)",
  "username": "string (unique)",
  "display_name": "string",
  "email": "string | null",
  "auth_type": "local | ldap",
  "ldap_dn": "string | null",
  "role": "admin | user",
  "is_active": "boolean",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "last_login": "string (ISO 8601) | null",
  "usage": {
    "monthly_count": "integer",
    "last_reset": "string (ISO 8601)"
  }
}
```

### 8.2 `UserCreate` - 新增使用者請求

```json
{
  "username": "string (required, 3-50 chars, alphanumeric + underscore)",
  "password": "string (required, min 8 chars)",
  "display_name": "string (required, 1-100 chars)",
  "email": "string (optional, valid email format)",
  "role": "admin | user (default: user)"
}
```

### 8.3 `OCRTask` - OCR 任務

```json
{
  "task_id": "string (ObjectId)",
  "user_id": "string (ObjectId)",
  "original_filename": "string",
  "file_type": "image | pdf",
  "file_size": "integer (bytes)",
  "page_count": "integer",
  "status": "uploaded | processing | completed | failed",
  "progress": "integer (0-100)",
  "error_message": "string | null",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### 8.4 `OCRResult` - OCR 結果

```json
{
  "result_id": "string (ObjectId)",
  "task_id": "string (ObjectId)",
  "page_number": "integer (1-based)",
  "extracted_text": "string",
  "structured_data": {
    "type": "string (文件類型推測)",
    "fields": [
      {
        "key": "string",
        "value": "string",
        "confidence": "number (0-1)"
      }
    ],
    "tables": [
      {
        "headers": ["string"],
        "rows": [["string"]]
      }
    ]
  },
  "confidence": "number (0-1)",
  "created_at": "string (ISO 8601)"
}
```

### 8.5 `LoginRequest` - 登入請求

```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

### 8.6 `LoginResponse` - 登入回應

```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer",
  "expires_in": "integer (seconds)",
  "user": "User"
}
```

### 8.7 `Pagination` - 分頁資訊

```json
{
  "page": "integer",
  "page_size": "integer",
  "total_items": "integer",
  "total_pages": "integer",
  "has_next": "boolean",
  "has_prev": "boolean"
}
```

### 8.8 `Error` - 錯誤回應

```json
{
  "error": {
    "code": "string (ERROR_CODE)",
    "message": "string",
    "details": "object | null",
    "request_id": "string (UUID)"
  }
}
```

---

## 9. WebSocket 規範 (WebSocket Specification)

### 9.1 連線端點

**URL:** `wss://api.smartocr.example.com/api/v1/ws/ocr-progress`

**認證:** 透過 Query Parameter 傳遞 Token

```
wss://api.smartocr.example.com/api/v1/ws/ocr-progress?token=YOUR_JWT_TOKEN&task_id=TASK_ID
```

### 9.2 訊息格式

#### 進度更新 (Server → Client)

```json
{
  "type": "progress",
  "task_id": "507f1f77bcf86cd799439013",
  "progress": 50,
  "status": "processing",
  "message": "正在處理第 1 頁...",
  "timestamp": "2025-12-24T10:30:02Z"
}
```

#### 完成通知 (Server → Client)

```json
{
  "type": "completed",
  "task_id": "507f1f77bcf86cd799439013",
  "progress": 100,
  "status": "completed",
  "message": "OCR 處理完成",
  "timestamp": "2025-12-24T10:30:05Z"
}
```

#### 錯誤通知 (Server → Client)

```json
{
  "type": "error",
  "task_id": "507f1f77bcf86cd799439013",
  "status": "failed",
  "error_code": "OPENAI_API_ERROR",
  "message": "OpenAI API 呼叫失敗",
  "timestamp": "2025-12-24T10:30:05Z"
}
```

### 9.3 心跳機制

- **Ping 間隔:** 30 秒
- **Pong 超時:** 10 秒
- 客戶端應實作自動重連機制

### 9.4 前端使用範例 (TypeScript)

```typescript
import { useEffect, useState } from 'react';

export function useOCRProgress(taskId: string, token: string) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const wsUrl = `wss://api.smartocr.example.com/api/v1/ws/ocr-progress?token=${token}&task_id=${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
      setStatus(data.status);

      if (data.type === 'error') {
        setError(data.message);
      }
    };

    ws.onerror = () => {
      setError('WebSocket 連線錯誤');
    };

    ws.onclose = () => {
      // 實作重連邏輯
    };

    return () => ws.close();
  }, [taskId, token]);

  return { progress, status, error };
}
```

---

## 10. API 生命週期與版本控制 (API Lifecycle and Versioning)

### 10.1 API 生命週期階段 (API Lifecycle Stages)

| 階段 | 說明 |
|:-----|:-----|
| **設計 (Design)** | API 正在設計和審查中，尚未實現 |
| **開發 (Development)** | 僅供內部開發和測試使用，API 極不穩定 |
| **Beta** | API 相對穩定，開放給用戶測試，應盡量避免破壞性變更 |
| **GA (General Availability)** | 官方穩定版本，承諾遵守版本控制和棄用策略 |
| **已棄用 (Deprecated)** | 不再推薦使用，將在未來被移除 |
| **已停用 (Decommissioned)** | API 已被移除，無法再訪問 |

### 10.2 版本控制策略 (Versioning Strategy)

- **策略:** URL 路徑版本控制 (e.g., `/api/v1/...`)
- **主版本號:** 當有破壞性變更時遞增 (v1 → v2)

#### 向後兼容變更 (不增加版本號)

- 增加新的 API 端點
- 在請求中增加新的可選參數
- 在回應中增加新的欄位

#### 破壞性變更 (必須增加主版本號)

- 刪除或重命名欄位/端點
- 修改現有欄位型別
- 增加新的必選參數
- 變更認證機制

### 10.3 API 棄用策略 (Deprecation Policy)

當一個 API 版本需要被棄用時：

1. **提前通知:** 至少提前 6 個月通知
2. **溝通管道:**
   - 文檔標註 (Deprecated 標籤)
   - HTTP Header: `Deprecation: true`, `Sunset: <date>`
   - 客戶郵件通知
3. **遷移支援:** 提供詳細的遷移指南

---

## 11. 附錄 (Appendix)

### 11.1 完整請求/回應範例

#### 範例 1: 完整 OCR 流程

**Step 1: 登入**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/auth/login \
  --header 'Content-Type: application/json' \
  --data '{
    "username": "demo",
    "password": "demo1234"
  }'
```

**回應:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "demo",
    "display_name": "Demo User",
    "role": "user"
  }
}
```

**Step 2: 上傳檔案**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/ocr/upload \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...' \
  --form 'file=@/path/to/invoice.png'
```

**回應:**

```json
{
  "task_id": "507f1f77bcf86cd799439013",
  "original_filename": "invoice.png",
  "file_type": "image",
  "file_size": 256000,
  "page_count": 1,
  "status": "uploaded",
  "created_at": "2025-12-24T10:30:00Z"
}
```

**Step 3: 執行 OCR (同時建立 WebSocket 連線)**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/ocr/process/507f1f77bcf86cd799439013 \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...'
```

**回應:**

```json
{
  "task_id": "507f1f77bcf86cd799439013",
  "status": "processing",
  "message": "OCR 處理已開始，請透過 WebSocket 追蹤進度"
}
```

**Step 4: 取得結果**

```bash
curl --request GET \
  --url http://localhost:8000/api/v1/ocr/result/507f1f77bcf86cd799439013 \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...'
```

**Step 5: 匯出 XLSX**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/v1/export/507f1f77bcf86cd799439013?format=xlsx' \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...' \
  --output result.xlsx
```

### 11.2 環境變數清單

| 變數名稱 | 說明 | 範例值 |
|:---------|:-----|:-------|
| `MONGODB_URL` | MongoDB 連線字串 | `mongodb://localhost:27017/ocr_saas` |
| `MINIO_ENDPOINT` | MinIO 端點 | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO Access Key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO Secret Key | `minioadmin` |
| `MINIO_BUCKET` | 預設 Bucket | `ocr-uploads` |
| `REDIS_URL` | Redis 連線字串 | `redis://localhost:6379` |
| `OPENAI_API_KEY` | OpenAI API Key | `sk-xxx` |
| `JWT_SECRET_KEY` | JWT 簽名密鑰 | (random string) |
| `JWT_ALGORITHM` | JWT 演算法 | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token 過期時間 (分鐘) | `1440` |

### 11.3 相關文件連結

- [架構設計文件](./smart_ocr_saas_architecture.md)
- [產品需求文件](./smart_ocr_saas_prd.md)
- [OpenAPI 規格](http://localhost:8000/api/v1/openapi.json) (FastAPI 自動生成)

---

**文件審核記錄 (Review History):**

| 日期 | 審核人 | 版本 | 變更摘要 |
|:-----|:-------|:-----|:---------|
| 2025-12-24 | 技術架構團隊 | v1.0.0 | 初稿建立，基於架構文件產出 |

---

**文件結束**
