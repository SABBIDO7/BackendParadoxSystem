import json
import tempfile
import time
from itertools import groupby

from fastapi import FastAPI, HTTPException, Request
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import subprocess
import win32print

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
    "password": "Hkms0ft",
    "host": "80.81.158.76",
    "port": 9988,
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci"
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
        error_message = None
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            error_message = "Invalid credentials"
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            error_message = "Company not found"
        else:
            error_message = "Internal Server Error"
        return error_message

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
        )

        # Establish the database connection
        conn = get_db(company_name)
        if isinstance(conn, str):  # Check if conn is an error message
            print("hhhhhhhhhhhhonnnnnnnnnnnnnn", conn)
            print(conn)
            return {"message": "Invalid Credentials"}  # Return the error message directly

        cursor = conn.cursor()
        cursor.execute(user_query)
        user = cursor.fetchone()

        if not user:
            return {"message": "Invalid Credentials"}

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
        data = await request.json()
        if 'username' in data:
            data['username'] = data['username'].upper()
        # Construct the SQL update query
        update_query = f"UPDATE users SET {', '.join(f'{field} = %s' for field in data)} WHERE id = %s"
        update_values = list(data.values())
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


import json

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
        comp = cursor.fetchone()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        compOb = dict(zip(column_names, comp))
        print("companyssssssssssssssss", compOb)

        return compOb
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass



from fastapi import HTTPException, Request


