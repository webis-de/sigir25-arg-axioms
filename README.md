# Axiomatic Re-Ranking for Argument Retrieval

In this paper, four new argumentative axioms are introduced. These axioms consider the similarity of document sentences—specifically argument units—with respect to the query.

## Experiments

The experiments involve a re-ranking of the Dirichlet-LM baseline from the 2020 and 2021 editions of the Touche Shared Task on Argument Retrieval. Additionally, we re-rank the participant submissions for Touche 2021 to demonstrate that the axioms can improve systems that already outperform the Dirichlet-LM baseline.

## Code Structure

Due to difficulties with conflicting Python packages, the code is divided into two parts:

1. **Socket Server**  
   Acts as a database for the embeddings. In additition to the requirement stated in requirements_socket.txt, you have to download the spacy corpus with
    `python -m spacy download en_core_web_lg`
        We used python 3.10
2. **Argument Re-Ranking**  
   Uses `ir_axioms` to perform the argument re-ranking. We used python 3.8





