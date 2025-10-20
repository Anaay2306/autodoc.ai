import type { NextApiRequest, NextApiResponse } from 'next'

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'Method not allowed' })
  try {
    const resp = await fetch(`${backendUrl}/parse_repo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    })
    const data = await resp.json().catch(() => ({}))
    if (!resp.ok) return res.status(resp.status).json({ ok: false, error: data.detail || 'Parse failed' })
    res.status(200).json(data)
  } catch (e: any) {
    res.status(500).json({ ok: false, error: e.message || 'Proxy error' })
  }
}
