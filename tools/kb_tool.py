"""Knowledge Base Retrieval Tool for AutoGen with Gap Tracking."""

from pathlib import Path
from database.db_service import SessionLocal
from database.models import KBDeficiency


def search_kb(query: str) -> str:
    """Searches local company policy documents (shipping, refunds, account, product FAQ)
    and returns relevant matching excerpts with source filenames.

    Args:
        query: Keywords or key terms describing the customer complaint or policy question.

    Returns:
        Relevant excerpts from policies with source citations, or a not-found notice.
    """
    kb_dir = Path(__file__).resolve().parent.parent / "knowledge_base"
    if not kb_dir.exists():
        return "Error: Knowledge base directory does not exist."

    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    matches = []

    for md_file in kb_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for para in paragraphs:
            para_lower = para.lower()
            hit_count = sum(1 for term in query_terms if term in para_lower)
            if hit_count > 0:
                matches.append((hit_count, md_file.name, para))

    if not matches:
        try:
            db = SessionLocal()
            record = KBDeficiency(query=query, notes="Automated log: no matching policy found")
            db.add(record)
            db.commit()
            db.close()
        except Exception:
            pass
        return "NO_MATCH: No relevant company policies found for the requested query."

    matches.sort(key=lambda x: x[0], reverse=True)
    top_matches = matches[:3]

    output_lines = []
    for count, source_file, text in top_matches:
        output_lines.append(f"[Source: {source_file}]\n{text}\n")

    return "\n---\n".join(output_lines)
