import properties
import os
import time


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_created_time(filename):
    file_info = os.stat(filename)
    file_fist_date = file_info.st_mtime if file_info.st_mtime <= file_info.st_ctime else file_info.st_mtime
    return time.strftime('%Y-%m-%d', time.localtime(file_fist_date))


def get_list_of_files(directory, files):
    if not os.path.exists(directory):
        print(f'Directory "{directory}" does not exist')
        exit(1)

    for (dir_path, dir_names, filenames) in os.walk(directory):
        filenames = [os.path.splitext(filename) for filename in filenames]

        files += [
            {'dir': dir_path,
             'filename': ''.join(filename),
             'dir_filename': os.path.join(dir_path, ''.join(filename)),
             'name': filename[0],
             'ext': filename[1],
             'created_at': get_created_time(os.path.join(dir_path, ''.join(filename)))
             } for filename in filenames
        ]


def check_extensions(files):
    for file in files:
        if file['ext'].lower() in properties.junk_extensions:
            print(f'Moving {file["dir_filename"]} to {properties.junk_directory}')
            os.replace(
                file["dir_filename"],
                os.path.join(properties.junk_directory, file["filename"])
            )
        elif file['ext'].lower() not in properties.img_extensions + properties.video_extensions:
            print(f'Extension not found => {file["dir_filename"]}')

    return [file for file in files if file['ext'].lower() not in properties.junk_extensions]


def move_file(file, to_dir):
    try:
        os.rename(file['dir_filename'], to_dir)
    except FileNotFoundError:
        print(f'File {file["dir_filename"]} not found')
    except FileExistsError:
        print(f'File {file["filename"]} exists in {to_dir}')


def move_files(files):
    for file in files:

        date_dir = os.path.join(properties.new_directory, file["created_at"])
        create_directory(date_dir)

        if file['ext'].lower() in properties.img_extensions:
            photo_dir = os.path.join(date_dir, 'photos')
            create_directory(photo_dir)
            move_file(file, os.path.join(photo_dir, file['filename']))

        elif file['ext'].lower() in properties.video_extensions:
            video_dir = os.path.join(date_dir, 'videos')
            create_directory(video_dir)
            move_file(file, os.path.join(video_dir, file['filename']))


if __name__ == '__main__':
    files = []

    for directory in [properties.new_directory, properties.junk_directory]:
        create_directory(directory)

    for directory in properties.directories:
        get_list_of_files(directory, files)

    # Perform a set to a list of dictionaries to avoid
    # duplicates in case one of the indicated directories is a child of another
    files = list(map(dict, frozenset(frozenset(i.items()) for i in files)))

    files = check_extensions(files)

    move_files(files)

    exit(0)
