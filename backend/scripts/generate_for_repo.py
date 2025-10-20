import sys
import pathlib
import asyncio

from services.embedding_store import EmbeddingStore
from services.perplexity_client import PerplexityClient
from parser.extract_code import parse_repository
from generator.generate_readme import generate_readme_markdown


async def main(repo_url: str) -> int:
    chunks = await parse_repository(repo_url, force_reparse=True)

    store = EmbeddingStore()
    if chunks:
        await store.index_chunks(chunks)

    pplx = PerplexityClient()
    top = await store.search_chunks(repo_url, query="overview architecture usage api", top_k=80)
    readme = await generate_readme_markdown(pplx, repo_url, top)

    out_dir = pathlib.Path(".autodoc")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    try:
        root_readme = pathlib.Path("README.md")
        if not root_readme.exists():
            root_readme.write_text(readme, encoding="utf-8")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_for_repo.py <repo_url>")
        raise SystemExit(2)
    repo = sys.argv[1]
    raise SystemExit(asyncio.run(main(repo)))
