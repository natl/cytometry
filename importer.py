'''
Import files from import directory to files directory.
Adds fcs file extension.
'''
import os


def import_files():
    import_files = os.listdir('import')
    output_files = os.listdir('files')

    for inname in import_files:
        if inname in output_files:
            print(inname + " is already in ./files/, skipping...")
        else:
            if inname[-4:] == ".fcs":
                outname = inname
            else:
                outname = inname + ".fcs"
            infile = file("import/" + inname, 'r')
            outfile = file("files/" + outname, 'w')
            print("Importing import/{0} as files/{1}".format(inname, outname))
            for ii, line in enumerate(infile):
                if ii == 0:
                    line = line.replace("\xaa", " ")
                outfile.write(line)
            infile.close()
            outfile.close()

if __name__ == "__main__":
    import_files()