@app.post("/updateCompany/{company_name}")
async def updateCompany(company_name: str, request: Request):
    try:
        conn = get_db(company_name)
        cursor = conn.cursor()
        data = await request.json()
        print(data)
        sql_query = (
            f"UPDATE company SET Name = '{data['Name']}', "
            f"Phone = '{data['Phone']}', "
            f"Street = '{data['Street']}', "
            f"Branch = '{data['Branch']}', "
            f"City = '{data['City']}', "
            f"Currency = '{data['Currency']}', "
            f"Name2 = '{data['Name2']}', "
            f"`EndTime` = '{data['EndTime']}' "
        )
        cursor.execute(sql_query)
        conn.commit()
        print("endddddddddddddddddd",data["EndTime"])
        return {"message": "Company info successfully updated"}
    except Exception as e:
        print("Error details:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


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
        if user is not None:
            return {"message": "User already exists"}
        user_name_uppercase = user_name.upper()

        # Get JSON data from request body
        data = await request.json()
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
            "SELECT items.ItemNo, items.GroupNo, items.ItemName, items.Image, items.UPrice, items.Disc, items.Tax, items.KT1, items.KT2, items.KT3, items.KT4, items.Active "
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
        return categories_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass


from collections import defaultdict

@app.post("/invoiceitem/{company_name}")
async def post_invoiceitem(company_name: str, request: Request):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        conn2 = get_db(company_name)
        cursor2 = conn2.cursor()
        data = await request.json()
        items_by_kitchen = defaultdict(list)
        print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkk",data["unsentMeals"])
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", data)

        if data["meals"] == []:
            return {"message": "Invoice is empty"}
        # Create a dictionary to store items grouped by kitchen code
        # items_by_kitchen = defaultdict(list)
        # Specify keys for grouping
        print("mmmmmmmmmmmmmmmmmmmmmm",data["closeTClicked"])
        if data["closeTClicked"]:
            cursor2.execute(f"Select TableNo from inv Where InvNo = '{data['message']}' ")
            tableno = cursor2.fetchone()  # Assuming you want to fetch one row
            tableno = tableno[0]
            print("tttttttttttttttttt", tableno)
            cursor.execute(f"Update tablesettings set UsedBy='' Where TableNo= '{tableno}'")
            cursor.execute(f"Update inv set TableNo='', UsedBy='' Where InvNo='{data['message']}'")
            # Update the invnum table
            cursor.execute(
                "UPDATE invnum SET Date = %s, Time= %s, AccountNo = %s, CardNo = %s, Branch = %s, Disc = %s, Srv = %s, InvType=%s, RealDate=%s, RealTime=%s WHERE InvNo = %s;",
                (
                    data["date"], data["time"], data["accno"], "cardno", data["branch"], data["discValue"], data["srv"],
                    data["invType"], data["realDate"], data["time"], data['message']
                )
            )

            # Fetch invnum data
            cursor.execute(
                "SELECT InvType, InvNo, Date, Time, AccountNo, CardNo, Branch, Disc, Srv, RealDate, RealTime FROM invnum WHERE InvNo = %s;",
                (data['message'],))
            invnum_data = cursor.fetchone()
            conn.commit()
            invnum_keys = ["InvType", "InvNo", "Date", "Time", "AccountNo", "CardNo", "Branch", "Disc", "Srv", "RealDate", "RealTime"]
            invnum_dicts = dict(zip(invnum_keys, invnum_data))
            return {"invoiceDetails": invnum_dicts}

        else:
            cursor.execute(f"Select KT, PrinterName from printers")
            printer_data = cursor.fetchall()
            printer_dic = {key: name for key, name in printer_data}
            # Specify keys for grouping
            keys_to_group_by = ['KT1', 'KT2', 'KT3', 'KT4']
            print("dmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm", data["tableNo"])
            inv_num = ''
            invoice_code = 1
            if data["tableNo"]:
                cursor.execute(f" Select InvNo from inv where tableNo = '{data["tableNo"]}'  LIMIT 1")
                inv_row = cursor.fetchone()
                inv_num = inv_row[0]
                cursor.execute(f"DELETE FROM inv WHERE InvNo = '{inv_num}'")
            else:
                # Insert into invoices table
                cursor.execute("INSERT INTO invnum () VALUES ();")
                # Get the last inserted invoice code
                invoice_code = cursor.lastrowid
            if len(data["unsentMeals"]) == 0:
                return {"message": "The meals already sent to kitchen"}
            # Group meals by printer names
            for meal in data["unsentMeals"]:
                printer_names = [printer_dic.get(meal[kt_key], "") for kt_key in keys_to_group_by]
                print("printer-names")
                # Remove dashes from printer names
                printer_names = [name.replace('-', '') for name in printer_names]
                non_empty_printer_names = [name for name in printer_names if name]  # Filter out empty strings
                if non_empty_printer_names:  # Check if there are non-empty printer names
                    for kitchen in non_empty_printer_names:
                        items_by_kitchen[kitchen].append(meal)

            for item in data["meals"]:
                cursor.execute(
                    "INSERT INTO inv (InvType, InvNo, ItemNo, Barcode, Branch, Qty, UPrice, Disc, Tax, GroupNo, KT1, KT2, KT3, KT4, TableNo, UsedBy, Printed, `Index`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (
                        data["invType"], inv_num if data["tableNo"] else invoice_code, item["ItemNo"], "barc", data["branch"],
                        item["quantity"], item["UPrice"],
                        item["Disc"], item["Tax"], item["GroupNo"], item["KT1"], item["KT2"], item["KT3"], item["KT4"], data["tableNo"] if data["tableNo"] else '', '', 'p' if data["tableNo"] else '', item["index"],
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

                            # Continue with your INSERT statement using the fetched values
                            cursor.execute(
                                "INSERT INTO inv (InvType, InvNo, ItemNo, Barcode, Branch, Qty, UPrice, Disc, Tax, GroupNo, KT1, KT2, KT3, KT4, TableNo, UsedBy, Printed, `Index`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                                (
                                    data["invType"], inv_num if data["tableNo"] else invoice_code, chosenModifier["ItemNo"], "barc",
                                    data["branch"], item["quantity"],
                                    item["UPrice"], disc, tax, group_no, kt1, kt2, kt3, kt4, data["tableNo"] if data["tableNo"] else '', '', 'p' if data["tableNo"] else '', item["index"],
                                )
                            )
            # Update the invnum table
            cursor.execute(
                "UPDATE invnum SET Date = %s, Time= %s, AccountNo = %s, CardNo = %s, Branch = %s, Disc = %s, Srv = %s, RealDate=%s, RealTime=%s, InvType=%s WHERE InvNo = %s;",
                (
                    data["date"], data["time"], data["accno"], "cardno", data["branch"], data["discValue"], data["srv"], data["realDate"], data["time"], data["invType"], inv_num if data["tableNo"] else invoice_code,
                )
            )

            # Fetch invnum data
            cursor.execute(
                "SELECT InvType, InvNo, Date, Time, AccountNo, CardNo, Branch, Disc, Srv, RealDate, RealTime FROM invnum WHERE InvNo = %s;",
                (inv_num if data["tableNo"] else invoice_code,))
            invnum_data = cursor.fetchone()
            conn.commit()
            print("hhhhhhhhhhhhhhhhhhhhhhhhh", invnum_data)
            invnum_keys = ["InvType", "InvNo", "Date", "Time", "AccountNo", "CardNo", "Branch", "Disc", "Srv", "RealDate", "RealTime"]
            invnum_dicts = dict(zip(invnum_keys, invnum_data))
            if data["tableNo"]:
                cursor.execute(f"Update tablesettings set UsedBy = '' Where TableNo = '{data["tableNo"]}'")
                conn.commit()
            print("rrrrrrrrrrrrrrrrrrrrrrrrrrrr", items_by_kitchen)
            return {"message": "Invoice items added successfully", "selectedData": items_by_kitchen, "invoiceDetails": invnum_dicts}

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
        print("ddddddddddddddd", modifiersitems)
        column_names = [desc[0] for desc in cursor.description]
        modifiers_list = [dict(zip(column_names, modifyitem)) for modifyitem in modifiersitems]
        print("modifiers_list", modifiers_list)
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
            "SELECT items.ItemNo, items.ItemName, items.Image, items.UPrice, items.Disc, items.Tax, items.KT1, items.KT2, items.KT3, items.KT4, items.Active, items.Ingredients, groupitem.GroupName, groupItem.GroupNo "
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
        column_names = [desc[0] for desc in cursor.description]
        grps_list = [dict(zip(column_names, allgrp)) for allgrp in allgroups]
        return grps_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

from fastapi import HTTPException

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

        # Get JSON data from request body
        data = await request.json()
        print("Received data:", data)

        # Check if the updated ItemNo already exists and is not the same as the original one
        existing_item_query = "SELECT ItemNo FROM items WHERE ItemNo = %s"
        cursor.execute(existing_item_query, (data["ItemNo"],))
        existing_item = cursor.fetchone()
        if existing_item is not None and item_id != data["ItemNo"]:
            return {"message":"ItemNo already exists. Please choose another ItemNo."}

        # Construct the SQL update query dynamically based on the fields provided in the request
        update_query = (
            "UPDATE items SET "
            "ItemNo = %s, GroupNo = %s, ItemName = %s, "
            "Image = %s, UPrice = %s, Disc = %s, Tax = %s, KT1 = %s, KT2 = %s, KT3 = %s, KT4 = %s, Active = %s, Ingredients = %s "
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
            data["Ingredients"],
            item_id
        ]
        update_inv_query = "UPDATE inv SET ItemNo = %s WHERE ItemNo = %s"
        cursor.execute(update_inv_query, (data["ItemNo"], item_id))

        # Commit the changes to the database
        conn.commit()

        # Execute the update query for items table
        cursor.execute(update_query, tuple(update_values))
        conn.commit()
        return {"message": "Item details updated successfully", "oldItemNo": item_id, "newItemNo": data["ItemNo"]}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()


@app.post("/additems/{company_name}/{item_no}")
async def add_item(
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
        if existItem is not None:
            return {"message": "Item already exists"}
        data = await request.json()
        insert_query = f"INSERT INTO items(ItemNo, GroupNo, ItemName, Image, UPrice, Disc, Tax, KT1, KT2, KT3, KT4, Active, Ingredients) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (item_no, '', '', '', 0.0, 0.0, 0.0, '', '', '', '', 'N', ''))
        conn.commit()
        return {"message": "Item added successfully", "item": item_no}
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
            "SELECT items.ItemNo, items.ItemName, items.Image, items.UPrice, items.Disc, items.Tax, items.KT1, items.KT2, items.KT3, items.KT4, items.Active, items.Ingredients, groupitem.GroupName, groupitem.GroupNo "
            "FROM items "
            "LEFT JOIN groupitem ON items.GroupNo = groupitem.GroupNo "
            "WHERE items.ItemNo = %s;"
        )
        cursor.execute(additem_query, (item_no,))
        additem = cursor.fetchone()
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

@app.post("/updateGroups/{company_name}/{group_id}")
async def updateGroups(
        company_name: str,
        group_id: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Get JSON data from request body
        data = await request.json()
        print("Received data:", data)

        # Check if the updated ItemNo already exists and is not the same as the original one
        existing_group_query = "SELECT GroupNo FROM groupitem WHERE GroupNo = %s"
        cursor.execute(existing_group_query, (data["GroupNo"],))
        existing_item = cursor.fetchone()
        if existing_item is not None and group_id != data["GroupNo"]:
            return {"message":"GroupNo already exists. Please choose another GroupNo."}

        # Construct the SQL update query dynamically based on the fields provided in the request
        update_query = (
            "UPDATE groupitem SET "
            "GroupNo = %s, GroupName = %s, Image = %s "
            "WHERE GroupNo = %s"
        )
        update_values = [
            data["GroupNo"],
            data["GroupName"],
            data["Image"],
            group_id
        ]
        update_inv_query = "UPDATE inv SET GroupNo = %s WHERE GroupNo = %s"
        cursor.execute(update_inv_query, (data["GroupNo"], group_id))

        # Commit the changes to the database
        conn.commit()

        # Execute the update query for items table
        cursor.execute(update_query, tuple(update_values))
        conn.commit()
        return {"message": "Group details updated successfully", "oldItemNo": group_id, "newItemNo": data["GroupNo"]}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()


@app.post("/addgroup/{company_name}/{group_no}")
async def addgroup(
        company_name: str,
        group_no: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Check if the user exists
        addGroup_query = f"SELECT * FROM groupitem WHERE GroupNo = %s"

        cursor.execute(addGroup_query, (group_no,))

        existGroup = cursor.fetchone()
        if existGroup is not None:
            return {"message": "Group already exists"}
        data = await request.json()
        insert_query = f"INSERT INTO groupitem(GroupNo, GroupName, Image) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (group_no, '', ''))
        conn.commit()
        return {"message": "Group added successfully", "group": group_no}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.get("/getGroupDetail/{company_name}/{group_no}")
async def get_item_detail(company_name: str, group_no: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        addgroup_query = (
            "SELECT GroupNo, GroupName, Image "
            "FROM groupitem "
            "WHERE GroupNo = %s;"
        )
        cursor.execute(addgroup_query, (group_no,))
        addgroup = cursor.fetchone()
        # Convert the tuple to a dictionary
        getaddgroup_dict = dict(zip(cursor.column_names, addgroup))
        print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", getaddgroup_dict)

        return getaddgroup_dict
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        if conn:
            conn.close()

@app.get("/clients/{company_name}")
async def get_clients(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        allclients_query = (
            "SELECT * FROM clients "
        )

        cursor.execute(allclients_query)
        allclients = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]

        # Convert the list of tuples to a list of dictionaries
        clients_list = [dict(zip(column_names, client)) for client in allclients]
        return clients_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.post("/addclients/{company_name}/{user_name}")
async def add_client(
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
        client_query = f"SELECT * FROM clients WHERE AccName = %s"

        cursor.execute(client_query, (user_name,))

        client = cursor.fetchone()
        if client is not None:
            return {"message": "Client already exists"}
        client_name_uppercase = user_name.upper()
        initial_insert_query = "INSERT INTO clients(AccName, Address, Address2, Tel, Building, Street, Floor, Active, GAddress, Email, VAT, Region, AccPrice, AccGroup, AccDisc, AccRemark) VALUES (%s, %s, %s, %s, %s, %s, %s, %s , %s, %s, %s, %s , %s, %s, %s, %s)"
        cursor.execute(initial_insert_query, (client_name_uppercase, '', '', '', '', '', '', 'Y', '', '', '', '', '', '', 0.0, ''))

        # Commit the changes to the database
        conn.commit()

        return {"message": "User added successfully", "user": client_name_uppercase}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.post("/updateClients/{company_name}/{client_id}")
async def update_client(
        company_name: str,
        client_id: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Check if the user exists
        user_query = "SELECT * FROM clients WHERE AccNo = %s"
        cursor.execute(user_query, (client_id,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        data = await request.json()
        update_query = (
            "UPDATE clients SET AccNo = %s, AccName = %s, Address = %s, "
            "Address2 = %s, Tel = %s, Building = %s, Street = %s, Floor = %s, Active = %s, GAddress = %s, Email = %s, VAT = %s, Region = %s, "
            "AccPrice = %s, AccGroup = %s, AccDisc = %s, AccRemark = %s   "
            "WHERE AccNo = %s"
        )
        update_values = [
            data["AccNo"],
            data["AccName"],
            data["Address"],
            data["Address2"],
            data["Tel"],
            data["Building"],
            data["Street"],
            data["Floor"],
            data["Active"],
            data["GAddress"],
            data["Email"],
            data["VAT"],
            data["Region"],
            data["AccPrice"],
            data["AccGroup"],
            data["AccDisc"],
            data["AccRemark"],
            client_id
        ]
        # Execute the update query
        cursor.execute(update_query, tuple(update_values))

        # Commit the changes to the database
        conn.commit()

        return {"message": "Client details updated successfully", "user": user}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.get("/getClientDetail/{company_name}/{client_id}")
async def get_client_detail(company_name: str, client_id: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        user_query = "SELECT * FROM clients WHERE AccName=%s"
        cursor.execute(user_query, (client_id,))
        client = cursor.fetchone()
        user_dict = dict(zip(cursor.column_names, client))

        return user_dict
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.get("/allsections/{company_name}")
async def get_allsections(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        allitems_query = (
            "SELECT * FROM section "
        )

        cursor.execute(allitems_query)
        allsections = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        section_list = [dict(zip(column_names, section)) for section in allsections]
        print("lennnnnnnnnnn",len(section_list))
        return {"section_list": section_list}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.post("/addsections/{company_name}")
async def add_section(
        company_name: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()
        data = await request.json()

        # Check if the user exists
        check_section = f"SELECT * FROM section WHERE SectionNo = %s"
        cursor.execute(check_section, (data["SectionNo"],))
        section = cursor.fetchone()
        if section is not None:
            return {"message": "Section already exists"}
        section_uppercase = data["Name"].upper()
        # Perform the actual insert operation
        insert_query = f"INSERT INTO section(SectionNo, Name) VALUES (%s, %s)"
        cursor.execute(insert_query, (data["SectionNo"],section_uppercase, ))
        conn.commit()

        return {"message": "Section added successfully", }
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.post("/updateSections/{company_name}/{section_id}")
async def update_section(
        company_name: str,
        section_id: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()

        # Get JSON data from request body
        data = await request.json()
        # Check if the updated ItemNo already exists and is not the same as the original one
        existing_item_query = "SELECT SectionNo FROM section WHERE SectionNo = %s"
        cursor.execute(existing_item_query, (data["SectionNo"],))
        existing_section = cursor.fetchone()
        if existing_section is not None and section_id != data["SectionNo"]:
            return {"message":"SectionNo already exists. Please choose another SectionNo."}

        # Construct the SQL update query dynamically based on the fields provided in the request
        update_query = (
            "UPDATE section SET "
            "SectionNo = %s, Name = %s "
            "WHERE SectionNo = %s"
        )
        update_values = [
            data["SectionNo"],
            data["Name"],
            section_id
        ]
        # Update the InvNo in the inv table after committing changes to items table
        update_table_query = "UPDATE tablesettings SET SectionNo = %s WHERE SectionNo = %s"
        cursor.execute(update_table_query, (data["SectionNo"], section_id))
        conn.commit()
        cursor.execute(update_query, tuple(update_values))
        conn.commit()
        return {"message": "Section updated successfully"}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.get("/alltables/{company_name}/{sectionNo}")
async def get_alltables(company_name: str, sectionNo: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        if sectionNo:
            cursor.execute(
                f"SELECT * FROM tablesettings Where SectionNo = '{sectionNo}'"
            )
        else:
            cursor.execute("Select * from tablesettings")
        alltables = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        table_list = [dict(zip(column_names, table)) for table in alltables]
        return table_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.post("/addtables/{company_name}/{sectionNo}")
async def add_table(
        company_name: str,
        sectionNo: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()
        data = await request.json()

        # Check if the user exists
        check_table = f"SELECT * FROM tablesettings WHERE TableNo = %s "

        cursor.execute(check_table, (data["TableNo"],))

        table = cursor.fetchone()
        if table is not None:
            return {"message": "Table already exists"}
        # Perform the actual insert operation
        insert_query = f"INSERT INTO tablesettings(TableNo, TableWaiter, SectionNo, Active, Description) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (data["TableNo"], data["TableWaiter"], sectionNo, data["Active"], data["Description"]))

        # Commit the changes to the database
        conn.commit()
        return {"message": "Table added successfully", }
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.post("/updateTables/{company_name}/{sectionNo}/{tableNo}")
async def update_table(
        company_name: str,
        sectionNo: str,
        tableNo: str,
        request: Request,
):
    conn = None
    try:
        # Check if the user exists in the given company
        conn = get_db(company_name)
        cursor = conn.cursor()
        data = await request.json()
        # Check if the updated ItemNo already exists and is not the same as the original one
        existing_table_query = "SELECT TableNo FROM tablesettings WHERE TableNo = %s "
        cursor.execute(existing_table_query, (data["TableNo"],))
        existing_table = cursor.fetchone()
        if existing_table is not None and tableNo != data["TableNo"]:
            return {"message":"Table No already exists. Please choose another Table No."}
        update_query = (
            "UPDATE tablesettings SET "
            "TableNo = %s, TableWaiter = %s, SectionNo = %s, Active = %s, Description = %s "
            "WHERE TableNo = %s AND SectionNo = %s "
        )
        update_values = [
            data["TableNo"],
            data["TableWaiter"],
            sectionNo,
            data["Active"],
            data["Description"],
            tableNo, sectionNo
        ]
        # Execute the update query for items table
        cursor.execute(update_query, tuple(update_values))
        conn.commit()
        return {"message": "Table updated successfully"}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

@app.get("/getInv/{company_name}/{tableNo}/{usedBy}")
async def getInv(company_name: str, tableNo: str, usedBy: str):
    conn = None
    try:
        conn = get_db(company_name)
        cursor = conn.cursor()
        # Check if the updated ItemNo already exists and is not the same as the original one
        existing_table_query = """
                    SELECT *
                    FROM inv
                    WHERE TableNo = %s LIMIT 1
                """
        cursor.execute(existing_table_query, (tableNo,))
        existing_table = cursor.fetchone()
        print("eeeeeeeeeeeeeeeeee")
        # Get column names from cursor.description if result set exists
        if existing_table:
            column_names = [desc[0] for desc in cursor.description]
            invNo = dict(zip(column_names, existing_table))
            inv_No = invNo["InvNo"]
            print("eeeeeeeeeeeeeeeeee111111111111111111111111111", inv_No)

            update_usedBy = "Update inv set UsedBy = %s where TableNo = %s "
            update_values = [usedBy, tableNo]
            cursor.execute(update_usedBy, tuple(update_values))
            conn.commit()
            print("eeeeeeeeeeeeeeeeee22222222222222222222222222222222")

            cursor.execute(f"Select Disc, Srv from invnum where InvNo ='{inv_No}'")
            result = cursor.fetchone()
            disc, srv = result
            print("eeeeeeeeeeeeeeeeee33333333333333333333333333333333")

            cursor.execute(f"Update tablesettings set UsedBy = '{usedBy}' where TableNo = '{tableNo}'")
            conn.commit()
            cursor.execute(f" Select `Index` from inv where TableNo= '{tableNo}' Group By `Index` ")
            extract_indexes = cursor.fetchall()
            print("eeeeeeeeeeeeeeeeee555555555555555555555555555555", extract_indexes)

            inv_list = []
            if extract_indexes and extract_indexes[0][0] is not None:

                for e_index_row in extract_indexes:
                    e_index = e_index_row[0]
                    query = f" Select inv.*, items.ItemName from inv left join items on inv.ItemNo = items.ItemNo where inv.Index = {e_index} and inv.TableNo = '{tableNo}' and inv.GroupNo != 'MOD' "
                    cursor.execute(query)
                    princ_items = cursor.fetchone()
                    print("666666666666666666666666666666666666666666666", princ_items)

                    column_names = [desc[0] for desc in cursor.description]
                    princ_item = dict(zip(column_names, princ_items))
                    query2 = f" Select inv.*, items.ItemName from inv left join items on inv.ItemNo = items.ItemNo Where inv.TableNo = '{tableNo}' and inv.Index = {e_index} and inv.GroupNo = 'MOD' "
                    cursor.execute(query2)
                    item_mods = cursor.fetchall()
                    print("8888888888888888888888888888888888888888", item_mods)
                    column_names = [desc[0] for desc in cursor.description]
                    item_mod = [dict(zip(column_names, imod)) for imod in item_mods]
                    print("8888888888888888888888888888888888888888", item_mod)

                    item = {
                        "ItemNo": princ_item["ItemNo"],
                        "ItemName": princ_item["ItemName"],
                        "Printed": princ_item["Printed"],
                        "UPrice": princ_item["UPrice"],
                        "Disc": princ_item["Disc"],
                        "Tax": princ_item["Tax"],
                        "quantity": princ_item["Qty"],
                        "KT1": princ_item["KT1"],
                        "KT2": princ_item["KT2"],
                        "KT3": princ_item["KT3"],
                        "KT4": princ_item["KT4"],
                        "index": princ_item["Index"],
                        "GroupNo": princ_item["GroupNo"],
                        "chosenModifiers": [
                            {"ItemNo": itemod["ItemNo"], "ItemName": itemod["ItemName"]}
                            for itemod in item_mod
                        ]
                    }
                    inv_list.append(item)
                print("ffffffffffffffffffff", inv_list)
                return {"inv_list": inv_list, "invNo": inv_No, "disc": disc, "srv": srv }
        return {"message": "there are no items"}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        if conn:
            conn.close()

# @app.post("/insertInv/{company_name}/{tableNo}/{usedBy}")
# async def insertInv(company_name: str, tableNo: str, usedBy: str, request: Request):
#     conn = None
#     try:
#         conn = get_db(company_name)
#         cursor = conn.cursor()
#
#         cursor.execute(f" Select InvNo from inv where tableNo = '{tableNo}'  LIMIT 1")
#         inv_row = cursor.fetchone()
#         data = await request.json()
#         meals = data['meals']
#         if(inv_row):
#             inv_num = inv_row[0]
#             if (inv_num is not None):
#                 cursor.execute(f"DELETE FROM inv WHERE InvNo = '{inv_num}'")
#                 for item in meals:
#                     cursor.execute(
#                         "INSERT INTO inv (InvType, InvNo, ItemNo, Barcode, Branch, Qty, UPrice, Disc, Tax, GroupNo, KT1, KT2, KT3, KT4, TableNo, UsedBy, Printed, `Index`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
#                         (
#                             data["invType"], inv_num, item["ItemNo"], "barc", data["branch"],
#                             item["quantity"], item["UPrice"],
#                             item["Disc"], item["Tax"], item["GroupNo"], item["KT1"], item["KT2"], item["KT3"],
#                             item["KT4"],
#                             tableNo, "", "p", item["index"])
#                     )
#                     if "chosenModifiers" in item and item["chosenModifiers"]:
#                         for chosenModifier in item["chosenModifiers"]:
#                             # Fetch the Disc, Tax, GroupNo, KT1, KT2, KT3, KT4 values from the items table
#                             cursor.execute(
#                                 "SELECT Disc, Tax, GroupNo, KT1, KT2, KT3, KT4 FROM items WHERE ItemNo = %s;",
#                                 (chosenModifier["ItemNo"],))
#                             result = cursor.fetchone()
#
#                             if result:
#                                 disc, tax, group_no, kt1, kt2, kt3, kt4 = result
#                                 cursor.execute(
#                                     "INSERT INTO inv (InvType, InvNo, ItemNo, Barcode, Branch, Qty, UPrice, Disc, Tax, GroupNo, KT1, KT2, KT3, KT4, TableNo, UsedBy, Printed, `Index`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
#                                     (
#                                         data["invType"], inv_num, chosenModifier["ItemNo"], "barc",
#                                         data["branch"], item["quantity"],
#                                         item["UPrice"], disc, tax, group_no, kt1, kt2, kt3, kt4, tableNo, "", "p",
#                                         item["index"]
#                                     )
#                                 )
#                 # Commit the transaction
#                 cursor.execute(
#                     f"UPDATE invnum SET InvType = '{data['invType']}', Date = '{data["date"]}', Time='{data["time"]}', AccountNo = 'accno', CardNo = 'cardno', Branch = '{data['branch']}', Disc = '{data['discValue']}', Srv = '{data['srv']}' WHERE InvNo = '{inv_num}'"
#                 )
#                 cursor.execute(f"Update tablesettings set UsedBy = '' Where TableNo = '{tableNo}'")
#                 conn.commit()
#                 return {"invNo": inv_num}
#     except HTTPException as e:
#         print("Error details:", e.detail)
#         raise e
#     finally:
#         if conn:
#             conn.close()

@app.get("/chooseAccess/{company_name}/{tableNo}/{loggedUser}")
async def chooseAccess(company_name: str, tableNo: str, loggedUser: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        tableNo_query = (
            f"SELECT * FROM inv Where TableNo = '{tableNo}' Limit 1 "
        )

        cursor.execute(tableNo_query)
        tableNo_fetch = cursor.fetchone()
        if(tableNo_fetch):
            print("lllllllllllllllllllllllllll", tableNo_fetch[1])
            column_names = [desc[0] for desc in cursor.description]
            row_dict = dict(zip(column_names, tableNo_fetch))
            print("nameeeeeeeeeeeeeeeees", row_dict["UsedBy"])
            print("loggeeeeeeeeeeeee", loggedUser)
            if row_dict["UsedBy"] != "" and row_dict["UsedBy"] != loggedUser:
                return {"message": "you can't access this table right now", "usedBy": row_dict["UsedBy"]}
            elif row_dict["UsedBy"] != "" and row_dict["UsedBy"] == loggedUser:
                return {"message": "you can access this table", "usedBy": row_dict["UsedBy"], "invNo": tableNo_fetch[1]}
        return {"message": "you can access this table", "usedBy": ""}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.post("/openTable/{company_name}/{tableNo}/{loggedUser}")
async def openTable(company_name: str, tableNo: str, loggedUser: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM inv WHERE TableNo = '{tableNo}' LIMIT 1")
        existTable = cursor.fetchone()
        if(existTable is None):
            cursor.execute("Insert Into invnum () Values (); ")
            invoice_code = cursor.lastrowid
            cursor.execute(
                f"Insert into inv(InvNo, TableNo, UsedBy) values ('{invoice_code}', '{tableNo}', '{loggedUser}')")
            cursor.execute(
                f"UPDATE tablesettings SET UsedBy = '{loggedUser}' WHERE TableNo = '{tableNo}'"
            )
            conn.commit()
            return {"message": invoice_code}
        else:
            return {"message": existTable[1]}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.get("/resetUsedBy/{company_name}/{InvNo}")
async def resetUsedBy(company_name: str, InvNo: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        conn2 = get_db(company_name)
        cursor = conn.cursor()
        cursor2 = conn2.cursor()

        # Update inv table
        cursor.execute(f"UPDATE inv SET UsedBy = '' WHERE InvNo = '{InvNo}'")
        conn.commit()

        # Fetch TableNo from inv table
        cursor.execute(f"SELECT TableNo FROM inv WHERE InvNo = '{InvNo}'")
        tableNo_row = cursor.fetchone()

        if tableNo_row:  # Check if a row was fetched
            tableNo = tableNo_row[0]  # Access the TableNo value
            print("vbbbbbbbbbbbbbbbbbbbbbb", tableNo)
            cursor2.execute(f"UPDATE tablesettings SET UsedBy='' WHERE TableNo = '{tableNo}'")
            conn2.commit()

    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        pass


@app.get("/getOneSection/{company_name}")
async def getOneSection(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        cursor.execute("Select SectionNo from section")
        secNo = cursor.fetchone()
        conn.commit()
        if secNo:
            return {"sectionNo": secNo[0]}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        pass

# @app.post("/groupkitchen/{company_name}/{tableNo}/{loggedin}")
# async def groupkitchen(company_name: str, request: Request, tableNo: str, loggedin: str):
#     try:
#         # Establish the database connection
#         conn = get_db(company_name)
#         cursor = conn.cursor()
#         data = await request.json()
#         cursor.execute(f"Select KT, Name from printers")
#         printer_data = cursor.fetchall()
#         printer_dic = {key: name for key, name in printer_data}
#         # Specify keys for grouping
#         keys_to_group_by = ['KT1', 'KT2', 'KT3', 'KT4']
#
#         # Group meals by printer names
#         unprintedMeals = defaultdict(list)
#         for meal in data:
#             printer_names = [printer_dic.get(meal[kt_key], "") for kt_key in keys_to_group_by]
#             # Remove dashes from printer names
#             printer_names = [name.replace('-', '') for name in printer_names]
#             non_empty_printer_names = [name for name in printer_names if name]  # Filter out empty strings
#             if non_empty_printer_names:  # Check if there are non-empty printer names
#                 for kitchen in non_empty_printer_names:
#                     unprintedMeals[kitchen].append(meal)
#         return {"unprintedMeals": unprintedMeals}
#     except HTTPException as e:
#         print("Error details:", e.detail)
#         raise e
#     finally:
#         pass

@app.get("/getInvHistoryDetails/{company_name}/{invNo}")
async def getAllInv(company_name: str, invNo: str):
    try:
        conn = get_db(company_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT inv.*, items.ItemName, groupitem.GroupName, invnum.*
            FROM inv
            INNER JOIN groupitem ON inv.GroupNo = groupitem.GroupNo
            INNER JOIN items ON inv.ItemNo = items.ItemNo
            INNER JOIN invnum ON inv.InvNo = invnum.InvNo
            WHERE inv.InvNo = '{invNo}'
        """)

        all_inv = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        inv_list = [dict(zip(column_names, inv)) for inv in all_inv]
        return inv_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass

@app.get("/getCompTime/{company_name}")
async def getCompTime(company_name: str):
    try:
        # Establish the database connection
        conn = get_db(company_name)
        cursor = conn.cursor()
        cursor.execute("Select EndTime from company")
        compTime = cursor.fetchone()
        if compTime:
            conn.commit()
            return {"compTime": compTime[0]}
        else:
            return {"compTime": "3:00"}
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        pass

@app.get("/getInvHistory/{company_name}")
async def getInvHistory(company_name: str):
    try:
        conn = get_db(company_name)
        cursor = conn.cursor()
        cursor.execute(f"Select * FROM invnum")

        all_inv = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        inv_list = [dict(zip(column_names, inv)) for inv in all_inv]
        print("invvvvvvvvvvvvvvvvvvv", inv_list)
        return inv_list
    except HTTPException as e:
        print("Error details:", e.detail)
        raise e
    finally:
        # The connection will be automatically closed when it goes out of scope
        pass