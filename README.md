# 📅 Event Tracking – Personal Dashboard powered by LLMs

> A side project to track events, reflections, and personal goals, while experimenting with LLMs and modern Python libraries.

## 🎯 Project Goal

Event Tracking is a mini application designed to help me:
- Keep track of my daily activities and personal goals.
- Visualize and analyze how I'm evolving over time.
- Experiment with and learn how to use **Large Language Models (LLMs)** and modern libraries in a meaningful personal project.

## 💡 Key Features

- **Event Calendar**: log daily activities with notes.
- **Weekly / Monthly Reviews**: reflect on productivity and energy levels.
- **Multi-Scale Planning**: define focus and goals across daily, monthly, and yearly horizons.
- **Interactive Dashboard**: visualize activities by category and energy levels.
- **LLM Integration** *(work in progress)*: generate automatic insights and summaries from logged events.

## 🧰 Tech Stack

- [Streamlit](https://streamlit.io/) → for building the interactive user interface
- [LangChain](https://www.langchain.com/) → to orchestrate interactions with LLMs
- [DuckDB](https://duckdb.org/) → for lightweight local data storage and querying
- [UV](https://docs.astral.sh/uv/) → An extremely fast Python package and project manager, written in Rust.

## 🛠️ Project Status

⚠️ **In early development (alpha)**  
The main goal is to explore and learn, so the codebase will evolve iteratively with frequent experiments and refactoring.

## 🧪 Learning Objectives

- Apply **LLM integration** in mini-apps.
- Learn and experiment with **LangChain**, **DuckDB**, **Streamlit**.
- Build a personal dashboard that is useful and sustainable over time.

## 🧱 Next Steps

- [ ] Define data structure for events
- [ ] Set up base Streamlit app
- [ ] Automatic event parsing and categorization using LLM
- [ ] Visualization of goal progression over time

## 📂 Proposed Repository Structure

```
├── README.md
├── data
|   ├── raw                          <- The original, immutable data dump.
│   ├── processed                    <- The final, canonical data sets for modeling.
│
├── development                      <- Jupyter notebooks and Python Scripts. Naming convention to be defined
│
├── reports                          <- Generated analysis as XLSX, HTML, PDF, LaTeX, etc.
│
└── {{ cookiecutter.module_name }}   <- Source code for use in this project.
    ├── __init__.py                  <- Makes {{ cookiecutter.module_name }} a Python module
    │
    ├── config.py                    <- Store useful variables and configuration
```