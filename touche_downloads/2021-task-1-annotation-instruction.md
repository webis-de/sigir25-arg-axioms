# Touché Task 1: Argument Retrieval for Controversial Questions

The goal of Task 1 is to support users who search for arguments to be used in conversations (e.g., getting an overview of pros and cons or just looking for arguments in line with a user's stance). Given a question on a controversial topic, the task is to retrieve relevant arguments from a focused crawl of online debate portals.

Each controversial search task is represented as a topic, where the *title* is a controversial question.

## 1. Read topic
For each topic, please read its title carefully.

## 2. Read document
Read the document and document title.

## 3. Annotate relevance
Annotate the document's relevance for the topic:
   
| Label | Title | Rule of thumb |
| --- | --- | --- |
| R-2 | highly relevant | Would definitely help in a discussion of/on the topic. |
| R-1 | relevant | Some (small) argumentative info that helps for the topic. Also contains some arguments that are off topic. |
| R-0 | not relevant | Does not contain any info about the topic discussion, but is an argument. |
| R-X | not an argument | Is not an argument, e.g., does not contain claims/premises. |

## 4. Annotate quality
###### Description
Annotate the rhetorical quality, i.e. "well-writtenness" of the document (regardless of its relevance).
   - Does the text have a good style of speech? Informal is regared inferior to formal language.
   - Does it have proper sentence structure, and is easy to read?
   - Does it include informal speech, profanity, has typos, and makes use of other detrimental style choices?

###### Examples
> "Gender is a social construct cuse we are told when weare first born by a dude what gender but if he didnt tellus that we woudnt have a gender its only cuse he told us that gender that we are that gender." (Topic: Is gender a social construct?)

The above argument, while factually sound, is of *low* rhetorical quality, as it lacks proper sentence structure, uses informal speech, has typos, and its use of ellipsis makes it hard to follow.

> "Callout culture gives a voice to disenfranchised or less powerful people. It is a way to acknowledge that you don’t have to have the power to change structural inequality. You don’t even have to have the power to change all of public sentiment. But for many individuals, it is the first time they do have a voice in those types of conversations." (Topic: Is Cancel Culture (or “Callout Culture”) Good for Society?)

The above argument is an example of *high* rhetorical quality, as it is presented in formal language, well-structured and written in a way that is easily understandable, and orthographically correct.

###### Labels

| Label | Title | Rule of thumb |
| --- | --- | --- |
| Q-2 | high quality | The text fulfills all the above criteria sufficiently, i.e., proper language, well-structured, little grammar issues, easy to follow |
| Q-1 | medium quality | The text fulfills only some of the above criteria, or only to a limited degree, e.g., proper language but broken logic / hard to follow |
| Q-0 | low quality | The text does not fulfill the above criteria or is not argumentative at all, e.g., profanity, hard to follow, hard to read |

