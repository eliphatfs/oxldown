import objaverse.xl as oxl


def get_repo_id_with_hash(item):
    org, repo = item["fileIdentifier"].split("/")[3:5]
    commit_hash = item["fileIdentifier"].split("/")[6]
    return f"{org}/{repo}/{commit_hash}"


if __name__ == '__main__':
    anno = oxl.get_annotations()
    repos = anno[anno['source'] == 'github'].apply(get_repo_id_with_hash, axis=1)
    breakpoint()
    res = oxl.download_objects(anno[anno['source'] == 'smithsonian'].iloc[0:1], processes=1, save_repo_format='files')
    print(res)
    breakpoint()
