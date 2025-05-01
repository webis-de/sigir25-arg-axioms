from typing import FrozenSet

from loguru import logger
from targer_api import ArgumentLabel, ArgumentSentences, ArgumentTag, analyze_text
from targer_api.constants import DEFAULT_TARGER_API_URL

import settings as s

TARGER_MODEL: str = "tag-webd-fasttext"
TARGER_MODELS: FrozenSet[str] = frozenset({TARGER_MODEL})


def build_argument(tagged_parts: ArgumentSentences):
    argu_sentences = [tag.token for tag in tagged_parts if (_is_claim(tag) or _is_premise(tag))  and tag.probability > 0.5]

    return ' '.join(argu_sentences)

def _is_claim(tag: ArgumentTag) -> bool:
    return (
            tag.label == ArgumentLabel.C_B or
            tag.label == ArgumentLabel.C_I or
            tag.label == ArgumentLabel.MC_B or
            tag.label == ArgumentLabel.MC_I
    )

def _is_premise(tag: ArgumentTag) -> bool:
    return (
            tag.label == ArgumentLabel.P_B or
            tag.label == ArgumentLabel.P_I or
            tag.label == ArgumentLabel.MP_B or
            tag.label == ArgumentLabel.MP_I
    )

def get_targer_annotation(document, task_info_dict=None):
    targer_own_sentencizer = False
    if task_info_dict is not None:
        targer_own_sentencizer = task_info_dict.get(s.TASK_INFO_TARGER_OWN_SENTENICER, False)

    if targer_own_sentencizer:
        data = get_targer_annotation_full_document(document)

    else:
        raise Exception("This function is not implemented")
        # data = get_targer_annotation_single_sentence_control(document)

    assert isinstance(data,list)

    data = [item for item in data if filter_targer(item)]
    if len(data) == 0:
        data = [" "]
    return data

def filter_targer(text):
    if len(text) <= 5:
        return False
    return True

def get_targer_annotation_full_document(document) : # get the Targer annotations for the full document
    final_annotations = []
    if isinstance(document,list):
        document = ' '.join(document)

    analyzed_doc = call_targer_api(document)
    if analyzed_doc is None :
        return final_annotations

    argument_sentences = [build_argument(tagged_parts) for tagged_parts in analyzed_doc[TARGER_MODEL]]
    final_annotations.extend(argument_sentences)
    return final_annotations

# def get_targer_annotation_single_sentence_control(document):
#     assert isinstance(document, list)
#     final_annotations = get_targer_annotation_single_document_sentences(document)
#     return final_annotations


def call_targer_api(document) :
    current_try = 0
    analyzed_doc = None

    while current_try < s.TARGER_TOTAL_TRIES :
        try :
            analyzed_doc = analyze_text(document, model_or_models=TARGER_MODELS, api_url=DEFAULT_TARGER_API_URL)
            break
        except ValueError as e :
            logger.error(f"Error in Targer API: {e}, Sentence: {document}")
            current_try += 1
    return analyzed_doc


def get_targer_annotation_single_document_sentences(document):
    final_annotations = []

   # raise Exception("This function is not implemented")
    for sentence in document:

        analyzed_doc = call_targer_api(sentence)
        if analyzed_doc is None:
            continue

        argument_sentences = [build_argument(tagged_parts) for tagged_parts in analyzed_doc[TARGER_MODEL]]
        if len(argument_sentences) > 1:
            logger.info(f"Multiple arguments detected in sentence: {sentence}")
        argument = ' '.join(argument_sentences)
        if argument.isspace():
            argument = ""
        final_annotations.append(argument)
    return final_annotations

if __name__ == '__main__':

    test_string ="hello, this is my first debate. i wish good luck to my opponents.commenters please advice me in the comments section and thank you!so let's get started.point 1:school uniform can be a indication of the student's pride and loyalty of the school. by wearing school uniform, students will feel proud of their school. however, this only applies if the school is reputable as if the school is not reputable....."
    task = {s.TASK_INFO_TARGER_OWN_SENTENICER : True}
    y = get_targer_annotation(test_string, task_info_dict=task)
