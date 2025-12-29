'use client'

import { useState, useEffect } from 'react'
import { File, Trash2, Download, Eye } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import Link from 'next/link'

interface OCRTask {
  id: string
  original_filename: string
  file_type: string
  status: string
  created_at: string
  page_count: number
}

export default function HistoryPage() {
  const [tasks, setTasks] = useState<OCRTask[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const limit = 10

  useEffect(() => {
    fetchHistory()
  }, [page])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/history', {
        params: { skip: (page - 1) * limit, limit },
      })
      setTasks(response.data.tasks)
      setTotal(response.data.total)
    } catch (error) {
      console.error('Failed to fetch history:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteTask = async (taskId: string) => {
    if (!confirm('確定要刪除此紀錄嗎？')) return

    try {
      await apiClient.delete(`/history/${taskId}`)
      fetchHistory()
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  const downloadResult = async (taskId: string, format: string) => {
    try {
      const response = await apiClient.get(`/export/${taskId}?format=${format}`, {
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ocr_result.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      completed: 'bg-green-100 text-green-800',
      processing: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800',
      uploaded: 'bg-gray-100 text-gray-800',
    }

    const labels: Record<string, string> = {
      completed: '已完成',
      processing: '處理中',
      failed: '失敗',
      uploaded: '待處理',
    }

    return (
      <span className={`px-2 py-1 text-xs rounded-full ${styles[status] || styles.uploaded}`}>
        {labels[status] || status}
      </span>
    )
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">歷史紀錄</h1>
        <p className="text-gray-600">查看和管理您的 OCR 辨識紀錄</p>
      </div>

      {loading ? (
        <div className="text-center py-12">載入中...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          尚無辨識紀錄
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    檔案名稱
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    類型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    狀態
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    建立時間
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <File className="w-5 h-5 text-gray-400 mr-3" />
                        <span className="text-sm font-medium text-gray-900">
                          {task.original_filename}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {task.file_type === 'pdf' ? 'PDF' : '圖片'}
                      {task.page_count > 1 && ` (${task.page_count} 頁)`}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(task.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(task.created_at).toLocaleString('zh-TW')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right space-x-2">
                      {task.status === 'completed' && (
                        <>
                          <Link
                            href={`/results/${task.id}`}
                            className="inline-flex items-center px-2 py-1 text-sm text-blue-600 hover:text-blue-800"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            查看
                          </Link>
                          <button
                            onClick={() => downloadResult(task.id, 'xlsx')}
                            className="inline-flex items-center px-2 py-1 text-sm text-green-600 hover:text-green-800"
                          >
                            <Download className="w-4 h-4 mr-1" />
                            匯出
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="inline-flex items-center px-2 py-1 text-sm text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        刪除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm border rounded disabled:opacity-50"
              >
                上一頁
              </button>
              <span className="px-4 py-2 text-sm">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm border rounded disabled:opacity-50"
              >
                下一頁
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
