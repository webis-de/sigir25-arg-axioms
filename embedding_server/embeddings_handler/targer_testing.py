from typing import FrozenSet

from sentence_transformers import SentenceTransformer
from targer_api import ArgumentLabel, ArgumentSentences, ArgumentTag, analyze_text
from targer_api.constants import DEFAULT_TARGER_API_URL


def build_sentences(sentences: ArgumentSentences):
    return [" ".join([
        tag.token
        for tag in sentence
        if (_is_claim(tag) or _is_premise(tag))  and tag.probability > 0.5
    ])for sentence in sentences]
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

model = SentenceTransformer('all-mpnet-base-v2')
targer_model: str = "tag-webd-fasttext"
targer_models: FrozenSet[str] = frozenset({targer_model})

if __name__ == '__main__':

    a = ['to begin i would like to review a few points from the last few posts that have been made by both massrebut and i. after that, then i will end with my conclusion.', 'my argument will reiterate and add new and different points to bring to focus when looking at single-sex schools versus co-educational schools.', 'if massrebut was not implying or assuming that "single-sex schools are better for education," in the first statement of his previous post, i ask myself why he remains in the debate after negating his own line of logic.', 'looking at massrebut"s cited debate point (along with the title of our entire debate)', 'massrebut can realize the forfeit of his argument with the statement of "no where have i implied or assumed or even suggested that single sex schools are better for education".', 'when i stated, "there are no jobs that only hire one sex," this was an example to show that single-sex education is not the best for students because it does not prepare students for the co-ed work world.', 'to reiterate: there is not "one job" that accepts only males or only females.', 'two main purposes of us education are learning basic knowledge and socialization skills.', 'the working world includes interaction with both sexes.', 'in single-sex schools, the individual is only exposed to and socialized with one group.', 'students in single-sex schools are therefore prepared to work and cooperate with only one gender.', 'therefore, single-sex schools do not prepare students for the world of employment.', 'co-educational schools have the two purposes fulfilled (learning a basis of knowledge and socialization), whereas single-sex schools only include the knowledge base.', '"boys and girls are interested in each other and define themselves by it as stated by it as stated by dragonrule029', 'but they could try for the football team or for the musical for a million other reasons not just because they are interested.', 'they could also be doing it to impress someone or get the attention or to even become friends with someone, which proves my point correct which stated that students have different driving factors in co-ed schools and they deviate from their true paths just because the other sex is present.', 'even i agree that "not everything that is done in schools is meant to "show-off"" but is certainly influenced by the other sex and even that depends on how much interested they are or how much they like and want to impress each other which is not a good learning environment for them."', 'we have agreed that not all actions are done to show off, according to the quoted statement above.', 'although, i would like to point out that in massrebut"s first argument he said "every action of the student is because he wants to impress or show off to someone he likes in the school" and in the quotations above massrebut says: "even i agree that "not everything that is done in schools is meant to "show-off""" which is therefore contradicting and negates that part of the argument.', 'regarding influencing the opposite sex, since i have already negated where that statement began, massrebut can decide if he would like to pick up that piece of the argument again or not.', '----- "when dragonrule029 talks about homosexuality and how it will cause the same level of distraction as it will in co - education schools and students will be distracted no matter where they are, well this view is completely wrong.', 'well, because not all students are homosexual and there is a 1% chance that one or two students will be and', 'so how will this make other students distracted, the ones who are not involved and the ones who do not care?', 'in co-ed schools, everyone would be looking at each other and the level of distraction in these schools is incomparable to single sex schools and to homosexual students.', 'and what are the chances that there are not homosexuals in co-ed schools?"', 'this is yet another interpretation that was taken incorrectly, not to mention the fact that more than 1% of the student body could be homosexual or another type of sexual attraction.', 'studies have shown that 12% of students identify as homo']
    a = ' '.join(a)
    doc1 = analyze_text(a, model_or_models=targer_models, api_url=DEFAULT_TARGER_API_URL)
    doc_sent = [build_sentences(sentences) for _, sentences in doc1.items()]

    prox = []
    for _, sentences in doc1.items():
        x = build_sentences(sentences)
        prox.append(x)
    mewo = 1