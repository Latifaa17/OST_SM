python -m venv ./venv
./venv/Scripts/activate

pip install -r ./requirements.txt

python Preprocessing.py >> preprocessing.log 2>&1 
