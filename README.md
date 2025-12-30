# Smart OCR System

**企業級中文 OCR 智能辨識系統**

基於 PaddleOCR 引擎的高性能文字辨識解決方案，支援批量處理與多格式匯出。

本專案包含兩個主要模組：
- **smart-ocr-system** (CLI) - 本地命令列 OCR 工具，基於 PaddleOCR
- **smart-ocr-saas** (Web) - 雲端 SaaS 服務，基於 OpenAI Vision API

---

## 功能特色

### CLI 工具 (PaddleOCR)

- **中文優化** - 使用 PaddleOCR 引擎，針對繁體/簡體中文辨識優化
- **批量處理** - 支援資料夾批量處理，遞迴掃描子目錄
- **多格式匯出** - 支援 TXT、JSON、CSV、XLSX 多種格式匯出
- **命令列介面** - 簡潔的 CLI 介面，易於整合自動化流程
- **GPU 加速** - 支援 NVIDIA GPU 加速處理

### SaaS 服務 (OpenAI Vision)

- **雲端部署** - Docker 一鍵部署，支援企業內部署
- **Web 介面** - 現代化 Next.js 前端，拖拽上傳
- **PDF 支援** - 支援 PDF 文件辨識（最多 10 頁）
- **即時進度** - WebSocket 即時處理進度推送
- **企業認證** - 支援本地帳號 + LDAP/AD 登入

---

## 系統需求

- Python 3.10+
- PaddlePaddle 2.6.2
- PaddleOCR 2.9.1

---

## 安裝教學

### 方法一：CPU 版本（推薦新手）

```bash
# 複製專案
git clone https://github.com/bheadwei/smart-ocr-system.git
cd smart-ocr-system

# 建立虛擬環境 (Python 3.10)
uv venv --python 3.10

# 啟動虛擬環境
# Windows (CMD)
.venv\Scripts\activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

# 安裝 CPU 版本
uv pip install paddlepaddle==2.6.2 paddleocr==2.9.1

# 安裝專案
uv pip install -e .
```

### 方法二：GPU 版本（NVIDIA 顯卡加速）

```bash
# 複製專案
git clone https://github.com/bheadwei/smart-ocr-system.git
cd smart-ocr-system

# 建立虛擬環境
uv venv --python 3.10
.venv\Scripts\activate  # Windows

# 安裝 GPU 版本 (CUDA 11.8/12.x)
uv pip install paddlepaddle-gpu==2.6.2 paddleocr==2.9.1

# 安裝 cuDNN（Windows 必須）
uv pip install nvidia-cudnn-cu11==8.9.5.29

# 安裝專案
uv pip install -e .
```

> **注意**：GPU 版本需要 NVIDIA 顯卡及 CUDA 驅動程式。程式會自動設定 cuDNN 路徑。

### 方法三：使用 pip

```bash
# 建立虛擬環境
python -m venv .venv
.venv\Scripts\activate  # Windows

# CPU 版本
pip install paddlepaddle==2.6.2 paddleocr==2.9.1

# 或 GPU 版本
pip install paddlepaddle-gpu==2.6.2 paddleocr==2.9.1 nvidia-cudnn-cu11==8.9.5.29

# 安裝專案
pip install -e .
```

---

## 操作說明

### 命令列介面 (CLI)

#### 基本用法

```bash
# 查看說明
smart-ocr --help

# 查看版本
smart-ocr --version

# 查看目前設定
smart-ocr config --show
```

#### 處理單一圖片

```bash
# 處理單一圖片（結果直接顯示在終端機）
smart-ocr process 圖片.png

# 處理圖片並輸出到檔案
smart-ocr process 圖片.png -o 結果.txt
```

#### 批量處理資料夾

```bash
# 處理資料夾內所有圖片
smart-ocr process ./文件資料夾/

# 遞迴處理（包含子資料夾）
smart-ocr process ./文件資料夾/ --recursive
smart-ocr process ./文件資料夾/ -r  # 簡寫
```

#### 匯出不同格式

```bash
# 匯出為純文字 (預設)
smart-ocr process 圖片.png -o 結果.txt -f txt

# 匯出為 JSON（含信心分數和座標）
smart-ocr process 圖片.png -o 結果.json -f json

# 匯出為 CSV（適合 Excel 分析）
smart-ocr process ./文件/ -o 結果.csv -f csv
```

#### 進階選項

```bash
# 使用 GPU 加速（需安裝 paddlepaddle-gpu）
smart-ocr process 圖片.png --gpu

# 處理英文文件
smart-ocr process document.png --lang en

# 靜默模式（不顯示處理過程）
smart-ocr process 圖片.png -q
smart-ocr process 圖片.png --quiet

# 組合使用
smart-ocr process ./文件/ -r -o 結果.json -f json --gpu
```

