import pandas as pd
from sqlalchemy import create_engine
import os


def gen_user_info_db():
    # DATABASE_URL = os.environ["DATABASE_URL"]
    data = {"department": ["学部"],
            "subject":["専攻"],
            "userid": ["1234567890"],
            }
    userid_df = pd.DataFrame(data)
    try:
        engine = create_engine("postgres://kpohefvamrmrbi:8063f7f969e8e2c09c8e50193c7cd7d5d2a3eff1051748f69330544e6e644d9f@ec2-52-202-146-43.compute-1.amazonaws.com:5432/d5748slr2bi4on")
        userid_df.to_sql("userinfo", engine, if_exists="replace", index=False)
        print("success")
    except:
        print("faild")


if __name__ == "__main__":
    gen_user_info_db()
