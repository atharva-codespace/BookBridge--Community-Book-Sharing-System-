"""
services/ai_recommendation.py
Feature 2: AI Book Recommendation. Shown to a Buyer right before Browse &
Search Books, this builds the buyer's history - wishlist, previously
requested/purchased books, favourite categories & authors inferred from
that history, and books they've donated or listed for exchange as an owner
- straight from the same SQLite tables every other service already reads
(models/wishlist.py, models/book_request.py, models/book.py). That history,
plus the list of currently available books (each with a real Book_ID), is
sent to the AI fallback chain (Gemini -> Groq -> OpenRouter -> Cerebras,
see ai_client.py) with strict instructions to recommend ONLY from that
candidate list - the AI is never given the freedom to invent a book that
doesn't exist in the database. If there isn't enough history, or every
provider is unavailable, a rule-based fallback recommends from the buyer's
favourite/available categories instead.
"""

import json
from collections import Counter

from models.book import Book
from models.book_request import BookRequest
from models.wishlist import Wishlist
from services.ai_client import ask_ai
from utils import ui

MAX_RECOMMENDATIONS = 3
MAX_CANDIDATES_SENT_TO_AI = 40  # keeps the prompt small even with a large catalog

SYSTEM_PROMPT = """
You are the AI Book Recommendation engine for BookBridge. You will be
given (1) a buyer's history and (2) a list of
CANDIDATE books that currently exist and are available in the database,
each with a Book_ID. Recommend at most 3 books for this buyer.

Rules:
- You may ONLY recommend books from the CANDIDATE list below. Never invent
  a title, author, or Book_ID that isn't in that list.
- Prefer books matching the buyer's favourite categories/authors, wishlist,
  or past purchases/donations/exchanges over random picks.
- If the history is thin or empty, recommend well-known/available
  candidates and say so honestly in the reason (e.g. "Popular choice in the
  Programming category").
- Respond with ONLY a JSON array, no other text before or after it, in
  exactly this shape:
  [{"book_id": 12, "reason": "You previously bought Python books."}]
- Keep each reason under 15 words.
""".strip()


def _get_available_candidates():
    """Real, currently available books - the only pool the AI is allowed to
    recommend from. Capped so the AI prompt stays a reasonable size."""
    books = [b for b in Book.get_all() if b.availability == "Available"]
    return books[:MAX_CANDIDATES_SENT_TO_AI]


def _build_history(user_id):
    """Pulls this buyer's history from the existing tables/models. Every
    piece is best-effort - if a table has no rows yet (e.g. no purchases),
    that section is simply left out of the prompt instead of erroring out.
    NOTE: previous searches aren't currently persisted anywhere in the
    database, so that signal is intentionally omitted until a search-log
    table exists."""
    history = {}

    wishlist = Wishlist.get_by_user(user_id)
    if wishlist:
        history["wishlist_titles"] = [w.book_title for w in wishlist]

    requests = BookRequest.get_sent_by_user(user_id)
    purchased_titles = [r.book_name for r in requests if r.status == "Approved"]
    if purchased_titles:
        history["purchased_titles"] = purchased_titles

    # Favourite categories/authors, inferred from purchases + wishlist
    # titles that still resolve to a real Books row.
    referenced_titles = purchased_titles + history.get("wishlist_titles", [])
    categories, authors = [], []
    for title in referenced_titles:
        book = Book.search_book(title)
        if book:
            categories.append(book.category)
            authors.append(book.author)
    if categories:
        history["favourite_categories"] = [c for c, _ in Counter(categories).most_common(3)]
    if authors:
        history["favourite_authors"] = [a for a, _ in Counter(authors).most_common(3)]

    # Books this user has donated or listed for exchange as an owner.
    owned = Book.get_by_owner(user_id)
    donated_or_exchanged = [b.title for b in owned if b.listing_type in ("Donation", "Exchange")]
    if donated_or_exchanged:
        history["donated_or_exchanged_titles"] = donated_or_exchanged

    return history


def _fallback_recommendations(candidates, history):
    """Used when every AI provider is unavailable or returns something
    unusable. Ranks the real candidate books by favourite category, then
    author, then just takes the most recent listings - always from the real
    database, never invented."""
    favourite_categories = set(history.get("favourite_categories", []))
    favourite_authors = set(history.get("favourite_authors", []))

    def score(book):
        s = 0
        if book.category in favourite_categories:
            s += 2
        if book.author in favourite_authors:
            s += 1
        return s

    ranked = sorted(candidates, key=score, reverse=True)
    picks = []
    for book in ranked[:MAX_RECOMMENDATIONS]:
        if book.category in favourite_categories:
            reason = f"Matches your {book.category} interests."
        elif book.author in favourite_authors:
            reason = f"You've shown interest in books by {book.author}."
        else:
            reason = "A currently available book you might like."
        picks.append({"book": book, "reason": reason})
    return picks


def _ask_ai_for_recommendations(candidates, history):
    """Sends history + candidate list to the AI fallback chain, expecting a
    JSON array of {book_id, reason} back. Returns None on any failure (every
    provider unavailable, unparsable reply, or every returned book_id being
    invalid) so the caller falls back to the rule-based picks instead."""
    candidate_lines = [
        f'Book_ID={b.book_id} | "{b.title}" by {b.author} | Category: {b.category}'
        for b in candidates
    ]
    prompt = (
        f"BUYER HISTORY:\n"
        f"{json.dumps(history, indent=2) if history else '(no history yet - new buyer)'}\n\n"
        f"CANDIDATE BOOKS (recommend ONLY from this list):\n" + "\n".join(candidate_lines)
    )

    with ui.spinner("Finding books for you"):
        reply = ask_ai(SYSTEM_PROMPT, prompt, max_tokens=400)
    if reply is None:
        return None

    try:
        # The AI is instructed to return pure JSON, but strip any accidental
        # markdown code fences just in case.
        cleaned = reply.strip().strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        parsed = json.loads(cleaned)
    except (ValueError, TypeError):
        return None

    by_id = {b.book_id: b for b in candidates}
    picks = []
    for item in parsed:
        book = by_id.get(item.get("book_id"))
        if book is None:
            continue  # ignore any Book_ID the AI invented or mistyped
        picks.append({"book": book, "reason": item.get("reason", "Recommended for you.")})
        if len(picks) == MAX_RECOMMENDATIONS:
            break

    return picks or None


def show_recommendations(session):
    """Called right before Browse & Search Books for a logged-in Buyer.
    Prints up to 3 recommended books with a short reason each, then lets the
    caller show the normal Browse & Search Books screen. Does nothing if
    there are currently no available books to recommend."""
    try:
        candidates = _get_available_candidates()
        if not candidates:
            return

        history = _build_history(session.user_id)
        picks = _ask_ai_for_recommendations(candidates, history)
        if picks is None:
            picks = _fallback_recommendations(candidates, history)
        if not picks:
            return

        ui.recommendation_panel(
            "📚 Recommended For You",
            [(pick["book"].title, pick["reason"]) for pick in picks],
        )
    except Exception as e:
        # Recommendations are a bonus on top of Browse & Search Books - never
        # let a failure here block the buyer from browsing normally.
        ui.warning(f"Could not generate recommendations: {e}")
