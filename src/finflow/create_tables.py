# create_tables.py
import os

from sqlalchemy import create_engine

import models  # 确保模型被导入并注册
from db import Base


engine = create_engine(os.environ["DATABASE_URL"])
Base.metadata.create_all(engine)