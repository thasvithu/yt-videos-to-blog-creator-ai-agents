import { useState } from 'react'
import GeneratorForm from './components/GeneratorForm'
import BlogPost from './components/BlogPost'
import './App.css'

function App() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [blogData, setBlogData] = useState<any>(null)

  const handleJobCreated = (id: string) => {
    setJobId(id)
  }

  const handleBlogGenerated = (data: any) => {
    setBlogData(data)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            YouTube to Blog Generator
          </h1>
          <p className="text-xl text-gray-600">
            Transform any YouTube video into a beautifully formatted blog post
          </p>
        </header>

        <div className="max-w-4xl mx-auto">
          {!blogData ? (
            <GeneratorForm 
              onJobCreated={handleJobCreated}
              onBlogGenerated={handleBlogGenerated}
              jobId={jobId}
            />
          ) : (
            <BlogPost 
              data={blogData}
              onReset={() => {
                setJobId(null)
                setBlogData(null)
              }}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default App
