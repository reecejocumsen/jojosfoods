import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from jojosfoods import settings
print(Path(__file__).resolve().parent.parent)
print(os.path.join(settings.BASE_DIR, "static\\img\\no-pic.png"))
