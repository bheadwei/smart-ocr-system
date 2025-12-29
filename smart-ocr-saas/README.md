# Smart OCR SaaS

雲端智能文字辨識服務 - 基於 OpenAI Vision API 的企業級 OCR 解決方案

## 技術棧

- **前端**: Next.js 14 (App Router) + TailwindCSS + TypeScript
- **後端**: Python FastAPI
- **資料庫**: MongoDB
- **物件儲存**: MinIO (S3 相容)
- **快取**: Redis
- **AI 服務**: OpenAI Vision API (GPT-4V)

## 功能特點

- 本地帳號 + LDAP/AD 企業登入
- 圖片辨識 (JPG, PNG, WEBP, etc.)
- PDF 文件辨識 (最多 10 頁)
- WebSocket 即時處理進度
- 多格式匯出 (JSON, CSV, XLSX)
- 歷史紀錄管理

## 快速開始

### 1. 環境需求

- Docker & Docker Compose
- Node.js 20+ (本地開發)
- Python 3.11+ (本地開發)

### 2. 設定環境變數

```bash
# 複製環境變數範例檔
cp .env.example .env

# 編輯 .env 並填入 OpenAI API Key
```

### 3. 啟動服務 (Docker Compose)

```bash
# 開發模式 (支援熱更新)
docker-compose -f docker-compose.dev.yml up -d

# 生產模式
docker-compose up -d
```

### 4. 存取服務

- **前端**: http://localhost:3000
- **後端 API**: http://localhost:8000/api/v1/docs
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin)

## 本地開發

### Backend

```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 複製環境變數
cp .env.example .env

# 啟動開發伺服器
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# 安裝依賴
npm install

# 複製環境變數
cp .env.example .env.local

# 啟動開發伺服器
npm run dev
```

## 專案結構

```
smart-ocr-saas/
├── backend/                 # FastAPI 後端
│   ├── app/
│   │   ├── api/v1/routes/   # API 路由
│   │   ├── core/            # 核心功能 (安全、資料庫)
│   │   ├── models/          # Pydantic 模型
│   │   ├── repositories/    # 資料存取層
│   │   └── services/        # 業務邏輯
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # Next.js 前端
│   ├── app/                 # App Router 頁面
│   ├── components/          # React 元件
│   ├── hooks/               # Custom Hooks
│   ├── lib/                 # 工具函數
│   ├── stores/              # Zustand 狀態
│   └── types/               # TypeScript 型別
│
├── docs/                    # 文件
├── docker-compose.yml       # 生產環境配置
├── docker-compose.dev.yml   # 開發環境配置
└── README.md
```

## API 文件

啟動後端後，存取 Swagger UI：
- http://localhost:8000/api/v1/docs

## 相關文件

- [PRD 文件](./docs/smart_ocr_saas_prd.md)
- [架構設計文件](./docs/smart_ocr_saas_architecture.md)

## License

MIT
