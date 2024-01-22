import json

from fastapi import FastAPI, HTTPException, Request
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_CONFIG = {
    "user": "root",
    "password": "yara",
    "host": "localhost",
    "port": 3308,
}

def get_db(company_name: str):
    try:
        print("companyyyyyyyyyyyy nameeee",company_name)
        # Connect to the database using MySQL Connector/Python
        connection = mysql.connector.connect(
            database=company_name,
            **DATABASE_CONFIG
        )
        return connection
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            raise HTTPException(status_code=404, detail="Company not found")
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        company_name = data.get('company_name')

        user_query = (
            f"SELECT * FROM users "
            f"WHERE username = '{username}' AND password = '{password}' "
            f"AND EXISTS (SELECT name FROM company WHERE name = '{company_name}')"
        )

        # Establish the database connection
        conn = get_db(company_name)

        cursor = conn.cursor()
        cursor.execute(user_query)
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        user = dict(zip(column_names, user))
        print("LOGGEEDDDDDDDDDD INNNNNNNNNNNNNNN USERRRRRRRRRRRRRRRRRRR")
        print("Received data:", username, password, company_name)
        print("Authentication successful:", username, company_name)
        return {"message": "Login successful", "user": user}
    except HTTPException as e:
        print("Validation error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.get("/users/{company_name}")
async def get_users(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        user_query = (
            f"SELECT * FROM users "
            f"WHERE EXISTS (SELECT name FROM company WHERE name = '{company_name}')"
        )

        cursor.execute(user_query)
        users = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        users_list = [dict(zip(column_names, user)) for user in users]

        # print("userssssssssssssssssssssssssssssss", users_list)

        return users_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass


@app.get("/getUserDetail/{company_name}/{username}")
async def get_user_detail(company_name: str, username: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        user_query = "SELECT * FROM users WHERE username=%s"
        cursor.execute(user_query, (username,))
        user = cursor.fetchone()

        print("userssssssssssssssssssssssssssssss", user)
        # Get column names from cursor.description

        # Convert the tuple to a dictionary
        user_dict = dict(zip(cursor.column_names, user))

        return user_dict
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass



@app.post("/users/{company_name}/{user_id}")
async def update_user(
        company_name: str,
        user_id: int,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Check if the user exists
        user_query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(user_query, (user_id,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get JSON data from request body
        data = await request.json()
        print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", data)

        # Convert username to uppercase if it exists in the data
        if 'username' in data:
            data['username'] = data['username'].upper()
            print("ana bl usernameeeeeeeeeeeeeeee", data['username'])

        # Construct the SQL update query
        update_query = f"UPDATE users SET {', '.join(f'{field} = %s' for field in data)} WHERE id = %s"
        update_values = list(data.values())
        print("updateddddddddddddddddddddddd valuessssssssssssssss", update_values)
        update_values.append(user_id)

        # Execute the update query
        cursor.execute(update_query, tuple(update_values))

        # Commit the changes to the database
        conn.commit()

        return {"message": "User details updated successfully", "user": user}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()


@app.get("/company/{company_name}")
async def get_company(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        user_query = (
            f"SELECT * FROM company "

        )

        cursor.execute(user_query)
        users = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        users_list = [dict(zip(column_names, user)) for user in users]

        print("userssssssssssssssssssssssssssssss", users_list)

        return users_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass


@app.post("/addusers/{company_name}/{user_name}")
async def add_user(
        company_name: str,
        user_name: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Check if the user exists
        user_query = f"SELECT * FROM users WHERE username = %s"

        cursor.execute(user_query, (user_name,))

        user = cursor.fetchone()
        # user_dict = dict(zip(cursor.column_names, user))
        # print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", user_dict)
        print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",user)
        if user is not None:
            return {"message": "User already exists"}

        # Convert username to uppercase
        user_name_uppercase = user_name.upper()

        # Get JSON data from request body
        data = await request.json()
        print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", data)

        # Perform the actual insert operation
        insert_query = f"INSERT INTO users(username, password, user_control, email, sales, sales_return, purshase, purshase_return, orders, trans, items, chart, statement) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (user_name_uppercase, '', '', '', '', '', '', '', '', '', '', '', ''))

        # Commit the changes to the database
        conn.commit()

        return {"message": "User added successfully", "user": user_name_uppercase}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.get("/categories/{company_name}")
async def get_categories(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        category_query = (
            f"SELECT * FROM groupitem WHERE GroupNo != 'MOD'"
        )

        cursor.execute(category_query)
        categories = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        categories_list = [dict(zip(column_names, category)) for category in categories]

        print("hol l categoriesssssss", categories_list)

        return categories_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.get("/allitems/{company_name}")
async def get_allitems(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        allitems_query = (
            "SELECT * FROM items "
            "WHERE GroupNo != 'MOD' AND Active = 'Y' "
        )

        cursor.execute(allitems_query)
        allitems = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        items_list = [dict(zip(column_names, allitem)) for allitem in allitems]

        print("hol alllllllllll itemsssss", items_list)

        return items_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass
@app.get("/categoriesitems/{company_name}/{category_id}")
async def get_itemsCategories(company_name: str, category_id: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        categoryitems_query = (
            "SELECT items.ItemNo, items.ItemName, items.Image, items.UPrice, items.Disc, items.Tax, items.KT1, items.KT2, items.KT3, items.KT4 "
            "FROM items "
            "INNER JOIN groupItem ON items.GroupNo = groupItem.GroupNo "
            "WHERE groupItem.GroupNo=%s And items.Active = 'Y'"
        )

        cursor.execute(categoryitems_query, (category_id,))
        categoriesitems = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        categories_list = [dict(zip(column_names, categoryitem)) for categoryitem in categoriesitems]

        print("hol l itemssssssssssssss in each categories", categories_list)

        return categories_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass


@app.post("/invoiceitem/{company_name}/{Branch}/{SAType}/{Date}/{DSValue}/{Srv}")
async def post_invoiceitem(company_name: str, Branch: str, SAType: str, Date: str, DSValue: float, Srv:float,request: Request):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Insert into invoices table
        cursor.execute("INSERT INTO invnum () VALUES ();")

        # Get the last inserted invoice code
        invoice_code = cursor.lastrowid
        parsed_date = datetime.strptime(Date, "%d-%m-%Y %H%M%S")

        data = await request.json()
        print("itemssssssssssssssss codeeeeeeeeeeeeee", data)

        overall_total = 0

        for item in data:
            # Fetch the Disc and Tax values from the items table
            # cursor.execute("SELECT Disc, Tax, GroupNo, KT1, KT2, KT3, KT4 FROM items WHERE ItemNo = %s;", (item["ItemNo"],))
            # result = cursor.fetchone()
            #
            # if result:
            #     disc, tax, GroupNo, KT1, KT2, KT3, KT4 = result
            # else:
            #     disc, tax = 0, 0
            # Calculate the total price for the current item
            total_price = item["UPrice"] * item["quantity"]

            # Add the total price to the overall total
            overall_total += total_price

            # Insert the item into the database with the calculated total price
            cursor.execute(
                "INSERT INTO inv (InvType, InvNo, ItemNo, Barcode, Branch, Qty, UPrice, Disc, Tax, GroupNo, KT1, KT2, KT3, KT4) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (
                    SAType, invoice_code, item["ItemNo"], "barc", Branch, item["quantity"], item["UPrice"],
                    item["Disc"], item["Tax"], item["GroupNo"], item["KT1"], item["KT2"], item["KT3"], item["KT4"]
                )
            )

            if "chosenModifiers" in item and item["chosenModifiers"]:
                for chosenModifier in item["chosenModifiers"]:
                    # Fetch the Disc, Tax, GroupNo, KT1, KT2, KT3, KT4 values from the items table
                    cursor.execute("SELECT Disc, Tax, GroupNo, KT1, KT2, KT3, KT4 FROM items WHERE ItemNo = %s;",
                                   (chosenModifier["ItemNo"],))
                    result = cursor.fetchone()

                    if result:
                        disc, tax, group_no, kt1, kt2, kt3, kt4 = result
                    else:
                        disc, tax, group_no, kt1, kt2, kt3, kt4 = 0, 0, "MOD", 0, 0, 0, 0

                    # Continue with your INSERT statement using the fetched values
                    cursor.execute(
                        "INSERT INTO inv (InvType, InvNo, ItemNo, Barcode, Branch, Qty, UPrice, Disc, Tax, GroupNo, KT1, KT2, KT3, KT4) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (
                            SAType, invoice_code, chosenModifier["ItemNo"], "barc", Branch, item["quantity"],
                            item["UPrice"], disc, tax, group_no, kt1, kt2, kt3, kt4
                        )
                    )

        cursor.execute(
            "UPDATE invnum SET Date = %s, AccountNo = %s, CardNo = %s, Branch = %s, Disc = %s, Srv = %s, InvType=%s WHERE InvNo = %s;",
            (
                parsed_date, "accno", "cardno", Branch, DSValue, Srv, SAType, invoice_code
            )
        )

        #cursor.execute("UPDATE invnum SET total = %s WHERE code = %s;", (overall_total, invoice_code))

        conn.commit()


        # Return the inserted data or any other relevant response
        return {"message": "Invoice items added successfully"}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.get("/getModifiers/{company_name}")
async def get_modifiers(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        modifieritems_query = (
            "SELECT ItemNo, ItemName, Image "
            "FROM items "
            "WHERE GroupNo=%s"
        )

        cursor.execute(modifieritems_query, ("MOD",))
        modifiersitems = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        modifiers_list = [dict(zip(column_names, modifyitem)) for modifyitem in modifiersitems]

        print("hol l itemssssssssssssss in each categories", modifiers_list)

        return modifiers_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.get("/allitemswithmod/{company_name}")
async def get_allitemswithmod(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        allitems_query = (
            "SELECT items.ItemNo, items.ItemName, items.Image, items.UPrice, items.Disc, items.Tax, items.KT1, items.KT2, items.KT3, items.KT4, items.Active, groupitem.GroupName, groupItem.GroupNo "
            "FROM items "
            "LEFT JOIN groupitem ON items.GroupNo = groupitem.GroupNo;"
        )

        cursor.execute(allitems_query)
        allitems = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        items_list = [dict(zip(column_names, allitem)) for allitem in allitems]

        # Handle the case where GroupNo is still ''
        for item in items_list:
            if item['GroupNo'] == '':
                item['GroupName'] = ' '  # or any default value you want

        print("hol alllllllllll itemsssss", items_list)

        return items_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        if conn:
            conn.close()


@app.get("/groupitems/{company_name}")
async def get_groupitems(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        allgroups_query = (
            "SELECT *  from groupitem "
        )

        cursor.execute(allgroups_query)
        allgroups = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        grps_list = [dict(zip(column_names, allgrp)) for allgrp in allgroups]

        print("hol alllllllllll itemsssss", grps_list)

        return grps_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.post("/updateItems/{company_name}/{item_id}")
async def update_item(
        company_name: str,
        item_id: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Check if the user exists
        user_query = "SELECT * FROM items WHERE ItemNo = %s"
        cursor.execute(user_query, (item_id,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get JSON data from request body
        data = await request.json()
        print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", data)

        # Construct the SQL update query
        update_query = (
            "UPDATE items SET ItemNo = %s, GroupNo = %s, ItemName = %s, "
            "Image = %s, UPrice = %s, Disc = %s, Tax = %s, KT1 = %s, KT2 = %s, KT3 = %s, KT4 = %s, Active = %s "
            "WHERE ItemNo = %s"
        )
        update_values = [
            data["ItemNo"],
            data["GroupNo"],
            data["ItemName"],
            data["Image"],
            data["UPrice"],
            data["Disc"],
            data["Tax"],
            data["KT1"],
            data["KT2"],
            data["KT3"],
            data["KT4"],
            data["Active"],
            item_id
        ]
        print("updateddddddddddddddddddddddd valuessssssssssssssss", update_values)

        # Execute the update query
        cursor.execute(update_query, tuple(update_values))

        # Commit the changes to the database
        conn.commit()

        return {"message": "User details updated successfully", "user": user}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.post("/additems/{company_name}/{item_no}")
async def add_user(
        company_name: str,
        item_no: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Check if the user exists
        addItem_query = f"SELECT * FROM items WHERE ItemNo = %s"

        cursor.execute(addItem_query, (item_no,))

        existItem = cursor.fetchone()
        # user_dict = dict(zip(cursor.column_names, user))
        # print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", user_dict)
        print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",existItem)
        if existItem is not None:
            return {"message": "Item already exists"}

        # Get JSON data from request body
        data = await request.json()
        print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", data)

        # Perform the actual insert operation
        insert_query = f"INSERT INTO items(ItemNo, GroupNo, ItemName, Image, UPrice, Disc, Tax, KT1, KT2, KT3, KT4, Active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (item_no, '', '', '', 0.0, 0.0, 0.0, '', '', '', '', 'N'))

        # Commit the changes to the database
        conn.commit()

        return {"message": "User added successfully", "item": item_no}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.get("/getItemDetail/{company_name}/{item_no}")
async def get_item_detail(company_name: str, item_no: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        additem_query = (
            "SELECT items.ItemNo, items.ItemName, items.Image, items.UPrice, items.Disc, items.Tax, items.KT1, items.KT2, items.KT3, items.KT4, items.Active, groupitem.GroupName, groupitem.GroupNo "
            "FROM items "
            "LEFT JOIN groupitem ON items.GroupNo = groupitem.GroupNo "
            "WHERE items.ItemNo = %s;"
        )
        cursor.execute(additem_query, (item_no,))
        additem = cursor.fetchone()

        print("Add itemsss", additem)
        # Get column names from cursor.description

        # Convert the tuple to a dictionary
        getadditem_dict = dict(zip(cursor.column_names, additem))

        return getadditem_dict
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        if conn:
            conn.close()