from typing import List, Dict, Protocol

class MarkdownModelClient(Protocol):
    def generate_markdown(self, system_prompt: str, user_prompt: str) -> str: ...

SYSTEM_PROMPT = (
    "You are an expert technical documentation writer and software architect specializing in healthcare systems. "
    "Analyze this repository and generate a superior README.md that surpasses standard documentation tools. "
    "Include comprehensive technical insights while maintaining clarity for all user levels.\n\n"
    "📋 Required Sections:\n\n"
    "1. Project Overview\n"
    "   - Executive summary with project vision and goals\n"
    "   - Problem statement and solution approach\n"
    "   - Target users and stakeholders\n"
    "   - Key differentiators and unique value proposition\n\n"
    "2. 🌟 Core Features\n"
    "   - Comprehensive feature list with technical capabilities\n"
    "   - Feature status (stable, beta, planned)\n"
    "   - Screenshots or diagrams where relevant\n"
    "   - Real-world use cases and scenarios\n\n"
    "3. 🔧 Technology Foundation\n"
    "   - Complete technology stack with version compatibility\n"
    "   - Architecture diagram with detailed component interactions\n"
    "   - Database schema overview and data flow\n"
    "   - External service integrations\n"
    "   - Performance considerations and optimizations\n\n"
    "4. 🚀 Getting Started\n"
    "   - Detailed prerequisites with version requirements\n"
    "   - Step-by-step installation guide\n"
    "   - Configuration options and customization\n"
    "   - Quick start examples\n"
    "   - Common troubleshooting tips\n\n"
    "5. 💻 Developer Guide\n"
    "   - Project structure explanation\n"
    "   - Code organization and patterns\n"
    "   - Development environment setup\n"
    "   - Coding standards and best practices\n"
    "   - Testing strategy and framework usage\n"
    "   - CI/CD pipeline overview\n\n"
    "6. 📚 API Documentation\n"
    "   - RESTful API endpoints with examples\n"
    "   - Request/response schemas\n"
    "   - Authentication and authorization flows\n"
    "   - Rate limiting and optimization\n"
    "   - Error handling and status codes\n"
    "   - API versioning strategy\n\n"
    "7. 🔐 Security & Compliance\n"
    "   - Security features and implementation\n"
    "   - Data encryption and protection measures\n"
    "   - Authentication mechanisms\n"
    "   - Authorization and access control\n"
    "   - Audit logging and monitoring\n"
    "   - Healthcare compliance considerations (HIPAA, etc.)\n\n"
    "8. 🌐 Deployment Guide\n"
    "   - Infrastructure requirements\n"
    "   - Environment setup (dev, staging, prod)\n"
    "   - Configuration management\n"
    "   - Monitoring and logging setup\n"
    "   - Backup and disaster recovery\n"
    "   - Performance optimization tips\n\n"
    "9. 🤝 Contributing\n"
    "   - Contribution workflow\n"
    "   - Code review process\n"
    "   - Branch strategy\n"
    "   - Issue and PR templates\n"
    "   - Community guidelines\n\n"
    "10. 📈 Roadmap & Vision\n"
    "    - Current development status\n"
    "    - Planned features and improvements\n"
    "    - Long-term project goals\n"
    "    - Known limitations and solutions\n\n"
    "11. ⚖️ Legal & Licensing\n"
    "    - License details\n"
    "    - Attribution requirements\n"
    "    - Third-party licenses\n"
    "    - Usage restrictions\n\n"
    "Use enhanced Markdown formatting:\n"
    "- Use tables for structured data\n"
    "- Include code blocks with syntax highlighting\n"
    "- Add collapsible sections for detailed content\n"
    "- Use badges for status indicators\n"
    "- Include anchors for navigation\n"
    "- Add inline comments for clarity\n\n"
    "Extract and highlight:\n"
    "- Key architectural decisions and their rationale\n"
    "- Critical security implementations\n"
    "- Performance optimizations\n"
    "- Unique technical solutions\n"
    "- Best practices implementation\n\n"
    "Focus on producing documentation that is:\n"
    "1. Technically comprehensive yet accessible\n"
    "2. Well-structured and easy to navigate\n"
    "3. Actionable with practical examples\n"
    "4. Maintainable and easy to update\n"
    "5. Security-focused for healthcare context\n"
)


