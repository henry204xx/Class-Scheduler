def hari_string_to_number(hari_str):
    """
    Konversi nama hari ke angka.
    
    Args:
        hari_str (str): Nama hari ("Senin", "Selasa", "Rabu", "Kamis", "Jumat")
    
    Returns:
        int: Angka hari (1-5), atau 0 jika tidak valid
    """
    hari_map = {
        "Senin": 1,
        "Selasa": 2,
        "Rabu": 3,
        "Kamis": 4,
        "Jumat": 5
    }
    return hari_map.get(hari_str, 0)