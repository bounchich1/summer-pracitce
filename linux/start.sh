#!/bin/bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate myenv
python main.py
read -p "Нажмите любую кнопку чтобы продолжить..."