### CLI 參數一覽表

| 參數            | 簡寫   | 說明                           | 預設值             |
| --------------- | ------ | ------------------------------ | ------------------ |
| `--output`    | `-o` | 輸出檔案路徑                   | 無（顯示在終端機） |
| `--format`    | `-f` | 輸出格式：txt, json, csv, xlsx | txt                |
| `--lang`      | `-l` | 語言：ch（中文）, en（英文）   | ch                 |
| `--gpu`       | -      | 啟用 GPU 加速                  | 停用               |
| `--recursive` | `-r` | 遞迴處理子資料夾               | 停用               |
| `--quiet`     | `-q` | 靜默模式                       | 停用               |

---

### Python API

#### 基本使用

```python
from smart_ocr import OCREngine, OCRConfig

# 建立配置（中文優化）
config = OCRConfig.for_chinese()

# 初始化引擎
engine = OCREngine(config)

# 處理單一圖片
result = engine.process_image("文件.png")

# 取得辨識結果
print(result.text)                           # 完整文字
print(f"信心分數: {result.average_confidence:.2%}")  # 平均信心分數

# 逐行取得結果
for line in result.lines:
    print(f"{line.text} (信心: {line.confidence:.2%})")
```

#### 批量處理

```python
from smart_ocr import OCREngine, OCRConfig

engine = OCREngine()

# 處理整個資料夾
results = engine.process_directory("./文件資料夾/")

# 遞迴處理（包含子資料夾）
results = engine.process_directory("./文件資料夾/", recursive=True)

# 指定圖片格式
results = engine.process_directory(
    "./文件資料夾/",
    extensions=[".png", ".jpg"],  # 只處理這些格式
    recursive=True
)

# 處理結果
for result in results:
    print(f"檔案: {result.source_file}")
    print(f"內容: {result.text}")
    print("-" * 40)
```

#### 匯出結果

```python
from smart_ocr import OCREngine

engine = OCREngine()
results = engine.process_directory("./文件資料夾/")

# 匯出為 JSON
engine.export_results(results, "output/結果.json", format="json")

# 匯出為 CSV
engine.export_results(results, "output/結果.csv", format="csv")

# 匯出為純文字
engine.export_results(results, "output/結果.txt", format="txt")
```

#### 自訂配置

```python
from smart_ocr import OCRConfig, OCREngine

# 自訂配置
config = OCRConfig(
    lang="ch",              # 語言：ch（中文）, en（英文）
    use_gpu=False,          # 是否使用 GPU
    use_angle_cls=True,     # 是否啟用文字方向分類
    det_db_thresh=0.3,      # 文字偵測閾值
    det_db_box_thresh=0.6,  # 文字框閾值
    output_dir="output",    # 預設輸出目錄
)

# 使用預設配置
config_cn = OCRConfig.for_chinese()  # 中文優化
config_en = OCRConfig.for_english()  # 英文優化
config_env = OCRConfig.from_env()    # 從環境變數讀取

engine = OCREngine(config_cn)
```

---

## 輸出格式說明

### TXT 格式

```
=== 文件1.png ===
這是辨識出來的文字內容
第二行文字

=== 文件2.png ===
另一個文件的內容
```

### JSON 格式

```json
[
  {
    "source_file": "文件1.png",
    "text": "這是辨識出來的文字內容\n第二行文字",
    "average_confidence": 0.95,
    "lines": [
      {
        "text": "這是辨識出來的文字內容",
        "confidence": 0.96,
        "bbox": [[10, 10], [200, 10], [200, 30], [10, 30]]
      },
      {
        "text": "第二行文字",
        "confidence": 0.94,
        "bbox": [[10, 40], [100, 40], [100, 60], [10, 60]]
      }
    ]
  }
]
```

### CSV 格式

| file      | text                   | confidence | bbox          |
| --------- | ---------------------- | ---------- | ------------- |
| 文件1.png | 這是辨識出來的文字內容 | 0.96       | [[10,10],...] |
| 文件1.png | 第二行文字             | 0.94       | [[10,40],...] |

### XLSX 格式（Excel）

Excel 檔案包含以下欄位，使用 UTF-8 編碼：

| 檔案      | 行號 | 文字內容               | 信心分數 | 座標          |
| --------- | ---- | ---------------------- | -------- | ------------- |
| 文件1.png | 1    | 這是辨識出來的文字內容 | 96.00%   | [[10,10],...] |
| 文件1.png | 2    | 第二行文字             | 94.00%   | [[10,40],...] |

**特色**：

- 標題列固定（凍結窗格）
- 欄位寬度自動調整
- 支援直接用 Excel 開啟，無亂碼

---

## 支援的圖片格式

| 格式 | 副檔名      |
| ---- | ----------- |
| PNG  | .png        |
| JPEG | .jpg, .jpeg |
| BMP  | .bmp        |
| TIFF | .tiff       |

