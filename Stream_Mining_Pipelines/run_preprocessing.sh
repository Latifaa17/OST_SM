python -m venv ./venv
./venv/Scripts/activate

pip install -r ./requirements_prep.txt

python Preprocessing.py >> preprocessing.log 2>&1 
