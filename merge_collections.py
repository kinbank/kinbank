import glob
import os
from shutil import move
from pathlib import Path

def move_files(filenames):
    new_filenames =  ['./' + f[20:] for f in filenames]
    for old, new in zip(filenames, new_filenames):
        print(old + "  " + os.path.dirname(new))
        if not os.path.isdir(os.path.dirname(new)):
            Path(os.path.dirname(new)).mkdir(parents=True, exist_ok=True)
        move(old, new)

## Varikin
print("Copying Varikin")
varikin_files = glob.glob("collections/varikin/kinbank/raw/**/*.csv", recursive=True)
move_files(varikin_files)

# ## Parabank
print("Copying Parabank")
parabank_files = glob.glob("collections/parabank/kinbank/raw/**/*.csv", recursive=True)
move_files(parabank_files)

## Goeldi
print("Copying Goeldi")
goedldi_files = glob.glob("collections/goeldi/kinbank/raw/**/*.csv", recursive=True)
move_files(goedldi_files)

## Kinura
print("Copying Kinura")
kinura_files = glob.glob("collections/kinura/kinbank/raw/**/*.csv", recursive=True)
move_files(kinura_files)

