import os
import shutil

def compile_training_data():
        return
        print('Compiling Training Data')
        td = os.path.join(os.getcwd(), 'training_data')
        folders = [ name for name in os.listdir(td) if os.path.isdir(os.path.join(td, name)) ]
        for i in folders:
                print("\t Compiling : ",i)
                c_dir = os.path.join(os.getcwd(), 'training_data', i)
                shutil.make_archive(c_dir, 'zip', c_dir)
        print("Done Compiling data")


compile_training_data()
