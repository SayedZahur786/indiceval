---
license: cc-by-4.0
task_categories:
- text-generation
language:
- hi
tags:
- gsm8k
- hindi
pretty_name: Hindi GSM8K
size_categories:
- 1K<n<10K
---

## Dataset Description:
The GSM8K-Hi (Hindi GSM8K) is the GCP translated counterpart of the English GSM8K test set. The samples are carefully reviewed by the human annotators and corrected for quality improvement. These problems take between 2 and 8 steps to solve, and solutions primarily involve performing a sequence of elementary calculations using basic arithmetic operations (+ − ×÷) to reach the final answer.

This dataset is ready for commercial/non-commercial use. The evaluation steps are described [here](https://huggingface.co/datasets/nvidia/GSM8K-Hi/blob/main/EVAL.md). <br>
Other Hindi benchmark datasets: [ [IFEval-Hi](https://huggingface.co/datasets/nvidia/IFEval-Hi) | [MT-Bench-Hi](https://huggingface.co/datasets/nvidia/MT-Bench-Hi) | [GSM8K-Hi](https://huggingface.co/datasets/nvidia/GSM8K-Hi) | [BFCL-Hi](https://huggingface.co/datasets/nvidia/BFCL-Hi) | [ChatRAG-Hi](https://huggingface.co/datasets/nvidia/ChatRAG-Hi) ]

## Dataset Owner:
NVIDIA Corporation

## Dataset Creation Date:
April 2025

## License/Terms of Use: 
CC-BY 4.0

## Intended Usage:
This dataset is intended to evaluate the ability of language models to solve grade school-level math word problems that require multi-step reasoning.   

## Dataset Characterization
Data Collection Method<br>
* Synthetic <br>

Labeling Method<br>
* Not Applicable <br>

## Dataset Format
Text

## Dataset Quantification
1.6MB of question-answer pairs, comprising 1319 individual samples.

## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility, and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.   

Please report security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

## Citing

If you find our work helpful, please consider citing our paper:
```
@article{kamath2025benchmarking,
  title={Benchmarking Hindi LLMs: A New Suite of Datasets and a Comparative Analysis},
  author={Kamath, Anusha and Singla, Kanishk and Paul, Rakesh and Joshi, Raviraj and Vaidya, Utkarsh and Chauhan, Sanjay Singh and Wartikar, Niranjan},
  journal={arXiv preprint arXiv:2508.19831},
  year={2025}
}
```
