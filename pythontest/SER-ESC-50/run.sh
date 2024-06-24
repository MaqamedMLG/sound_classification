#!/bin/bash

# Temporary workaround for OpenMP duplicate library error
export KMP_DUPLICATE_LIB_OK=TRUE

# Check to see if ESC-50-master directory exists in the current directory
if [ -d "ESC-50-master" ]; then
    # If it does - train both models and generate comparative predictions
    python train.py
    python predict.py
else
    # If it does not - fetch the necessary data
    # Train both models and generate comparative predictions
    bash fetch_data.sh
    python train.py
    python predict.py
fi
