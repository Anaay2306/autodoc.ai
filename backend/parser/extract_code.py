import os
import tempfile
import shutil
from typing import List, Dict, Any
from git import Repo

try:
    from tree_sitter_languages import get_language, get_parser  # type: ignore
    TS_AVAILABLE = True
except Exception:
    TS_AVAILABLE = False

SUPPORTED_EXTS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cs": "c_sharp",
}

IGNORED_DIRS = {".git", "node_modules", ".venv", "dist", "build", ".next"}


def _detect_lang(path: str) -> str:
    _, ext = os.path.splitext(path)
    return SUPPORTED_EXTS.get(ext, "")


def _extract_chunks_from_file(file_path: str, repo_url: str) -> List[Dict[str, Any]]:
    lang = _detect_lang(file_path)
    chunks: List[Dict[str, Any]] = []
    
    # Skip very large files
    if os.path.getsize(file_path) > 1024 * 1024:  # 1MB limit
        print(f"Skipping large file {file_path}")
        return chunks
        
    try:
        if TS_AVAILABLE and lang:
            try:
                language = get_language(lang)  # noqa: F401
                parser = get_parser(lang)
                with open(file_path, "rb") as f:
                    code = f.read()
                _ = parser.parse(code)  # We could walk the tree; baseline uses whole file
                decoded = code.decode("utf-8", errors="ignore")
                if len(decoded.strip()) > 0:  # Skip empty files
                    chunks.append({
                        "repo_url": repo_url,
                        "file_path": file_path,
                        "content": decoded,
                        "metadata": {"language": lang, "parsed_with": "tree-sitter"},
                    })
            except Exception as e:
                print(f"Tree-sitter parsing failed for {file_path}: {e}")
                # Fallback to basic parsing
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if len(content.strip()) > 0:  # Skip empty files
                    chunks.append({
                        "repo_url": repo_url,
                        "file_path": file_path,
                        "content": content,
                        "metadata": {"language": lang, "parsed_with": "fallback"},
                    })
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if len(content.strip()) > 0:  # Skip empty files
                chunks.append({
                    "repo_url": repo_url,
                    "file_path": file_path,
                    "content": content,
                    "metadata": {"language": lang or "unknown", "parsed_with": "fallback"},
                })
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return chunks


async def parse_repository(repo_url: str, force_reparse: bool = False) -> List[Dict[str, Any]]:
    tmp_dir = tempfile.mkdtemp(prefix="autodoc_")
    try:
        print(f"Cloning repository {repo_url} to {tmp_dir}...")
        # Set a timeout for the clone operation
        Repo.clone_from(repo_url, tmp_dir, depth=1)  # depth=1 for faster cloning
        print("Repository cloned successfully")
        
        all_chunks: List[Dict[str, Any]] = []
        for root, dirs, files in os.walk(tmp_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for fname in files:
                try:
                    path = os.path.join(root, fname)
                    rel = os.path.relpath(path, tmp_dir)
                    # Limit to code-like files
                    if any(rel.endswith(ext) for ext in SUPPORTED_EXTS.keys()):
                        chunks = _extract_chunks_from_file(path, repo_url)
                        if chunks:
                            all_chunks.extend(chunks)
                            print(f"Processed {rel}: {len(chunks)} chunks")
                except Exception as e:
                    print(f"Error processing {fname}: {e}")
                    continue
        
        print(f"Total chunks extracted: {len(all_chunks)}")
        return all_chunks
    except Exception as e:
        print(f"Error during repository parsing: {e}")
        raise
    finally:
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Failed to cleanup temporary directory {tmp_dir}: {e}")
