#!/bin/bash

# Navigate to the Sphinx documentation directory
cd docs || exit

# Build the docs .rst files
sphinx-apidoc -o source/ ../

# Build the Sphinx documentation
make html

# Navigate back to the root directory
cd .. || exit

# Check if there are any unstaged changes in the docs build directory
if [[ -n $(git status -s docs/build/html) ]]; then
    echo "Documentation needs rebuilding. Please stage the changes and commit again."
    exit 1
fi

exit 0
