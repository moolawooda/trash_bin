import os

files = os.listdir("./")

for file in files:
    if ".py" in file:
        srun = "nohup srun python3 < " + file + " > " + file[:-3] + ".out &"
        print(srun)
