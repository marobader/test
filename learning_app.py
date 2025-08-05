from typing import List, Dict, Tuple

from transliterate import translit


class LearningApp:
    """A minimal implementation of the Birkenbihl inspired learning app."""

    def __init__(self):
        # vocabulary: word -> translation
        self.vocab: Dict[str, str] = {}
        # transliterations: word -> transliteration
        self.transliterations: Dict[str, str] = {}

    def add_text(self, text: str, lang: str) -> List[List[str]]:
        """Split text into lines and words, store transliterations."""
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        tokenized: List[List[str]] = []
        for line in lines:
            words = line.split()
            tokenized.append(words)
            for word in words:
                if word not in self.vocab:
                    self.vocab[word] = None
                    # translit returns in user's language when reversed
                    try:
                        self.transliterations[word] = translit(word, lang, reversed=True)
                    except Exception:
                        # if transliteration not supported, store original
                        self.transliterations[word] = word
        return tokenized

    def set_translation(self, word: str, translation: str) -> None:
        """Add or update translation for a word."""
        self.vocab[word] = translation

    def get_vocabulary(self) -> Dict[str, Dict[str, str]]:
        """Return vocabulary with translations and transliterations."""
        return {
            word: {
                "translation": self.vocab[word],
                "transliteration": self.transliterations.get(word, word),
            }
            for word in self.vocab
        }

    def suggest_text(self, texts: List[Tuple[str, str]]) -> List[Tuple[str, float]]:
        """Rank candidate texts by coverage of known vocabulary."""
        suggestions = []
        for text, lang in texts:
            words = set(text.split())
            if not words:
                suggestions.append((text, 0.0))
                continue
            known = sum(1 for w in words if self.vocab.get(w))
            coverage = known / len(words)
            suggestions.append((text, coverage))
        # sort by coverage descending
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions
