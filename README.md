# Arxiv Query Fluent

A Python library providing a fluent, intuitive, and chainable interface for easily building complex arXiv API queries, simplifying data retrieval and integration into your workflow.  
The project provides a convenient Python interface to build queries, display results, and download PDFs.  
This README provides examples to get you started and explains the query syntax, sorting, grouping, and pagination features.

## Usage

### Installation

```bash
$ pip install arxiv_query_fluent
```

In your Python script, include the line

```python
from arxiv_query_fluent import (
    Query,
    Field,
    Category,
    Opt,
    DateRange,
    SortCriterion,
    SortOrder
)
```

## Basic Query Example: Search Papers by Author

The following example demonstrates how to search all papers written by the author **"Stas Tiomkin"**.

```python
query = Query().add(Field.author, "Stas Tiomkin")
```

Then, run the query and inspect the results:

```python
result = query.get()
result.desc()
```

The output might look like:

```plain
Page Entries: 1-26 | Total Entries : 26 | Pages: 1 / 1
```

This output indicates:
- **Page Entries: 1-26**: The current page contains results 1 to 26.
- **Total Entries: 26**: A total of 26 papers were found.
- **Pages: 1 / 1**: All results are on one page.

To view detailed information for the first 3 papers (with abstracts truncated to 100 characters):

```python
result.show(top_n=3, abstract_shown=100)
```

Output:

```plain
Entries: 1-3/(26) | Pages: 1 / 1
───────────────────────────────────────────
Entry: #1
Title: Acoustic Wave Manipulation Through Sparse Robotic Actuation | arXiv Identifier: 2502.08784v2
Authors: Tristan Shah, Noam Smilovich, Feruza Amirkulova, Samer Gerges, Stas Tiomkin
Published Date: 2025-02-12 20:54:46+00:00
PDF Link: http://arxiv.org/pdf/2502.08784v2
Abstract:
Recent advancements in robotics, control, and machine learning have
facilitated progress in the chal...
───────────────────────────────────────────
Entry: #2
Title: Average-Reward Reinforcement Learning with Entropy Regularization | arXiv Identifier: 2501.09080v1
Authors: Jacob Adamczyk, Volodymyr Makarenko, Stas Tiomkin, Rahul V. Kulkarni
Published Date: 2025-01-15 19:00:46+00:00
PDF Link: http://arxiv.org/pdf/2501.09080v1
Abstract:
The average-reward formulation of reinforcement learning (RL) has drawn
increased interest in recent...
───────────────────────────────────────────
Entry: #3
Title: EVAL: EigenVector-based Average-reward Learning | arXiv Identifier: 2501.09770v1
Authors: Jacob Adamczyk, Volodymyr Makarenko, Stas Tiomkin, Rahul V. Kulkarni
Published Date: 2025-01-15 19:00:45+00:00
PDF Link: http://arxiv.org/pdf/2501.09770v1
Abstract:
In reinforcement learning, two objective functions have been developed
extensively in the literature...
───────────────────────────────────────────
```

To download the first paper, execute:

```python
result.download_pdf(identifier="2501.09080v1", dirpath="./")
```

**Parameter Explanation:**
- **identifier**: The arXiv identifier of the paper (e.g., "2501.09080v1").
- **dirpath**: The directory path where the PDF file will be saved.
- **filename** (Optional[str]): If not provided, the default filename will be `<identifier>.pdf` (e.g., "2501.09080v1.pdf").

Output:

```plain
'./2501.09080v1.pdf'
```

---

## Advanced Query: Combining Author and Subject Filters

To search for papers by **"Stas Tiomkin"** that also belong to the AI category:

```python
result = (
    Query(max_entries_per_pager=10)
    .add(Field.author, "Stas Tiomkin")
    .add(Field.category, Category.CS_AI, Opt.And)
    .get()
)
result.list()
```

