'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, Loader2, Download } from 'lucide-react'
import { useOCRProgress } from '@/hooks/useWebSocket'
import { apiClient } from '@/lib/api-client'

interface UploadedFile {
  file: File
  taskId?: string
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed'
  progress: number
  result?: any
  error?: string
}

export default function UploadPage() {
  const [files, setFiles] = useState<UploadedFile[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      status: 'pending' as const,
      progress: 0,
    }))
    setFiles((prev) => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  })

  const uploadAndProcess = async (index: number) => {
    const uploadedFile = files[index]
    if (!uploadedFile || uploadedFile.status !== 'pending') return

    // Update status to uploading
    setFiles((prev) =>
      prev.map((f, i) => (i === index ? { ...f, status: 'uploading' as const } : f))
    )

    try {
      // Upload file
      const formData = new FormData()
      formData.append('file', uploadedFile.file)

      const uploadResponse = await apiClient.post('/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      const taskId = uploadResponse.data.id

      // Update with task ID
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index ? { ...f, taskId, status: 'processing' as const } : f
        )
      )

      // Process OCR
      const processResponse = await apiClient.post(`/ocr/process/${taskId}`)

      // Update with result
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index
            ? { ...f, status: 'completed' as const, progress: 100, result: processResponse.data }
            : f
        )
      )
    } catch (error: any) {
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index
            ? { ...f, status: 'failed' as const, error: error.message || '處理失敗' }
            : f
        )
      )
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const processAll = () => {
    files.forEach((file, index) => {
      if (file.status === 'pending') {
        uploadAndProcess(index)
      }
    })
  }

  const downloadResult = async (taskId: string, format: string) => {
    try {
      const response = await apiClient.get(`/export/${taskId}?format=${format}`, {
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url

      const contentDisposition = response.headers['content-disposition']
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : `ocr_result.${format}`

      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">上傳辨識</h1>
        <p className="text-gray-600">上傳圖片或 PDF 文件進行 OCR 文字辨識</p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <p className="text-lg text-gray-600">
          {isDragActive ? '放開以上傳檔案' : '拖放檔案到這裡，或點擊選擇檔案'}
        </p>
        <p className="text-sm text-gray-400 mt-2">
          支援 JPG, PNG, PDF 等格式，單檔最大 50MB，PDF 最多 10 頁
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-medium">檔案列表 ({files.length})</h2>
            <button
              onClick={processAll}
              disabled={!files.some((f) => f.status === 'pending')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              全部處理
            </button>
          </div>

          <div className="space-y-3">
            {files.map((uploadedFile, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border"
              >
                <div className="flex items-center space-x-3">
                  <File className="w-8 h-8 text-gray-400" />
                  <div>
                    <p className="font-medium">{uploadedFile.file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {uploadedFile.status === 'pending' && (
                    <button
                      onClick={() => uploadAndProcess(index)}
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      開始處理
                    </button>
                  )}

                  {(uploadedFile.status === 'uploading' ||
                    uploadedFile.status === 'processing') && (
                    <div className="flex items-center text-blue-600">
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      處理中...
                    </div>
                  )}

                  {uploadedFile.status === 'completed' && uploadedFile.taskId && (
                    <div className="flex items-center space-x-2">
                      <span className="text-green-600 text-sm">完成</span>
                      <a
                        href={`/results/${uploadedFile.taskId}`}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      >
                        查看結果
                      </a>
                      <button
                        onClick={() => downloadResult(uploadedFile.taskId!, 'json')}
                        className="px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
                      >
                        JSON
                      </button>
                      <button
                        onClick={() => downloadResult(uploadedFile.taskId!, 'xlsx')}
                        className="px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
                      >
                        Excel
                      </button>
                    </div>
                  )}

                  {uploadedFile.status === 'failed' && (
                    <span className="text-red-600 text-sm">
                      {uploadedFile.error || '失敗'}
                    </span>
                  )}

                  <button
                    onClick={() => removeFile(index)}
                    className="p-1 text-gray-400 hover:text-red-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