def _format_context(chunks: List[Dict]) -> str:
    lines = []
    total_size = 0
    max_content_size = 3000  # Increased for more comprehensive analysis
    max_chunks = 25  # Balanced for important context
    
    # Enhanced priority sorting with more nuanced categories
    def chunk_priority(chunk):
        path = chunk.get('file_path', '').lower()
        content = chunk.get('content', '').lower()
        score = 5  # Default priority
        
        # Core application files
        if 'main.py' in path or 'app.js' in path:
            score = 0
        # Security-related files
        elif any(term in path for term in ['auth', 'security', 'encrypt']):
            score = 1
        # API and routing files
        elif any(term in path for term in ['routes', 'api', 'controller']):
            score = 2
        # Data model and schema files
        elif any(term in path for term in ['model', 'schema', 'database']):
            score = 3
        # Healthcare-specific files
        elif any(term in content for term in ['patient', 'doctor', 'medical', 'health']):
            score = 4
            
        # Boost score for files with substantial documentation
        if content.count('"""') > 1 or content.count('/**') > 1:
            score -= 0.5
        # Boost for files with type hints or interfaces
        if any(term in content for term in ['type ', 'interface ', '@types']):
            score -= 0.3
            
        return score
    
    # Sort chunks by priority score
    sorted_chunks = sorted(chunks, key=chunk_priority)
    
    # Group related files together
    grouped_chunks = []
    current_group = []
    current_type = None
    
    for c in sorted_chunks[:max_chunks]:
        path = c.get('file_path', '')
        content = c.get('content', '')
        file_type = None
        
        if 'routes' in path or 'api' in path:
            file_type = 'API'
        elif 'model' in path or 'schema' in path:
            file_type = 'Data Model'
        elif 'auth' in path or 'security' in path:
            file_type = 'Security'
        
        if file_type != current_type and current_group:
            grouped_chunks.extend(current_group)
            current_group = []
        
        current_type = file_type
        current_group.append((path, content, file_type))
    
    grouped_chunks.extend(current_group)
    
    # Format chunks with section headers and contextual information
    for path, content, file_type in grouped_chunks:
        if total_size > 24000:  # Leave room for system prompt
            break
            
        # Add section header if it's a categorized file
        if file_type:
            lines.append(f"\n### {file_type} Component")
            
        header = f"File: {path}"
        content = c.get("content", "")
        
        # Truncate content if too long
        if len(content) > max_content_size:
            content = content[:max_content_size] + "\n... (truncated)\n"
        
        # Build code block
        code_block = f"### {header}\n\n```{c.get('metadata', {}).get('language', '')}\n{content}\n```\n"
        
        # Check if adding this chunk would exceed reasonable size
        if total_size + len(code_block) > 24000:  # Leave room for system prompt and other content
            print(f"Truncating context at {len(lines)} chunks to stay within size limits")
            break
            
        lines.append(code_block)
        total_size += len(code_block)
    
    print(f"Formatted {len(lines)} chunks, total size: {total_size} characters")
    return "\n\n".join(lines)


async def generate_readme_markdown(client: MarkdownModelClient, repo_url: str, chunks: List[Dict]) -> str:
    context = _format_context(chunks)
    user_prompt = (
        f"Repository URL: {repo_url}\n\n"
        f"Relevant code context (selected snippets):\n\n{context}\n\n"
        "Please produce a single complete README.md in Markdown."
    )
    return client.generate_markdown(SYSTEM_PROMPT, user_prompt)
