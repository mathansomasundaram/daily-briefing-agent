"""
LLM formatting module.
Uses Azure OpenAI to format real articles into structured email digest.
"""

from typing import Dict, List, Union
import re
from openai import OpenAI, AzureOpenAI
from datetime import date

from src.aggregation.sources_config import get_category_display_name, get_all_category_emojis
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMFormatter:
    """
    Formats real articles into email digest using LLM.
    """

    def __init__(self, openai_client: Union[OpenAI, AzureOpenAI], model: str = "gpt-4o-mini", max_output_tokens: int = 4000, batch_size: int = 5):
        """
        Initialize the LLM formatter.

        Args:
            openai_client (Union[OpenAI, AzureOpenAI]): OpenAI or Azure OpenAI client instance
            model (str): Model or deployment name to use
            max_output_tokens (int): Maximum output tokens
            batch_size (int): Number of categories to process in each batch (default: 5)
        """
        self.client = openai_client
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.batch_size = batch_size
        self.logger = logger
        # Get emojis dynamically from configuration
        self.category_emojis = get_all_category_emojis()

    def build_prompt(self, articles_by_category: Dict[str, List[Dict]], is_batch: bool = False) -> str:
        """
        Build prompt with real article data for LLM.

        Args:
            articles_by_category (Dict[str, List[Dict]]): Articles grouped by category

        Returns:
            str: Formatted prompt
        """
        today = date.today().strftime("%B %d, %Y")

        # Build articles section
        articles_text = ""

        for category, articles in articles_by_category.items():
            if not articles:
                continue

            display_name = get_category_display_name(category)
            articles_text += f"\n{display_name}\n"
            articles_text += "=" * 50 + "\n"

            for i, article in enumerate(articles, 1):
                articles_text += f"{i}. **{article['title']}**\n"
                articles_text += f"   Summary: {article['summary']}\n"
                articles_text += f"   Source: {article['source']}\n"
                articles_text += f"   URL: {article['url']}\n"
                articles_text += "\n"

        # Build complete prompt based on whether this is a batch or full digest
        if is_batch:
            # For batches, only format the categories (no greeting/closing)
            prompt = f"""You are formatting sections of a **Daily Market & Tech Digest** for **{today}**.

Below are REAL, pre-fetched articles from the last 24 hours. Your task:
1. Format ONLY the categories provided below
2. Preserve ALL facts and sources EXACTLY as provided
3. Do NOT invent, add, or modify any information
4. Do NOT add greeting or closing - just format the category sections
5. Use SIMPLE ENGLISH - avoid jargon, complex terms, and technical language. Write for a general audience.

────────────────────────
REAL ARTICLES TO FORMAT
────────────────────────

{articles_text}

────────────────────────
FORMATTING RULES (MANDATORY)
────────────────────────
- ALL section headings MUST be **bold**
- Use emojis ONLY in headings
- Add a blank line between sections
- Use VERY SHORT bullet points for each article (1-2 lines max)
- Include source attribution for EVERY article in EXACT format: "Source: [Source Name] | [URL]"
- DO NOT use markdown links like [text](url) - use the pipe format above
- Highlight important numbers in **bold**
- Be concise - keep each article to 1-2 sentences only
- MUST include ALL categories provided above
- Focus on market-relevant, economic, and tech news - skip human interest stories
- Use SIMPLE, CLEAR ENGLISH - avoid jargon, complex vocabulary, and technical terms. Make it easy to read and understand.

────────────────────────
OUTPUT FORMAT
────────────────────────

Format ONLY the category sections (NO greeting, NO closing):

**[Category Heading with Emoji]**
- [Article 1: Very brief 1-2 line summary]
  Source: [Source] | [URL]

- [Article 2: Very brief 1-2 line summary]
  Source: [Source] | [URL]

[Continue for all articles in category]

[Blank line between categories]

CRITICAL: Include ALL categories. Be extremely concise (1-2 lines per article). Do NOT add information from your knowledge base."""
        else:
            # For full digest (original behavior)
            prompt = f"""You are formatting a **Daily Market & Tech Digest** for **{today}**.

Below are REAL, pre-fetched articles from the last 24 hours. Your task:
1. Format them into the specified structure
2. Preserve ALL facts and sources EXACTLY as provided
3. Do NOT invent, add, or modify any information
4. Keep formatting clean and mobile-friendly
5. INCLUDE ALL CATEGORIES - do not skip any category that has articles
6. Use SIMPLE ENGLISH - avoid jargon, complex terms, and technical language. Write for a general audience.

────────────────────────
REAL ARTICLES TO FORMAT
────────────────────────

{articles_text}

────────────────────────
FORMATTING RULES (MANDATORY)
────────────────────────
- ALL section headings MUST be **bold**
- Use emojis ONLY in headings
- Add a blank line between sections
- Use VERY SHORT bullet points for each article (1-2 lines max)
- Include source attribution for EVERY article in EXACT format: "Source: [Source Name] | [URL]"
- DO NOT use markdown links like [text](url) - use the pipe format above
- Highlight important numbers in **bold**
- Be concise - keep each article to 1-2 sentences only
- MUST include ALL categories provided above
- Focus on market-relevant, economic, and tech news - skip human interest stories
- Use SIMPLE, CLEAR ENGLISH - avoid jargon, complex vocabulary, and technical terms. Make it easy to read and understand.

────────────────────────
OUTPUT STRUCTURE
────────────────────────

Format the articles into this structure:

Dear Reader,

Here is your Daily Market & Tech Digest for {today}:

[For EVERY category that has articles, create a section with:]

**[Category Heading with Emoji]**
- [Article 1: Very brief 1-2 line summary]
  Source: [Source] | [URL]

- [Article 2: Very brief 1-2 line summary]
  Source: [Source] | [URL]

[Continue for all articles in category]

[Blank line between categories]

────────────────────────

Best regards,
Your Daily Briefing Agent

CRITICAL: Include ALL categories. Be extremely concise (1-2 lines per article). Do NOT add information from your knowledge base."""

        return prompt

    def _post_process_output(self, text: str) -> str:
        """
        Post-process LLM output to add HTML formatting.

        1. Convert **bold** to <b>bold</b>
        2. Convert "Source: Name | URL" to "Source: <a href='URL'>Name</a>"
        3. Add horizontal lines after section headings

        Args:
            text (str): Raw LLM output

        Returns:
            str: HTML-formatted text
        """
        # 1. Convert **text** to <b>text</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # 2a. Convert markdown links [text](url) to <a href='url'>text</a>
        def replace_markdown_link(match):
            link_text = match.group(1).strip()
            url = match.group(2).strip()
            return f"<a href='{url}'>{link_text}</a>"

        text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', replace_markdown_link, text)

        # 2b. Convert "Source: Name | URL" to "Source: <a href='URL'>Name</a>"
        # Pattern: Source: {source_name} | {url}
        def replace_source(match):
            source_name = match.group(1).strip()
            url = match.group(2).strip()
            return f"Source: <a href='{url}'>{source_name}</a>"

        text = re.sub(r'Source:\s*([^|]+?)\s*\|\s*(https?://[^\s]+)', replace_source, text)

        # 3. Add horizontal line after each section heading
        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            formatted_lines.append(line)

            # Check if this line is a section heading (starts with <b> and has emoji)
            # Add <hr> right after the heading
            # Use dynamically loaded emojis instead of hardcoded list
            if line.strip().startswith('<b>') and any(emoji in line for emoji in self.category_emojis):
                formatted_lines.append('<hr>')

        return '\n'.join(formatted_lines)

    def _format_batch(self, batch_articles: Dict[str, List[Dict]]) -> str:
        """
        Format a single batch of categories using LLM.

        Args:
            batch_articles (Dict[str, List[Dict]]): Articles for this batch

        Returns:
            str: Formatted batch content (without greeting/closing)
        """
        # Build prompt for this batch
        prompt = self.build_prompt(batch_articles, is_batch=True)

        try:
            # Call Azure OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_output_tokens,
                temperature=0.7
            )

            batch_content = response.choices[0].message.content
            if not batch_content:
                self.logger.warning("Empty response from LLM for batch")
                return self._fallback_format(batch_articles)

            # Log token usage for this batch
            if response.usage:
                usage = response.usage
                self.logger.info(
                    f"Batch token usage - Input: {usage.prompt_tokens}, "
                    f"Output: {usage.completion_tokens}, Total: {usage.total_tokens}"
                )

            return batch_content

        except Exception as e:
            self.logger.error(f"Error formatting batch: {e}", exc_info=True)
            # Fallback for this batch
            return self._fallback_format(batch_articles)

    def format_digest(self, articles_by_category: Dict[str, List[Dict]]) -> str:
        """
        Format articles into email digest using Azure OpenAI with batch processing.

        Args:
            articles_by_category (Dict[str, List[Dict]]): Articles grouped by category

        Returns:
            str: Formatted digest ready for email

        Raises:
            Exception: If OpenAI API call fails
        """
        self.logger.info(f"Formatting digest with LLM (batch size: {self.batch_size})")

        # Get list of categories
        categories = list(articles_by_category.keys())
        total_categories = len(categories)

        # If categories <= batch_size, process all at once (no batching needed)
        if total_categories <= self.batch_size:
            self.logger.info(f"Processing all {total_categories} categories in single batch")
            prompt = self.build_prompt(articles_by_category, is_batch=False)

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_output_tokens,
                    temperature=0.7
                )

                raw_digest = response.choices[0].message.content
                if not raw_digest:
                    self.logger.warning("Empty response from LLM")
                    return self._fallback_format(articles_by_category)

                # Log token usage
                if response.usage:
                    usage = response.usage
                    self.logger.info(
                        f"Token usage - Input: {usage.prompt_tokens}, "
                        f"Output: {usage.completion_tokens}, Total: {usage.total_tokens}"
                    )

                # Post-process to add HTML formatting
                formatted_digest = self._post_process_output(raw_digest)
                self.logger.info("Successfully formatted digest with LLM")
                return formatted_digest

            except Exception as e:
                self.logger.error(f"Error formatting digest with LLM: {e}", exc_info=True)
                return self._fallback_format(articles_by_category)

        # Process in batches
        self.logger.info(f"Processing {total_categories} categories in batches of {self.batch_size}")

        today = date.today().strftime("%B %d, %Y")
        all_batch_contents = []

        # Split into batches and process each
        for i in range(0, total_categories, self.batch_size):
            batch_categories = categories[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_categories + self.batch_size - 1) // self.batch_size

            self.logger.info(
                f"Processing batch {batch_num}/{total_batches}: "
                f"{', '.join(batch_categories)}"
            )

            # Create batch with selected categories
            batch_articles = {cat: articles_by_category[cat] for cat in batch_categories}

            # Format this batch
            batch_content = self._format_batch(batch_articles)
            all_batch_contents.append(batch_content)

        # Combine all batches with greeting and closing
        combined_content = f"Dear Reader,\n\n"
        combined_content += f"Here is your Daily Market & Tech Digest for {today}:\n\n"
        combined_content += "\n\n".join(all_batch_contents)
        combined_content += "\n\n────────────────────────\n\n"
        combined_content += "Best regards,\nYour Daily Briefing Agent"

        # Post-process to add HTML formatting
        formatted_digest = self._post_process_output(combined_content)

        self.logger.info(
            f"Successfully formatted digest with LLM using {len(all_batch_contents)} batches"
        )

        return formatted_digest

    def _fallback_format(self, articles_by_category: Dict[str, List[Dict]]) -> str:
        """
        Fallback formatting without LLM (simple text format with HTML).

        Args:
            articles_by_category (Dict[str, List[Dict]]): Articles grouped by category

        Returns:
            str: HTML-formatted digest
        """
        today = date.today().strftime("%B %d, %Y")

        output = f"Dear Reader,\n\n"
        output += f"Here is your Daily Market & Tech Digest for {today}:\n\n"

        for category, articles in articles_by_category.items():
            if not articles:
                continue

            display_name = get_category_display_name(category)
            output += f"**{display_name}**\n"

            for article in articles:
                output += f"- {article['title']}\n"
                output += f"  {article['summary']}\n"
                output += f"  Source: {article['source']} | {article['url']}\n\n"

            output += "\n"

        output += "Best regards,\nYour Daily Briefing Agent"

        self.logger.warning("Used fallback formatting (LLM unavailable)")

        # Apply same post-processing for HTML formatting
        return self._post_process_output(output)
