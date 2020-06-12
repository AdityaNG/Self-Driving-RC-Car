import os
import shutil

def compile_training_data():
        print('Compiling Training Data')
        td = os.path.join(os.getcwd(), 'training_data')
        folders = [ name for name in os.listdir(td) if os.path.isdir(os.path.join(td, name)) ]
        files = [ name for name in os.listdir(td) if str(name).endswith(".zip") ]
        for i in folders:
                if i+".zip" not in files:
                        #print("\t Compiling : ", i)
                        shutil.copyfile("player.py", os.path.join(os.getcwd(), 'training_data', i, "player.py"))
                        c_dir = os.path.join(os.getcwd(), 'training_data', i)
                        shutil.make_archive(c_dir, 'zip', c_dir)
        #print("Done Compiling data")


compile_training_data()
