import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Props = {
  markdown: string
}

export default function MarkdownPreview({ markdown }: Props) {
  const onCopy = async () => {
    if (!markdown) return
    await navigator.clipboard.writeText(markdown)
  }

  const onDownload = () => {
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'README.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!markdown) return null

  return (
    <div className="mt-6">
      <div className="flex gap-2 mb-3">
        <button onClick={onCopy} className="bg-card border border-border text-foreground rounded-lg px-3 py-2">Copy</button>
        <button onClick={onDownload} className="bg-card border border-border text-foreground rounded-lg px-3 py-2">Download README.md</button>
      </div>
      <div className="prose prose-invert max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </div>
  )
}
