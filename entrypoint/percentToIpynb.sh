#!/bin/env bash

cd /gacalc/

source /venv/bin/activate
cd notebooks
jupytext --to ipynb displaymv.py
