import cups

try:
    conn = cups.Connection()
    printers = conn.getPrinters()
    default_printer = conn.getDefault()

    print("Printers:", printers)
    print("Default printer:", default_printer)
except Exception as e:
    print("Error connecting to CUPS:", e)