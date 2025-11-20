import { useState, useEffect } from 'react'
import { generateBlogPost, getJobStatus, GenerateRequest } from '../api/client'
import { Loader2, Youtube } from 'lucide-react'

interface Props {
  onJobCreated: (jobId: string) => void
  onBlogGenerated: (data: any) => void
  jobId: string | null
}

export default function GeneratorForm({ onJobCreated, onBlogGenerated, jobId }: Props) {
  const [channelName, setChannelName] = useState('')
  const [videoTitle, setVideoTitle] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [statusMessage, setStatusMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!jobId) return

    // Poll for job status
    const interval = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId)
        setProgress(status.progress)
        
        if (status.status === 'completed' && status.result) {
          clearInterval(interval)
          setLoading(false)
          onBlogGenerated(status.result)
        } else if (status.status === 'failed') {
          clearInterval(interval)
          setLoading(false)
          setError(status.error_message || 'Generation failed')
        } else {
          setStatusMessage(`Status: ${status.status}... ${status.progress}%`)
        }
      } catch (err: any) {
        console.error('Status check error:', err)
        setError('Failed to check job status')
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(interval)
  }, [jobId, onBlogGenerated])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    setProgress(0)
    setStatusMessage('Starting generation...')

    try {
      const request: GenerateRequest = {
        channel_name: channelName,
        video_title: videoTitle,
        ...(email && { email })
      }

      const response = await generateBlogPost(request)
      onJobCreated(response.job_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start generation')
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="flex items-center justify-center mb-6">
        <Youtube className="w-12 h-12 text-red-600 mr-3" />
        <h2 className="text-3xl font-bold text-gray-800">Generate Blog Post</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="channel" className="block text-sm font-medium text-gray-700 mb-2">
            YouTube Channel Name *
          </label>
          <input
            id="channel"
            type="text"
            value={channelName}
            onChange={(e) => setChannelName(e.target.value)}
            placeholder="e.g., @freecodecamp"
            required
            disabled={loading}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>

        <div>
          <label htmlFor="video" className="block text-sm font-medium text-gray-700 mb-2">
            Video Title *
          </label>
          <input
            id="video"
            type="text"
            value={videoTitle}
            onChange={(e) => setVideoTitle(e.target.value)}
            placeholder="e.g., Python Tutorial for Beginners"
            required
            disabled={loading}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            Email (Optional)
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            disabled={loading}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
          <p className="mt-1 text-sm text-gray-500">
            We'll send the blog post to this email when ready
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {loading && (
          <div className="bg-blue-50 border border-blue-200 px-4 py-3 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-blue-700 font-medium">{statusMessage}</span>
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            'Generate Blog Post'
          )}
        </button>
      </form>
    </div>
  )
}
