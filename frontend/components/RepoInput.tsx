import { useState } from 'react'

type Props = {
  loading: boolean
  onGenerate: (url: string) => Promise<void>
}

export default function RepoInput({ loading, onGenerate }: Props) {
  const [repoUrl, setRepoUrl] = useState('')

  return (
    <div className="flex gap-2">
      <input
        className="flex-1 bg-transparent border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
        placeholder="https://github.com/owner/repo"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
      />
      <button
        onClick={() => onGenerate(repoUrl)}
        disabled={loading || !repoUrl}
        className="bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-lg px-4 py-2"
      >
        {loading ? 'Generating…' : 'Generate'}
      </button>
    </div>
  )
}
