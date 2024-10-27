from collections.abc import Iterator

from nltk.tokenize import PunktTokenizer


class Localizer:
    def __init__(self, text: str, lang: str = "english"):
        """
        :param text: The text to be tokenized.
        :param lang: The language for the Punkt Tokenizer. Defaults to "english".
        """

        self.text = text

        self.tokenizer = PunktTokenizer(lang=lang)

        self.spans = list(self.tokenizer.span_tokenize(text))

    def iter_sentences(self, n_sentences: int = 3) -> Iterator[tuple[str, tuple[int, int], list[tuple[int, int]]]]:
        """
        :param n_sentences: Number of sentences to iterate over at a time. Must be greater than 0.
        :return: An iterator yielding a tuple containing the combined text of the sentences,
                 a tuple with the start and stop positions of the text,
                 and a list of tuples with the spans of each sentence.
        """

        if n_sentences < 1:
            raise ValueError("Cannot have less than 1 sentence per window.")

        current_index = 0

        while True:
            spans = self.spans[current_index:current_index + n_sentences]

            start = spans[0][0]
            stop = spans[-1][1]

            yield self.text[start:stop], (start, stop), spans

            current_index += 1

            if current_index + n_sentences > len(self.spans):
                break
