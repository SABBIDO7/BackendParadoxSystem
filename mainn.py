#
# from fastapi import FastAPI, HTTPException, Request, Depends
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session
# from models import Users, Company
# import models
# from sqlalchemy.exc import OperationalError
# from fastapi.middleware.cors import CORSMiddleware
# from models import Base
# from fastapi import HTTPException
# from sqlalchemy import text
# import mysql.connector
#
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# DATABASE_URL_TEMPLATE = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database_name}"
# DATABASE_URL_TEMPLATE2 = "mysql+mysqlconnector://root:yara@localhost:3308/abc"
# engine = create_engine(DATABASE_URL_TEMPLATE2)
# Base.metadata.create_all(bind=engine)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# def get_db(company_name: str):
#     database_url = DATABASE_URL_TEMPLATE.format(
#         user="root",
#         password="yara",
#         host="localhost",
#         port="3308",
#         database_name=company_name,
#     )
#     engine = create_engine(database_url)
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     db = SessionLocal()
#     try:
#         return db
#     except OperationalError as e:
#         if "Unknown database" in str(e):
#             raise HTTPException(status_code=404, detail="Company not found")
#         else:
#             raise
#     finally:
#         db.close()
#
# def authenticate_user(db: Session, username: str, password: str, company_name: str):
#     try:
#         valid_company = db.query(Company).filter(Company.name == company_name).first()
#         if not valid_company:
#             raise HTTPException(status_code=401, detail="Invalid company name")
#
#         user = db.query(Users).filter(Users.username == username, Users.password == password).first()
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid credentials")
#
#         return user
#     except HTTPException as e:
#         raise e
#     except OperationalError:
#         raise HTTPException(status_code=404, detail="Company not found")
#     finally:
#         db.close()
#
# @app.post("/login")
# async def login(request: Request):
#     try:
#         data = await request.json()
#         username = data.get('username')
#         password = data.get('password')
#         company_name = data.get('company_name')
#
#         db = get_db(company_name)
#         print("Received data:", username, password, company_name)
#         user = authenticate_user(db=db, username=username, password=password, company_name=company_name)
#         print("Authentication successful:", username, company_name)
#         return {"message": "Login successful", "user": user}
#     except HTTPException as e:
#         print("Validation error details:", e.detail)
#         raise e
#
#
# @app.get("/users/{company_name}")
# async def get_users(
#     company_name: str,
#     db: Session = Depends(get_db)
# ):
#     try:
#         valid_company = db.query(Company).filter(Company.name == company_name).first()
#         if not valid_company:
#             raise HTTPException(status_code=404, detail="Company not found")
#
#         # Query the Users table to get all users for the specified company
#         users = db.query(Users).all()
#
#         return users
#     except HTTPException as e:
#         print("Error details:", e.detail)
#         raise e
#     finally:
#         # Close the database session manually
#         db.close()
#
#
#
# @app.post("/users/{company_name}/{user_id}")
# async def update_user(
#     company_name: str,
#     user_id: int,
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Check if the user exists in the given company
#         user = db.execute(text(f"SELECT * FROM users WHERE id = {user_id}")).fetchone()
#         print("mn baad l userrrrrrrrrrrrrrrrrrrrrrrrr",user)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#
#         # Get JSON data from request body
#         data = await request.json()
#         print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data)
#
#         # Define a list to store the update clauses
#         update_clauses = []
#
#         # Check if each field exists in the Users model and add to update clauses
#         for field, value in data.items():
#             if field in ["username", "password", "user_control", "email", "sales", "sales_return", "purshase", "purshase_return", "order", "trans", "items", "chart", "statement"]:
#                 update_clauses.append(f"{field} = '{value}'")
#
#         # Check if any valid fields were provided
#         if not update_clauses:
#             raise HTTPException(status_code=422, detail="No valid fields provided for update")
#
#         # Construct the SQL update query
#         update_query = text(f"UPDATE users SET {', '.join(update_clauses)} WHERE id = {user_id}")
#
#         # Execute the update query
#         db.execute(update_query)
#
#         # Commit the changes to the database
#         db.commit()
#
#         return {"message": "User details updated successfully", "user": user}
#     except HTTPException as e:
#         print("Error details:", e.detail)
#         raise e
#     finally:
#         # Close the database session manually
#         db.close()

