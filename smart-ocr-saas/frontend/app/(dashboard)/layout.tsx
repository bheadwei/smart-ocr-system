'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/stores/authStore'
import { Upload, History, Settings, LogOut } from 'lucide-react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { isAuthenticated, user, logout } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/upload" className="text-xl font-bold text-blue-600">
                Smart OCR
              </Link>

              <div className="hidden sm:ml-10 sm:flex sm:space-x-4">
                <Link
                  href="/upload"
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  上傳辨識
                </Link>
                <Link
                  href="/history"
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600"
                >
                  <History className="w-4 h-4 mr-2" />
                  歷史紀錄
                </Link>
                {user?.role === 'admin' && (
                  <Link
                    href="/admin/users"
                    className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    使用者管理
                  </Link>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user?.display_name || user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-red-600"
              >
                <LogOut className="w-4 h-4 mr-2" />
                登出
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}
