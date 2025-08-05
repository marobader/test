from typing import List, Dict, Tuple, Optional

from transliterate import translit
from difflib import SequenceMatcher
from googletrans import Translator


class LearningApp:
    """A minimal implementation of the Birkenbihl inspired learning app."""

    def __init__(self):
        # vocabulary: word -> translation
        self.vocab: Dict[str, Optional[str]] = {}
        # transliterations: word -> transliteration
        self.transliterations: Dict[str, str] = {}
        # stored texts
        self.texts: List[Dict] = []
        # cache for reference translations
        self.references: Dict[str, str] = {}
        self.translator = Translator()

    def add_text(self, text: str, lang: str) -> int:
        """Split text, store transliterations and return text id."""
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        tokenized: List[List[str]] = []
        for line in lines:
            words = line.split()
            tokenized.append(words)
            for word in words:
                if word not in self.vocab:
                    self.vocab[word] = None
                    try:
                        self.transliterations[word] = translit(word, lang, reversed=True)
                    except Exception:
                        self.transliterations[word] = word
        text_id = len(self.texts) + 1
        self.texts.append({"id": text_id, "text": text, "lang": lang, "tokens": tokenized})
        return text_id

    def list_texts(self) -> List[Dict]:
        """Return stored texts."""
        return self.texts

    def get_text(self, text_id: int) -> Dict:
        return next(t for t in self.texts if t["id"] == text_id)

    def text_progress(self, text_id: int) -> Tuple[int, int]:
        entry = self.get_text(text_id)
        words = [w for line in entry["tokens"] for w in line]
        total = len(words)
        done = sum(1 for w in words if self.vocab.get(w))
        return done, total

    def get_reference(self, word: str, src: str, dest: str) -> str:
        """Return reference translation for a word using googletrans."""
        if word not in self.references:
            try:
                self.references[word] = self.translator.translate(word, src=src, dest=dest).text
            except Exception:
                self.references[word] = ""
        return self.references[word]

    def translation_status(self, word: str, user_translation: Optional[str], src: str, dest: str) -> str:
        """Return correctness status for a translation."""
        if not user_translation:
            return "neutral"
        reference = self.get_reference(word, src, dest)
        if not reference:
            return "neutral"
        ratio = SequenceMatcher(None, user_translation.lower(), reference.lower()).ratio()
        if ratio > 0.8:
            return "correct"
        if ratio > 0.5:
            return "almost"
        return "wrong"

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
