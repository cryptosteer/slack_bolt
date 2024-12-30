import psycopg2
import pprint


pretty_printer = pprint.PrettyPrinter(width=60, depth=3, sort_dicts=True)


def debug(data, message=None):
    if message:
        print(f"\n### {message} ###")
    print(f"Data type: {type(data)}")
    if isinstance(data, dict):
        pretty_printer.pprint(data)
    elif hasattr(data, "__dict__"):
        print("Attributes:")
        pretty_printer.pprint(vars(data))
        print("\nMethods:")
        methods = [
            method
            for method in dir(data)
            if callable(getattr(data, method)) and not method.startswith("__")
        ]
        pretty_printer.pprint(methods)
    else:
        print("Unsupported data type: Raw printing")
        print(data)


def get_sql_client():
    return psycopg2.connect(
        host="209.126.85.73",
        port="5432",
        user="postgres",
        password="3o6dA$Bc9YLRr&",
        dbname="rocketeer",
        sslmode="disable",
    )


def sql_query(query: str):
    try:
        conn = get_sql_client()
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = [dict(zip(columns, row)) for row in rows]
        return result
    finally:
        conn.close()


def sql_statement(statement: str):
    conn = get_sql_client()
    cur = conn.cursor()
    try:
        cur.execute(statement)
        conn.commit()
        result = {
            "success": True,
            "message": "SQL statement executed successfully",
            "rows_affected": cur.rowcount,
        }
    except Exception as e:
        conn.rollback()
        result = {
            "success": False,
            "message": f"Error executing SQL statement: {str(e)}",
            "rows_affected": 0,
        }
    finally:
        cur.close()
        conn.close()
    return result
