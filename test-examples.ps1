./venv/Scripts/Activate.ps1
mkdir -p .temp/
cd .temp

cp -r ../src/* .
cp -r ../examples/* .

echo "Testing example 1..."
python example_1.py
echo "Success!, Testing example 2..."
python example_2.py
echo "Success!, Testing example 3..."
python example_3.py
echo "Success! All examples passed, removing temporary files..."

cd ..
rm -r ./.temp/