---

## 專案結構

```
smart-ocr-system/
├── src/smart_ocr/           # CLI 工具原始碼
│   ├── __init__.py          # 套件初始化
│   ├── cli.py               # 命令列介面
│   └── core/
│       ├── config.py        # 配置管理
│       └── ocr_engine.py    # OCR 處理引擎 (PaddleOCR)
│
├── smart-ocr-saas/          # SaaS 服務 (OpenAI Vision)
│   ├── backend/             # FastAPI 後端
│   │   ├── app/
│   │   │   ├── api/v1/      # API 路由
│   │   │   ├── core/        # 核心功能
│   │   │   ├── models/      # 資料模型
│   │   │   ├── services/    # 業務邏輯
│   │   │   └── repositories/# 資料存取層
│   │   └── Dockerfile
│   ├── frontend/            # Next.js 前端
│   │   ├── app/             # App Router 頁面
│   │   ├── stores/          # Zustand 狀態管理
│   │   └── Dockerfile
│   └── docker-compose.yml   # Docker 部署配置
│
├── tests/                   # 測試套件
├── docs/                    # 專案文件
├── data/                    # 測試資料
├── output/                  # 輸出目錄
├── pyproject.toml           # 專案配置
└── README.md                # 本文件
```

---

## 開發指南

### 安裝開發相依套件

```bash
uv pip install pytest pytest-cov black isort flake8 mypy
```

### 執行測試

```bash
# 執行所有測試
pytest tests/

# 執行並顯示詳細資訊
pytest tests/ -v

# 執行並顯示覆蓋率
pytest tests/ --cov=src/smart_ocr
```

### 程式碼格式化

```bash
# 格式化程式碼
black src/ tests/

# 排序 import
isort src/ tests/
```

### 靜態分析

```bash
# Lint 檢查
flake8 src/

# 類型檢查
mypy src/
```

---

## 效能建議

1. **GPU 加速**：如有 NVIDIA GPU，安裝 `paddlepaddle-gpu` 並使用 `--gpu` 參數
2. **批量處理**：處理資料夾比逐一處理檔案更有效率
3. **語言設定**：設定正確的語言（`--lang`）可提高辨識準確度
4. **圖片品質**：高解析度、清晰的圖片可獲得更好的辨識效果

---

## 快速執行範例

```bash
# 1. 啟動虛擬環境
.venv\Scripts\activate

# 2. 處理單張圖片（CPU）
smart-ocr process data/image.jpg

# 3. 處理單張圖片（GPU 加速）
smart-ocr process data/image.jpg --gpu

# 4. 輸出到 JSON 檔案
smart-ocr process data/image.jpg -o output/result.json -f json --gpu

# 5. 輸出到 CSV 檔案
smart-ocr process data/image.jpg -o output/result.csv -f csv --gpu

# 6. 輸出到 Excel 檔案（UTF-8 編碼）
smart-ocr process data/image.jpg -o output/result.xlsx -f xlsx --gpu

# 7. 批量處理整個資料夾
smart-ocr process data/ -r -o output/batch_result.json -f json --gpu
```

---

## 常見問題

### Q: 辨識結果不準確？

1. 確認圖片清晰度足夠
2. 確認語言設定正確（中文用 `ch`，英文用 `en`）
3. 嘗試調整偵測閾值參數

### Q: 處理速度太慢？

1. 使用 GPU 加速（`--gpu`）
2. 批量處理整個資料夾而非逐一處理
3. 降低圖片解析度（如果可接受）

### Q: 安裝時出現錯誤？

1. 確認 Python 版本為 3.10+
2. 確認已正確安裝 PaddlePaddle
3. Windows 用戶可能需要安裝 Visual C++ Redistributable

### Q: GPU 版本出現 cuDNN 錯誤？

如果出現 `cudnn64_8.dll not found` 錯誤：

```bash
# 安裝 cuDNN 8.x（paddlepaddle-gpu 2.6.2 需要）
pip install nvidia-cudnn-cu11==8.9.5.29
```

### Q: Windows 終端機顯示亂碼？

程式已自動處理 UTF-8 編碼。如果仍有問題，可在 PowerShell 執行：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## SaaS 服務

如需使用雲端版本（基於 OpenAI Vision API），請參閱 [smart-ocr-saas/README.md](./smart-ocr-saas/README.md)。

SaaS 版本提供：
- Web 介面操作
- PDF 文件辨識
- 企業 LDAP 認證
- 歷史紀錄管理
- 多格式匯出

---

## 授權

MIT License

---

## 致謝

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 優秀的多語言 OCR 工具包
- [PaddlePaddle](https://www.paddlepaddle.org.cn/) - 深度學習平台
- [OpenAI](https://openai.com/) - GPT-4 Vision API
