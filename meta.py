import os
import objaverse.xl as oxl


oxl.get_annotations()
os.system(f"rclone --config rclone.conf copy {os.path.expanduser('~/.objaverse')} haosus3:objaverse-xl/meta")
