import { useState } from 'react'
import { motion } from 'framer-motion'
import RepoInput from '../components/RepoInput'
import MarkdownPreview from '../components/MarkdownPreview'
import Lightning from '../components/Lightning'

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [markdown, setMarkdown] = useState('')
  const [error, setError] = useState('')

  const onGenerate = async (repoUrl: string) => {
    setError('')
    setLoading(true)
    setMarkdown('')
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const parseRes = await fetch(`${backendUrl}/parse_repo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl })
      });
      const parseJson = await parseRes.json().catch(() => ({}));
      if (!parseRes.ok) throw new Error(parseJson.error || 'Failed to parse repository');

      const genRes = await fetch(`${backendUrl}/generate_readme`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl })
      });
      const data = await genRes.json().catch(() => ({}));
      if (!genRes.ok) throw new Error(data.error || 'Failed to generate README');
      setMarkdown(data.readme || '');
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <Lightning hue={220} xOffset={0} speed={1} intensity={0.9} size={1} />
      <div className="relative z-10 px-4 py-10 flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-4xl bg-card/80 backdrop-blur border border-border rounded-lg p-6"
        >
          <h1 className="text-2xl font-semibold mb-2">AutoDoc.AI</h1>
          <p className="text-muted mb-6">Generate high-quality README.md files from public GitHub repositories.</p>

          <RepoInput loading={loading} onGenerate={onGenerate} />
          {error && <div className="text-red-400 text-sm mt-4">{error}</div>}

          <MarkdownPreview markdown={markdown} />
        </motion.div>
        <footer className="mt-6 text-xs text-muted">Built with Next.js, FastAPI, Supabase, and Perplexity</footer>
      </div>
    </div>
  )
}
