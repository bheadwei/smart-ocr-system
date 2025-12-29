'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, Loader2, FileText, CheckCircle, XCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface OCRField {
  key: string
  value: string
  confidence: number
}

interface OCRResult {
  page_number: number
  extracted_text: string
  structured_data: {
    type: string
    fields: OCRField[]
  }
  confidence: number
}

interface TaskResult {
  task_id: string
  status: string
  results: OCRResult[]
  created_at: string
}

// Define the target fields we want to display
const TARGET_FIELDS = [
  { key: '銀行名稱', label: '銀行名稱' },
  { key: '戶名', label: '戶名' },
  { key: '身分證', label: '身分證' },
  { key: '存款帳號', label: '存款帳號' },
  { key: '連絡電話', label: '連絡電話' },
  { key: '聯絡地址', label: '聯絡地址' },
  { key: '電費', label: '電費帳號' },
  { key: '水費', label: '水費帳號' },
  { key: '電信費', label: '電信費帳號' },
]

export default function ResultPage() {
  const params = useParams()
  const router = useRouter()
  const taskId = params.id as string

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [taskResult, setTaskResult] = useState<TaskResult | null>(null)

  useEffect(() => {
    const fetchResult = async () => {
      try {
        setLoading(true)
        const response = await apiClient.get(`/ocr/result/${taskId}`)
        setTaskResult(response.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || '無法取得辨識結果')
      } finally {
        setLoading(false)
      }
    }

    if (taskId) {
      fetchResult()
    }
  }, [taskId])

  const downloadResult = async (format: string) => {
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

  // Helper to get field value from result
  const getFieldValue = (result: OCRResult, fieldKey: string): string => {
    const fields = result.structured_data?.fields || []
    const field = fields.find(f => f.key === fieldKey)
    return field?.value || '-'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">載入中...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => router.back()}
          className="flex items-center text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          返回
        </button>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-medium text-red-800">{error}</h2>
          <p className="text-red-600 mt-2">請確認任務 ID 是否正確，或稍後再試</p>
        </div>
      </div>
    )
  }

  if (!taskResult) {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => router.back()}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            返回
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">辨識結果</h1>
            <p className="text-sm text-gray-500">任務 ID: {taskId}</p>
          </div>
        </div>

        {/* Download buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => downloadResult('json')}
            className="flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            <Download className="w-4 h-4 mr-2" />
            JSON
          </button>
          <button
            onClick={() => downloadResult('xlsx')}
            className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Download className="w-4 h-4 mr-2" />
            Excel
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="flex items-center space-x-2">
        {taskResult.status === 'completed' ? (
          <CheckCircle className="w-5 h-5 text-green-500" />
        ) : (
          <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
        )}
        <span className={taskResult.status === 'completed' ? 'text-green-600' : 'text-blue-600'}>
          {taskResult.status === 'completed' ? '辨識完成' : '處理中'}
        </span>
        <span className="text-gray-400">|</span>
        <span className="text-gray-500">{taskResult.results?.length || 0} 頁</span>
      </div>

      {/* Results Table */}
      {taskResult.results && taskResult.results.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    頁碼
                  </th>
                  {TARGET_FIELDS.map(field => (
                    <th
                      key={field.key}
                      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {field.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {taskResult.results.map((result, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {result.page_number}
                    </td>
                    {TARGET_FIELDS.map(field => (
                      <td
                        key={field.key}
                        className="px-4 py-4 text-sm text-gray-900 max-w-xs truncate"
                        title={getFieldValue(result, field.key)}
                      >
                        {getFieldValue(result, field.key)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Raw Text Section */}
      {taskResult.results && taskResult.results.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-medium text-gray-900">原始辨識文字</h2>
          </div>
          <div className="divide-y">
            {taskResult.results.map((result, idx) => (
              <div key={idx} className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    第 {result.page_number} 頁
                  </span>
                  <span className="text-xs text-gray-500">
                    信心度: {(result.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <pre className="text-sm text-gray-600 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg overflow-x-auto">
                  {result.extracted_text || '(無辨識文字)'}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
