# Data Processing Project

Python project for data validation, processing and analysis using pandas.

## Features

- Generate synthetic transaction data
- Validate CSV files
- Process and transform datasets
- Analyze revenue metrics
- Save processed results
- Automated testing with pytest

## Project Structure

bash src/ ├── models/ ├── processors/ ├── utils/ ├── validators/  tests/ data/ 

## Installation

Create virtual environment:

bash python3 -m venv .venv source .venv/bin/activate 

Install dependencies:

bash pip install -r requirements.txt 

## Run Project

bash python3 -m src.main 

## Run Tests

bash python3 -m pytest tests/ -v 

## Technologies

- Python
- Pandas
- NumPy
- Pytest
- Black

## Goal

Practice modular Python project structure, testing, and ETL-style data processing workflows.