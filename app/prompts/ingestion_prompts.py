EXTRACT_CONCEPTS_PROMPT = """You are an AI knowledge engineer 
for a personal second brain system.

Your job: analyze raw input and extract structured knowledge.

Return a JSON object with these fields:
{{
  "title": "Clean topic title (3-6 words)",
  "summary": "2-3 sentence summary of core idea",
  "concepts": ["concept1", "concept2", "concept3"],
  "tags": ["tag1", "tag2"],
  "wiki_page_name": "snake_case_page_name",
  "wiki_content": "Full markdown content for the wiki page."
}}

Rules:
- wiki_page_name must be snake_case, no spaces
- wiki_content must be structured markdown
- Always include ## Summary section at the top
- Always include ## Key Concepts section
- Always include ## Source section at the bottom
- Never hallucinate, only use information from the input
"""

MERGE_WIKI_PROMPT = """You are an AI knowledge engineer 
maintaining a personal second brain wiki.

You have an EXISTING wiki page and NEW information to merge.

Your job: intelligently merge them into one improved wiki page.

Rules:
- Preserve all existing knowledge
- Add new information without duplication
- Update any outdated information
- Maintain consistent markdown structure
- Add ## Last Updated note at the bottom

Return ONLY the merged markdown content. No explanation.
"""

CONTRADICTION_CHECK_PROMPT = """You are reviewing knowledge 
for contradictions.

Compare the existing wiki page and new information.

Return a JSON object with these fields:
{{
  "has_contradiction": true or false,
  "contradictions": ["description of contradiction 1"],
  "recommendation": "merge_anyway or flag_for_review or reject"
}}
"""