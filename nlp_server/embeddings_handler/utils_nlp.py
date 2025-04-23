# create sentences
import spacy

class TextPreprocessor() :
    def __init__(self) :
        self.nlp = spacy.load("en_core_web_lg")

    def count_words(self , data_str) :
        # Process the text using spaCy
        doc = self.nlp(data_str)

        # Extract words (tokens) from the processed document
        words = [token.text for token in doc if token.is_alpha]
        return len(words)

    def filter_text(self,text) :
        if len(text) <= 5 : # very short sentences are removed
            return False
        return True

    def create_sentences(self , data_str) :
        single_sentences_final = []
        doc = self.nlp(data_str) # create sentences out of document
        for sent in doc.sents :
            sentence = sent.text
            if self.filter_text(sentence) :
                single_sentences_final.append(sentence)
        return single_sentences_final


if __name__ == '__main__' :
    a = """Regarding vegetarianism, the expert named James A. Fyfe argues that, "In a nutshell, vegetarianism is the refusal of eating meat, or any other animal, in preference to the use of any product that, at least in principle, uses less land, less water, and emits fewer greenhouse gas emissions than meat."
    According to Fyfe, this means that, "No more meat. No more dairy. No more eggs. No more wool, leather, fur, silk, or feathers. No more silk screen, leather or fur. While thi"""
    c = TextPreprocessor()
    sents = c.create_sentences(a)
    for x in sents :
        print(x)