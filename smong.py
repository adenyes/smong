from pathlib import Path

import click


def frame_generator(src_avi_file) -> bytes:
    frame_buffer = bytearray()
    read_size = 4096
    with open(src_avi_file, 'rb') as fp:
        raw_data = fp.read(read_size)
        next_possible = 0
        while raw_data:
            frame_buffer.extend(raw_data)
            while True:
                split_index = frame_buffer.find(b'00dc', next_possible)
                if split_index >= 0:
                    yield frame_buffer[:split_index + 4]
                    frame_buffer = frame_buffer[split_index + 4:]
                    next_possible = 0
                else:
                    break
            next_possible = len(frame_buffer) - 4
            raw_data = fp.read(read_size)
        yield frame_buffer


def is_iframe(raw_frame):
    return raw_frame[5:8] == bytes.fromhex('0001B0')


@click.group()
def smong():
    pass


@smong.command()
@click.argument('src_avi_file', type=click.Path(exists=True, dir_okay=False))
@click.option('repeat', '-r', type=click.INT, default=24)
def pcopy(src_avi_file, repeat):
    src_path = Path(src_avi_file)
    dst_path = src_path.parent / (src_path.stem + "_copied" + src_path.suffix)
    frame_count = 0
    iframe_count = 0
    with dst_path.open('wb') as dst:
        seen_iframe = False
        for frame in frame_generator(src_avi_file):
            frame_count += 1
            if is_iframe(frame):
                iframe_count += 1
                if seen_iframe:
                    continue
                else:
                    seen_iframe = True
            else:
                for i in range(repeat):
                    dst.write(frame)

            dst.write(frame)

    click.echo(
        f"Processed {frame_count} frames, skipped {iframe_count} iframes.")


@smong.command()
@click.argument('src_avi_file', type=click.Path(exists=True, dir_okay=False))
def ikill(src_avi_file):
    src_path = Path(src_avi_file)
    dst_path = src_path.parent / (src_path.stem + "_killed" + src_path.suffix)

    if src_path.suffix != ".avi":
        click.echo("Warning: source file doesn't have an .avi extension. "
                   "This program is only expecting AVI file inputs.")
        # TODO: convert to AVI as needed

    frame_count = 0
    iframe_count = 0
    with dst_path.open('wb') as dst:
        seen_iframe = False
        for frame in frame_generator(src_avi_file):
            frame_count += 1
            if is_iframe(frame):
                iframe_count += 1
                if seen_iframe:
                    continue
                else:
                    seen_iframe = True
            dst.write(frame)

    click.echo(
        f"Processed {frame_count} frames, skipped {iframe_count} iframes.")


if __name__ == '__main__':
    smong()

