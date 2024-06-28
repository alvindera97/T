#!/bin/bash

# Navigate to the Sphinx documentation directory
cd docs

# Clear previous Sphinx documentation build
make clean

# Build the Sphinx documentation
make html

# Navigate back to the root directory
cd .. || exit