**Explanation:**
- **Field.category**: This `category` field filters query results by the subject category of a paper. It corresponds to the 'cat' prefix in the arXiv API. For a complete list of fields, please refer to [Appendix A](#appendix-a).  
- **Category.CS_AI**: `CS_AI` Represents the `Computer Science - Artificial Intelligence` category. It filters the query to return only papers related to AI. For values that can be used with Field.category, please refer to the [arXiv category taxonomy](https://arxiv.org/category_taxonomy). The Category Enum in this project is built based on the current arXiv Category Taxonomy.

Output:

```plain
[2025-02-12] [Acoustic Wave Manipulation Through Sparse Robotic Actuation] [Tristan Shah,Noam Smilovich,Feruza Amirkulova,Samer Gerges,Stas Tiomkin]
[2025-01-15] [Average-Reward Reinforcement Learning with Entropy Regularization] [Jacob Adamczyk,Volodymyr Makarenko,Stas Tiomkin,Rahul V. Kulkarni]
[2025-01-15] [EVAL: EigenVector-based Average-reward Learning] [Jacob Adamczyk,Volodymyr Makarenko,Stas Tiomkin,Rahul V. Kulkarni]
[2025-01-02] [Bootstrapped Reward Shaping] [Jacob Adamczyk,Volodymyr Makarenko,Stas Tiomkin,Rahul V. Kulkarni]
[2024-11-20] [SuPLE: Robot Learning with Lyapunov Rewards] [Phu Nguyen,Daniel Polani,Stas Tiomkin]
[2024-06-26] [Boosting Soft Q-Learning by Bounding] [Jacob Adamczyk,Volodymyr Makarenko,Stas Tiomkin,Rahul V. Kulkarni]
[2024-06-20] [Learning telic-controllable state representations] [Nadav Amir,Stas Tiomkin,Angela Langdon]
[2023-11-27] [Taming Waves: A Physically-Interpretable Machine Learning Framework for Realizable Control of Wave Dynamics] [Tristan Shah,Feruza Amirkulova,Stas Tiomkin]
[2023-11-11] [Controllability-Constrained Deep Network Models for Enhanced Control of Dynamical Systems] [Suruchi Sharma,Volodymyr Makarenko,Gautam Kumar,Stas Tiomkin]
[2023-11-06] [Multi-Resolution Diffusion for Privacy-Sensitive Recommender Systems] [Derek Lilienthal,Paul Mello,Magdalini Eirinaki,Stas Tiomkin]
```

This example uses the `list()` method to display each paper's publication date, title, and authors.

The query syntax follows the structure:

```
Query().add(Field, Value).add(Field, Value, BooleanOperator)...get()
```

Where:
- **Field** is an Enum object.
- **Value** is a string or a DateRange object.
- **Boolean Operator** can be `And`, `Or`, or `AndNot`.

For more details on the supported fields by the arXiv API, please refer to [arXiv API documentation](https://info.arxiv.org/help/api/user-manual.html#51-details-of-query-construction).

---

## Sorting and Ordering Query Results

You can sort your query results by different criteria. For example, to sort by submitted date in ascending order and filter for AI papers with the keyword "DeepSeek":

```python
deepseek = (
    Query(sortBy=SortCriterion.SubmittedDate, sortOrder=SortOrder.Ascending)
    .add(Field.category, Category.CS_AI)
    .add(Field.all, "DeepSeek", Opt.And)
    .add(Field.submitted_date, DateRange("20240701", "20250228"), Opt.And)
    .get(1)
)
deepseek.show(3, abstract_shown=0)
```

Output:

```plain
Entries: 1-3/(50) | Pages: 1 / 3
───────────────────────────────────────────
Entry: #1
Title: Let the Expert Stick to His Last: Expert-Specialized Fine-Tuning for Sparse Architectural Large Language Models | arXiv Identifier: 2407.01906v2
Authors: Zihan Wang, Deli Chen, Damai Dai, Runxin Xu, Zhuoshu Li, Y. Wu
Published Date: 2024-07-02 03:11:13+00:00
PDF Link: http://arxiv.org/pdf/2407.01906v2
───────────────────────────────────────────
Entry: #2
Title: Let the Code LLM Edit Itself When You Edit the Code | arXiv Identifier: 2407.03157v2
Authors: Zhenyu He, Jun Zhang, Shengjie Luo, Jingjing Xu, Zhi Zhang, Di He
Published Date: 2024-07-03 14:34:03+00:00
PDF Link: http://arxiv.org/pdf/2407.03157v2
───────────────────────────────────────────
Entry: #3
Title: DotaMath: Decomposition of Thought with Code Assistance and Self-correction for Mathematical Reasoning | arXiv Identifier: 2407.04078v3
Authors: Chengpeng Li, Guanting Dong, Mingfeng Xue, Ru Peng, Xiang Wang, Dayiheng Liu
Published Date: 2024-07-04 17:39:16+00:00
PDF Link: http://arxiv.org/pdf/2407.04078v3
───────────────────────────────────────────
```

Alternatively, you can change the sorting criteria to sort by relevance in descending order:

```python
(
    Query(sortBy=SortCriterion.Relevance, sortOrder=SortOrder.Descending)
    .add(Field.category, Category.CS_AI)
    .add(Field.all, "DeepSeek", Opt.And)
    .add(Field.submitted_date, DateRange("20240701", "20250228"), Opt.And)
    .get(1)
    .show(3, 0)
)
```

Output:

```plain
Entries: 1-3/(50) | Pages: 1 / 3
───────────────────────────────────────────
Entry: #1
Title: DocPuzzle: A Process-Aware Benchmark for Evaluating Realistic Long-Context Reasoning Capabilities | arXiv Identifier: 2502.17807v1
Authors: Tianyi Zhuang, Chuqiao Kuang, Xiaoguang Li, Yihua Teng, Jihao Wu, Yasheng Wang, Lifeng Shang
Published Date: 2025-02-25 03:29:53+00:00
PDF Link: http://arxiv.org/pdf/2502.17807v1
───────────────────────────────────────────
Entry: #2
Title: A Comparison of DeepSeek and Other LLMs | arXiv Identifier: 2502.03688v2
Authors: Tianchen Gao, Jiashun Jin, Zheng Tracy Ke, Gabriel Moryoussef
Published Date: 2025-02-06 00:38:25+00:00
PDF Link: http://arxiv.org/pdf/2502.03688v2
───────────────────────────────────────────
Entry: #3
Title: DeepSeek-VL2: Mixture-of-Experts Vision-Language Models for Advanced Multimodal Understanding | arXiv Identifier: 2412.10302v1
Authors: Zhiyu Wu, Xiaokang Chen, Zizheng Pan, Xingchao Liu, Wen Liu, Damai Dai, Huazuo Gao, Yiyang Ma, Chengyue Wu, Bingxuan Wang, Zhenda Xie, Yu Wu, Kai Hu, Jiawei Wang, Yaofeng Sun, Yukun Li, Yishi Piao, Kang Guan, Aixin Liu, Xin Xie, Yuxiang You, Kai Dong, Xingkai Yu, Haowei Zhang, Liang Zhao, Yisong Wang, Chong Ruan
Published Date: 2024-12-13 17:37:48+00:00
PDF Link: http://arxiv.org/pdf/2412.10302v1
───────────────────────────────────────────
```

---

## Advanced Grouping Queries Combining Multiple Criteria

You can combine multiple queries using grouping and boolean operators. For example:

```python
group_1 = Query().add(Field.author, "Stas Tiomkin").add(Field.author, "Daniel Polani", Opt.And)
group_2 = Query().add(Field.title, "Dynamic", Opt.Or).add(Field.submitted_date, DateRange("20240101", "20241231"), Opt.Or)
query = Query().add_group(group_1).add_group(group_2, Opt.And_Not)
result = query.get()
result.desc()
```

Output:

```plain
Page Entries: 1-1 | Total Entries : 1 | Pages: 1 / 1
```

To display the details of the grouped query result:

```python
result.show()
```

Output:

```plain
Entries: 1-1/(1) | Pages: 1 / 1
───────────────────────────────────────────
Entry: #1
Title: AvE: Assistance via Empowerment | arXiv Identifier: 2006.14796v5
Authors: Yuqing Du, Stas Tiomkin, Emre Kiciman, Daniel Polani, Pieter Abbeel, Anca Dragan
Published Date: 2020-06-26 04:40:11+00:00
PDF Link: http://arxiv.org/pdf/2006.14796v5
Abstract:
One difficulty in using artificial agents for human-assistive applications
lies in the challenge of accurately assisting with a person's goal(s). Existing
methods tend to rely on inferring the human's...
───────────────────────────────────────────
```

---

## Efficient Pagination with Python Generators

The following example demonstrates how to iterate through paginated results using a Python generator:

```python
q = Query(max_entries_per_pager=10).add(Field.title, "transformer").add(Field.submitted_date, DateRange("20230101", "20230110"), Opt.And)
for page in q.paginated_results():
    page.desc()
```

Output:

```plain
Page Entries: 1-10 | Total Entries : 65 | Pages: 1 / 7
Page Entries: 11-20 | Total Entries : 65 | Pages: 2 / 7
Page Entries: 21-30 | Total Entries : 65 | Pages: 3 / 7
Page Entries: 31-40 | Total Entries : 65 | Pages: 4 / 7
Page Entries: 41-50 | Total Entries : 65 | Pages: 5 / 7
Page Entries: 51-60 | Total Entries : 65 | Pages: 6 / 7
Page Entries: 61-65 | Total Entries : 65 | Pages: 7 / 7
```

---

This project is designed with simplicity and flexibility in mind, enabling engineers—whether or not they are familiar with the arXiv API—to easily build and execute arXiv queries. Contributions, bug reports, and suggestions for improvement are very welcome!

For more details on query syntax and the supported fields, please refer to the [official arXiv API documentation](https://info.arxiv.org/help/api/user-manual.html#51-details-of-query-construction).

Happy querying!

---

## Appendix A: Field Enum Reference

| Field Enum          | ArXiv API Prefix | Explanation                  |
|---------------------|------------------|------------------------------|
| Field.abstract      | abs              | Abstract                     |
| Field.author        | au               | Author                       |
| Field.all           | all              | All of the above             |
| Field.category      | cat              | Subject Category             |
| Field.comment       | co               | Comment                      |
| Field.id            | id               | Id (use id_list instead)     |
| Field.journal_ref   | jr               | Journal Reference            |
| Field.title         | ti               | Title                        |
| Field.rn            | rn               | Report Number                |
| Field.submitted_date|                  | Submitted Date of the Paper  |

---

## Appendix B: Field.category Values

For values that can be used with `Field.category`, please refer to the [arXiv category taxonomy](https://arxiv.org/category_taxonomy). Note that in this project, `Field.category` corresponds to the `Category` Enum class, which is built based on the current arXiv Category Taxonomy.
