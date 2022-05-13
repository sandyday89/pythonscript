# this is test python script
# import required module
import os
# assign directory
directory = 'testdir'

# iterate over files in
# that directory
def main():
    for root, subdirectories, files in os.walk(directory):
            for file in files:
                with open(os.path.join(root, file), 'r') as f:
                    filedata = f.read()
                # Replace the target string
                filedata = filedata.replace('hellothisistest','willbedone')
                with open(os.path.join(root, file), 'w') as f:
                    f.write(filedata)

if __name__ == '__main__':
    main()