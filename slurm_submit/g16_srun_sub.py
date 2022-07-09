import os

files = os.listdir("./")

for file in files:
    if ".gjf" in file:
        srun = "nohup srun g16 < " + file + " > " + file[:-4] + ".out &"
        print(srun)
        
