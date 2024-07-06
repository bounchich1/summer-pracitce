#!/bin/bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate myenv
pip install -r requirements.txt
read -p "Нажмите любую клавишу чтобы продолжить..."