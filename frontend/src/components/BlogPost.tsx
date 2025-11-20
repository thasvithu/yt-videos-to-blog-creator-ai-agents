import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Copy, Download, Mail, Check, RefreshCw } from 'lucide-react'
import { sendEmail } from '../api/client'

interface Props {
  data: {
    title: string
    markdown_content: string
    html_content?: string
    metadata?: any
    created_at: string
  }
  onReset: () => void
}

export default function BlogPost({ data, onReset }: Props) {
  const [copied, setCopied] = useState(false)
  const [emailInput, setEmailInput] = useState('')
  const [emailSent, setEmailSent] = useState(false)
  const [emailError, setEmailError] = useState('')

  const handleCopy = () => {
    navigator.clipboard.writeText(data.markdown_content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([data.markdown_content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${data.title.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleSendEmail = async () => {
    if (!emailInput) return

    setEmailError('')
    try {
      // TODO: Get job_id from somewhere
      await sendEmail('job-id-placeholder', emailInput)
      setEmailSent(true)
      setTimeout(() => setEmailSent(false), 3000)
    } catch (err: any) {
      setEmailError('Failed to send email')
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-gray-800">{data.title}</h2>
        <button
          onClick={onReset}
          className="flex items-center text-blue-600 hover:text-blue-700 font-medium"
        >
          <RefreshCw className="w-5 h-5 mr-2" />
          New Post
        </button>
      </div>

      <div className="flex gap-3 mb-6">
        <button
          onClick={handleCopy}
          className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 mr-2 text-green-600" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 mr-2" />
              Copy
            </>
          )}
        </button>

        <button
          onClick={handleDownload}
          className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <Download className="w-4 h-4 mr-2" />
          Download
        </button>
      </div>

      {/* Email Section */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex gap-3">
          <input
            type="email"
            value={emailInput}
            onChange={(e) => setEmailInput(e.target.value)}
            placeholder="Enter email to receive this post"
            className="flex-1 px-4 py-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSendEmail}
            disabled={!emailInput || emailSent}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
          >
            {emailSent ? (
              <>
                <Check className="w-4 h-4 mr-2" />
                Sent!
              </>
            ) : (
              <>
                <Mail className="w-4 h-4 mr-2" />
                Send Email
              </>
            )}
          </button>
        </div>
        {emailError && (
          <p className="mt-2 text-sm text-red-600">{emailError}</p>
        )}
      </div>

      {/* Blog Content */}
      <div className="prose prose-lg max-w-none">
        <ReactMarkdown>{data.markdown_content}</ReactMarkdown>
      </div>

      <div className="mt-8 pt-6 border-t border-gray-200 text-sm text-gray-500">
        Generated on {new Date(data.created_at).toLocaleString()}
      </div>
    </div>
  )
}
