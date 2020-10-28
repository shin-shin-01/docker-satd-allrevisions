from setting import PATH_OF_GITCLONE, PATH_OF_GITLOGTXT, PATH_OF_ERROR_GITLOG, PATH_OF_GITLOGCSV, PATH_OF_GITSHOWLIST
from tqdm import tqdm
import subprocess
import os
import re
import pandas as pd



def command_ls(repository):
    command = f'ls'
    cwd = f'./{PATH_OF_GITCLONE}/{repository}/'

    # ignore utf-8 Error
    txt_ls_dir = subprocess.run(list(command.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore")
    txt_ls_dir = str(txt_ls_dir.stdout)

    return txt_ls_dir



if __name__ == "__main__":
    repositories = os.listdir(PATH_OF_GITCLONE)
    df = pd.DataFrame(columns=["project", "list", "InTemplate?"])

    for repository in tqdm(repositories):

        if repository == ".DS_Store":
            continue

        txt_ls_dir = command_ls(repository)

        search = re.search('.*Dockerfile.*template.*', txt_ls_dir)

        if search is None:
            in_template = 0
        else:
            in_template = 1
            
        df = df.append({ "project": repository ,"list": txt_ls_dir, "InTemplate?": in_template }, ignore_index=True)

    df.to_csv('b-searchTemplates/list.csv')

