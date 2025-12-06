#!/bin/env bash

cd /geometricalgebra/

source /venv/bin/activate
cd notebooks
jupytext --to ipynb displaymv.py
