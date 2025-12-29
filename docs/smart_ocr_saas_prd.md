# 專案簡報與產品需求文件 (Project Brief & PRD) - Smart OCR SaaS

---

**文件版本 (Document Version):** `v1.2`
**最後更新 (Last Updated):** `2025-12-24`
**主要作者 (Lead Author):** `產品團隊`
**審核者 (Reviewers):** `技術負責人`
**狀態 (Status):** `草稿 (Draft)`

---

## 目錄 (Table of Contents)

1.  [專案總覽 (Project Overview)](#第-1-部分專案總覽-project-overview)
2.  [商業目標 (Business Objectives) - 「為何做？」](#第-2-部分商業目標-business-objectives---為何做)
3.  [使用者故事與允收標準 (User Stories & UAT) - 「做什麼？」](#第-3-部分使用者故事與允收標準-user-stories--uat---做什麼)
4.  [範圍與限制 (Scope & Constraints)](#第-4-部分範圍與限制-scope--constraints)
5.  [技術架構概述 (Technical Architecture)](#第-5-部分技術架構概述-technical-architecture)
6.  [待辦問題與決策 (Open Questions & Decisions)](#第-6-部分待辦問題與決策-open-questions--decisions)

---

**目的**: 本文件旨在定義 Smart OCR SaaS 專案的「為何」與「為誰」，為整個專案設定最高層次的目標和邊界。它是所有後續設計、開發與測試工作的唯一事實來源 (Single Source of Truth)。

---

## 第 1 部分：專案總覽 (Project Overview)

| 區塊 | 內容 |
| :--- | :--- |
| **專案名稱** | Smart OCR SaaS - 雲端智能文字辨識服務 |
| **專案代號** | `smart-ocr-saas` |
| **狀態** | 規劃中 |
| **目標發布日期** | TBD |
| **核心技術棧** | **前端**: Next.js (React)<br>**後端**: Python FastAPI<br>**資料庫**: MongoDB<br>**AI 服務**: OpenAI Vision API |

---

## 第 2 部分：商業目標 (Business Objectives) - 「為何做？」

| 區塊 | 內容 |
| :--- | :--- |
| **1. 背景與痛點** | **現狀問題：**<br>- 現有本地 PaddleOCR 解決方案需要高額的本地運算資源（GPU/CPU）<br>- 部署和維護成本高，需要專業技術人員<br>- 無法彈性擴展，高峰期處理能力受限<br>- 中小企業難以負擔自建 OCR 系統的成本<br><br>**目標用戶痛點：**<br>- 需要快速將圖片/文件中的文字數位化<br>- 希望將辨識結果輸出為結構化格式 (Excel, CSV, JSON)<br>- 缺乏技術資源自行部署 OCR 系統 |
| **2. 策略契合度** | - 轉型為 SaaS 模式，降低用戶使用門檻<br>- 利用 OpenAI Vision API 的強大能力，減少本地維護成本<br>- 建立訂閱制收入模式，創造穩定現金流<br>- 擴展市場覆蓋範圍，服務更多中小企業客戶 |
| **3. 成功指標 (Success Metrics)** | - **主要指標**: MVP 完成後 30 天內獲得 100 位註冊用戶<br>- **次要指標**: 辨識準確率 > 95%<br>- **技術指標**: API 回應時間 < 5 秒 (單張圖片) |

---

## 第 3 部分：使用者故事與允收標準 (User Stories & UAT) - 「做什麼？」

### Epic 1: 使用者身份管理 (User Authentication)

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) |
| :--- | :--- | :--- |
| **US-101** | **As a** 使用者,<br>**I want to** 使用本地帳號密碼登入,<br>**so that** 我可以存取 OCR 服務。 | 1. 正確帳密可成功登入<br>2. 錯誤帳密顯示提示訊息<br>3. 密碼需符合安全性要求<br>4. 登入後導向儀表板 |
| **US-102** | **As a** 企業使用者,<br>**I want to** 使用公司 LDAP/AD 帳號登入,<br>**so that** 我可以使用企業單一登入存取服務。 | 1. 支援 LDAP/Active Directory 認證<br>2. 自動同步使用者基本資訊<br>3. 支援 LDAPS (SSL/TLS) 加密連線<br>4. 登入失敗顯示明確錯誤訊息 |
| **US-103** | **As a** 系統管理員,<br>**I want to** 管理本地使用者帳號,<br>**so that** 我可以控制誰能存取系統。 | 1. 可新增/編輯/停用本地帳號<br>2. 可設定帳號權限角色<br>3. 可重設使用者密碼 |
| **US-104** | **As a** 使用者,<br>**I want to** 查看我的 API 使用量,<br>**so that** 我可以管理我的用量配額。 | 1. 顯示當月已使用次數<br>2. 顯示剩餘配額<br>3. 配額不足時提醒 |

### Epic 2: 檔案上傳與 OCR 辨識 (File Upload & OCR)

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) |
| :--- | :--- | :--- |
| **US-201** | **As a** 使用者,<br>**I want to** 上傳圖片檔案,<br>**so that** 系統可以辨識圖片中的文字。 | 1. 支援 JPG, PNG, WEBP, GIF, BMP, TIFF 格式<br>2. 單檔上限 10MB<br>3. 顯示上傳進度 |
| **US-202** | **As a** 使用者,<br>**I want to** 上傳 PDF 文件,<br>**so that** 系統可以辨識 PDF 中的文字。 | 1. 支援 PDF 格式上傳<br>2. 自動將 PDF 頁面轉換為圖片進行辨識<br>3. 支援多頁 PDF (上限 10 頁)<br>4. 單檔上限 20MB |
| **US-203** | **As a** 使用者,<br>**I want to** 一次上傳多個檔案,<br>**so that** 我可以批量處理文件。 | 1. 支援拖放多檔上傳<br>2. 最多同時處理 10 個檔案<br>3. 顯示每個檔案處理狀態 |
| **US-204** | **As a** 使用者,<br>**I want to** 即時查看處理進度,<br>**so that** 我可以知道辨識還需要多久。 | 1. WebSocket 即時推送處理狀態<br>2. 顯示處理進度百分比<br>3. 處理完成即時通知 |
| **US-205** | **As a** 使用者,<br>**I want to** 查看 OCR 辨識結果,<br>**so that** 我可以確認辨識內容是否正確。 | 1. 顯示辨識出的文字內容<br>2. 支援編輯修正辨識結果<br>3. 顯示辨識信心度 |

### Epic 3: 結果匯出 (Export)

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) |
| :--- | :--- | :--- |
| **US-301** | **As a** 使用者,<br>**I want to** 將辨識結果匯出為 JSON,<br>**so that** 我可以整合到其他系統。 | 1. 點擊匯出按鈕下載 JSON<br>2. 格式符合標準 JSON 規範<br>3. 包含完整辨識資訊 |
| **US-302** | **As a** 使用者,<br>**I want to** 將辨識結果匯出為 Excel (XLSX),<br>**so that** 我可以用試算表軟體編輯。 | 1. 正確匯出為 .xlsx 格式<br>2. 支援中文字元不亂碼<br>3. 欄位結構清晰 |
| **US-303** | **As a** 使用者,<br>**I want to** 將辨識結果匯出為 CSV,<br>**so that** 我可以匯入其他系統。 | 1. 使用 UTF-8 編碼<br>2. 正確處理逗號與引號<br>3. 支援中文字元 |

### Epic 4: 歷史紀錄管理 (History Management)

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) |
| :--- | :--- | :--- |
| **US-401** | **As a** 使用者,<br>**I want to** 查看我的辨識歷史紀錄,<br>**so that** 我可以重新下載之前的結果。 | 1. 依時間排序顯示歷史<br>2. 可搜尋/篩選紀錄<br>3. 可重新下載結果 |
| **US-402** | **As a** 使用者,<br>**I want to** 刪除歷史紀錄,<br>**so that** 我可以管理我的資料。 | 1. 可單筆刪除<br>2. 可批量刪除<br>3. 刪除前確認提示 |

---

## 第 4 部分：範圍與限制 (Scope & Constraints)

| 區塊 | 內容 |
| :--- | :--- |
| **功能性需求 (In Scope - MVP)** | - 本地帳號登入系統<br>- LDAP/AD 企業登入整合<br>- 使用者帳號管理 (管理員功能)<br>- 單張/批量圖片上傳<br>- PDF 文件上傳與辨識<br>- OpenAI Vision API 串接辨識<br>- WebSocket 即時進度通知<br>- 辨識結果預覽與編輯<br>- 多格式匯出 (JSON, CSV, XLSX)<br>- 使用量統計儀表板<br>- 辨識歷史紀錄管理 |
| **非功能性需求 (NFRs)** | - **性能**: 單張圖片辨識回應 < 5 秒<br>- **安全性**: 所有密碼使用 bcrypt 加密，API 金鑰加密存儲，LDAP 支援 SSL/TLS<br>- **可用性**: 支援 RWD 響應式設計<br>- **可靠性**: API 服務可用率 > 99%<br>- **資料保護**: 使用者資料加密傳輸 (HTTPS)<br>- **即時性**: WebSocket 連線穩定，斷線自動重連 |
| **不做什麼 (Out of Scope - V1)** | - 第三方登入 (Google/Facebook OAuth)<br>- Email 註冊功能<br>- 付費訂閱系統 (Stripe 串接)<br>- 多語言 OCR (僅支援中英文)<br>- 即時多人協作功能<br>- 手機 App |
| **假設與依賴** | - **假設**: 使用者具備穩定網路連線<br>- **假設**: 使用者上傳的檔案品質足以辨識<br>- **假設**: 企業用戶有可用的 LDAP/AD 伺服器<br>- **依賴**: OpenAI Vision API 服務可用性<br>- **依賴**: MongoDB 資料庫服務<br>- **依賴**: MinIO 物件儲存服務<br>- **依賴**: PDF 轉圖片處理函式庫 (pdf2image/PyMuPDF) |

---

## 第 5 部分：技術架構概述 (Technical Architecture)

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS + WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Pages/     │  │  Components/ │  │   API Client │           │
│  │   Routes     │  │  UI Library  │  │   + WS Hook  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                         Vercel / Self-hosted                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API + WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  │   Auth     │ │   OCR      │ │   Export   │ │ WebSocket  │    │
│  │  (Local +  │ │  Service   │ │   Service  │ │  Manager   │    │
│  │  LDAP/AD)  │ │            │ │            │ │            │    │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │
│                      Railway / Render / Self-hosted              │
└───────┬─────────────┬─────────────┬─────────────┬───────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────────┐
│  MongoDB    │ │  OpenAI   │ │   MinIO   │ │   LDAP/AD         │
│             │ │  Vision   │ │  (Object  │ │   Server          │
│             │ │  API      │ │  Storage) │ │   (Enterprise)    │
└─────────────┘ └───────────┘ └───────────┘ └───────────────────┘
```

### 技術選型說明

| 層級 | 技術選擇 | 選擇原因 |
| :--- | :--- | :--- |
| **前端框架** | Next.js 14+ (App Router) | - React 生態系成熟<br>- 內建 SSR/SSG 支援<br>- 優異的 DX 開發體驗<br>- 內建 WebSocket 支援 |
| **後端框架** | Python FastAPI | - 高性能非同步框架<br>- 自動生成 OpenAPI 文件<br>- 原生 WebSocket 支援<br>- Python AI 生態系整合 |
| **資料庫** | MongoDB | - 文件型資料庫適合非結構化資料<br>- Schema 彈性高<br>- 易於水平擴展 |
| **物件儲存** | MinIO | - S3 相容 API<br>- 可自建部署，資料主權可控<br>- 高性能分散式儲存<br>- 支援大檔案上傳 |
| **AI 服務** | OpenAI Vision API | - GPT-4V 多模態能力強大<br>- 無需本地 GPU 資源<br>- 支援複雜版面理解<br>- 按量計費彈性高 |
| **認證** | JWT + HTTP-only Cookie | - 無狀態驗證<br>- 前後端分離友好<br>- 安全性較高 |
| **企業認證** | LDAP/Active Directory | - 企業單一登入整合<br>- 支援 LDAPS 加密<br>- 使用 python-ldap 函式庫 |
| **即時通訊** | WebSocket | - 雙向即時通訊<br>- 處理進度即時推送<br>- 使用 FastAPI WebSocket |
| **PDF 處理** | PyMuPDF (fitz) | - 高效能 PDF 解析<br>- 支援 PDF 轉圖片<br>- 純 Python 實作 |

### API 端點規劃 (初版)

```
# 認證相關
POST   /api/v1/auth/login              # 本地帳號登入
POST   /api/v1/auth/login/ldap         # LDAP/AD 登入
POST   /api/v1/auth/logout             # 使用者登出
GET    /api/v1/auth/me                 # 取得當前使用者資訊

# 使用者管理 (管理員)
GET    /api/v1/admin/users             # 取得使用者列表
POST   /api/v1/admin/users             # 新增本地使用者
PUT    /api/v1/admin/users/{id}        # 編輯使用者
DELETE /api/v1/admin/users/{id}        # 停用使用者

# OCR 處理
POST   /api/v1/ocr/upload              # 上傳檔案 (圖片/PDF)
POST   /api/v1/ocr/process/{id}        # 執行 OCR 辨識
GET    /api/v1/ocr/result/{id}         # 取得辨識結果
PUT    /api/v1/ocr/result/{id}         # 編輯辨識結果
DELETE /api/v1/ocr/result/{id}         # 刪除辨識結果

# 匯出
GET    /api/v1/export/{id}             # 匯出辨識結果 (支援 format=json|csv|xlsx)

# 歷史紀錄
GET    /api/v1/history                 # 取得歷史紀錄列表
DELETE /api/v1/history/{id}            # 刪除歷史紀錄

# 使用量
GET    /api/v1/usage                   # 取得使用量統計

# WebSocket
WS     /api/v1/ws/ocr-progress         # OCR 處理進度即時推送
```

### 資料庫 Schema 設計 (MongoDB Collections)

```javascript
// users collection
{
  _id: ObjectId,
  username: String,           // 登入帳號
  password_hash: String,      // 本地帳號密碼 (LDAP 用戶為 null)
  display_name: String,       // 顯示名稱
  email: String,              // 電子郵件 (可選)
  auth_type: String,          // "local" | "ldap"
  ldap_dn: String,            // LDAP Distinguished Name (LDAP 用戶)
  role: String,               // "admin" | "user"
  is_active: Boolean,         // 帳號是否啟用
  created_at: DateTime,
  updated_at: DateTime,
  last_login: DateTime,
  usage: {
    monthly_count: Number,
    last_reset: DateTime
  }
}

// ocr_tasks collection
{
  _id: ObjectId,
  user_id: ObjectId,
  original_filename: String,
  file_type: String,          // "image" | "pdf"
  file_size: Number,          // 檔案大小 (bytes)
  minio_bucket: String,       // MinIO bucket 名稱
  minio_object_key: String,   // MinIO 物件 key
  page_count: Number,         // PDF 頁數 (圖片為 1)
  status: String,             // "uploaded" | "processing" | "completed" | "failed"
  progress: Number,           // 處理進度 0-100
  error_message: String,      // 錯誤訊息 (如有)
  created_at: DateTime,
  updated_at: DateTime
}

// ocr_results collection
{
  _id: ObjectId,
  task_id: ObjectId,          // 關聯的 ocr_task
  user_id: ObjectId,
  page_number: Number,        // 頁碼 (PDF 多頁)
  extracted_text: String,     // 辨識出的文字
  structured_data: Object,    // OpenAI 解析的結構化資料
  confidence: Number,         // 辨識信心度
  created_at: DateTime,
  updated_at: DateTime
}

// ldap_config collection (系統設定)
{
  _id: ObjectId,
  server_url: String,         // ldap://ldap.example.com:389
  use_ssl: Boolean,           // 是否使用 LDAPS
  base_dn: String,            // 搜尋 base DN
  bind_dn: String,            // 綁定 DN
  bind_password_encrypted: String,  // 加密的綁定密碼
  user_search_filter: String, // 使用者搜尋 filter
  username_attribute: String, // 帳號屬性 (如 sAMAccountName)
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

---

## 第 6 部分：待辦問題與決策 (Open Questions & Decisions)

| 問題/決策 ID | 描述 | 狀態 | 備註 |
| :--- | :--- | :--- | :--- |
| **D-008** | 次數限制暫緩實作 | 已決定 | 先完成功能，測試後估算成本再設定 |
| **D-009** | LDAP 失敗時允許本地帳號備援登入 | 已決定 | 確保服務可用性 |
| **D-010** | PDF 單檔頁數上限設定為 10 頁 | 已決定 | 控制單次處理量 |
| **D-001** | 決定採用 MongoDB 作為主要資料庫 | 已決定 | 文件型資料庫適合 OCR 結果儲存 |
| **D-002** | 決定使用 OpenAI Vision API 取代本地 PaddleOCR | 已決定 | 降低本地運算成本 |
| **D-003** | 前後端分離架構：Next.js + FastAPI | 已決定 | 符合現代 SaaS 開發最佳實踐 |
| **D-004** | 決定使用 MinIO 作為物件儲存方案 | 已決定 | S3 相容、可自建部署、資料主權可控 |
| **D-005** | 決定使用 WebSocket 實現即時進度通知 | 已決定 | FastAPI 原生支援，使用者體驗佳 |
| **D-006** | 決定支援 PDF 文件上傳與辨識 | 已決定 | 使用 PyMuPDF 轉換為圖片後辨識 |
| **D-007** | 決定採用本地帳號 + LDAP/AD 雙認證模式 | 已決定 | 移除 Email 註冊，支援企業單一登入 |

---

## 附錄：專案里程碑 (Milestones)

### Phase 1: 基礎架構
- [ ] 專案初始化與環境設定 (Next.js + FastAPI + MongoDB + MinIO)
- [ ] Docker Compose 開發環境配置
- [ ] 基礎 API 框架與路由設計
- [ ] MinIO 儲存服務整合

### Phase 2: 認證系統
- [ ] 本地帳號登入系統
- [ ] JWT Token 機制
- [ ] LDAP/AD 認證整合
- [ ] 使用者管理介面 (管理員)

### Phase 3: 核心 OCR 功能
- [ ] 圖片上傳功能
- [ ] PDF 上傳與頁面轉換
- [ ] OpenAI Vision API 串接
- [ ] WebSocket 即時進度推送
- [ ] 辨識結果展示與編輯

### Phase 4: 匯出與歷史
- [ ] JSON/CSV/XLSX 多格式匯出
- [ ] 歷史紀錄管理
- [ ] 使用量統計儀表板
- [ ] 批量檔案處理

### Phase 5: 優化與上線
- [ ] 效能優化
- [ ] UI/UX 改進
- [ ] 錯誤處理強化
- [ ] 監控與日誌系統
- [ ] 部署文件與上線準備

---

**文件結束**
