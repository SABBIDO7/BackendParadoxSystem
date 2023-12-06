from fastapi.middleware.cors import CORSMiddleware
import hashlib
from sqlalchemy import create_engine,func,text
from sqlalchemy.orm import sessionmaker
import models
from fastapi import FastAPI, HTTPException,status,Request
from sqlalchemy.ext.declarative import declarative_base


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/AddCompany/",status_code=status.HTTP_201_CREATED)
async def add_company(request:Request):
    try:
        data = await request.json()

        engine=create_engine(f'mysql+pymysql://root:root@localhost:3307')
        SessionLocal= sessionmaker(autocommit=False, autoflush= False, bind=engine)
        Base = declarative_base()


        db = SessionLocal()

        query = text(f"SELECT SCHEMA_NAME FROM      INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{data.CompanyName}'")
        result = db.execute(query).fetchone()

        if result:
            # Database with the same name already exists
            raise HTTPException(status_code=400, detail="Database with this name already exists")

        # Create a new database and insert the company information
        create_db_query = text(f"CREATE DATABASE {data.CompanyName}")
        db.execute(create_db_query)
        if db:
                    engine2=create_engine(f'mysql+pymysql://root:root@localhost:3307/{data.CompanyName}')
        SessionLocal2= sessionmaker(autocommit=False, autoflush= False, bind=engine2)

        # Create tables in the new database
        Base.metadata.create_all(bind=engine2)
        db2 = SessionLocal2()
        post_companyDetails = models.CompanyManagementP(name=data.CompanyName,tel=data.tel,currency=data.currency)
        db2.add(post_companyDetails)
        db2.commit()
        if db2:
            
            create_dept=models.DepartmentsP(name=data.departmentName,description=data.departmentDescription)
            db2.add(create_dept)
            db2.commit()
            post_user=models.UsersP(name=data.username,usercode=data.usercode,department_id=create_dept.id)

            db2.add(post_user)
            db2.commit()

            return {"status": True, "message": "Company added successfully"}
    except Exception as e:
        return {"status": False, "error": str(e)}
    finally:
        db.close()





@app.post("/Checkuser/",status_code=status.HTTP_201_CREATED)
async def authenticate_user(username, password,CompanyName):
    try:
        engine=create_engine(f'mysql+pymysql://root:root@localhost:3307/{CompanyName}')
        SessionLocal= sessionmaker(autocommit=False, autoflush= False, bind=engine)

        db = SessionLocal()
    
        user = db.query(models.Users).filter(models.Users.username == username).first()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        print(hashed_password)
        print(user.username)
        print(user.password)
        # Check if the user exists and the provide
        # d password matches the stored hashed password
        if user and user.password==hashed_password:
            return {"status":True}  # Authentication successful
        else:
            return {"status":False}  # Authentication failed
    except Exception as e:
        # Handle the error when the database doesn't exist
        return {"status": False, "error": "Database does not exist or connection failed"}
    finally:
        db.close()