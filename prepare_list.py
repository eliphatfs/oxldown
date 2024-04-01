import json
import objaverse.xl as oxl


def get_repo_id_with_hash(item):
    spl = item["fileIdentifier"].split("/")
    org, repo, commit_hash = spl[3], spl[4], spl[6]
    return f"{org}/{repo}/{commit_hash}"


def get_file_id_from_file_identifier(file_identifier: str) -> str:
    return file_identifier.split("fileId=")[-1]


if __name__ == '__main__':
    anno = oxl.get_annotations()

    thingi_fileid = anno[anno['source'] == 'thingiverse']['fileIdentifier'].apply(get_file_id_from_file_identifier).to_numpy().tolist()
    thingi = sorted({'thingiverse:' + x for x in thingi_fileid})

    smith_uri = anno[anno['source'] == 'smithsonian']['fileIdentifier'].to_numpy().tolist()
    smithsonian = sorted({'smithsonian:' + x for x in smith_uri})

    repos = anno[anno['source'] == 'github'].apply(get_repo_id_with_hash, axis=1).to_numpy().tolist()
    repos = sorted({'github:' + x for x in repos})

    all_list = repos + smithsonian + thingi
    with open("all_id_list.json", "w") as fo:
        json.dump(all_list, fo, indent=2)
