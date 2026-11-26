from database import supabase               # importing runs database.py (loads env, builds client)

def main() -> None:                         # `-> None` = returns nothing
    try:                                    # network calls can fail, so wrap them
        response = (
            supabase.table("items")         # pick the table (like FROM items)
            .select("*")                    # SELECT *
            .execute()                      # sends the HTTP request; nothing runs before this
        )
        print("Connected. Rows:", response.data)  # .data = list of dicts, one per row
    except Exception as exc:                # broad catch is OK in a test script only
        print("Connection FAILED:", exc)

if __name__ == "__main__":                  # run main() only when executed directly
    main()
