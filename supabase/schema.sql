-- Enable pgvector (enabled by default on Supabase)
create extension if not exists vector;

-- Table: code_chunks
create table if not exists public.code_chunks (
  id uuid primary key default gen_random_uuid(),
  repo_url text not null,
  file_path text not null,
  content text not null,
  metadata jsonb not null default '{}',
  embedding vector(1536),
  created_at timestamptz not null default now()
);
create index if not exists code_chunks_repo_idx on public.code_chunks (repo_url);
create index if not exists code_chunks_path_idx on public.code_chunks (file_path);
create index if not exists code_chunks_embedding_idx on public.code_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- Table: readme_history
create table if not exists public.readme_history (
  id uuid primary key default gen_random_uuid(),
  repo_url text not null,
  generated_readme text not null,
  created_at timestamptz not null default now()
);
create index if not exists readme_repo_idx on public.readme_history (repo_url);

-- Function: match_code_chunks
create or replace function match_code_chunks (
  repo_url_filter text,
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  repo_url text,
  file_path text,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select
    code_chunks.id,
    code_chunks.repo_url,
    code_chunks.file_path,
    code_chunks.content,
    code_chunks.metadata,
    1 - (code_chunks.embedding <=> query_embedding) as similarity
  from code_chunks
  where
    code_chunks.repo_url = repo_url_filter and
    1 - (code_chunks.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
$$;
