#!/bin/bash
conda create --name myenv python=3.8.19 -y
source $(conda info --base)/etc/profile.d/conda.sh
conda activate myenv
pip install -r requirements.txt
read -p "Press any key to continue..."
