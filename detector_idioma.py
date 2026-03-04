def detectar_idioma(texto):
    """
    Detector simple de idioma basado en palabras comunes.
    Retorna: 'es' (español) o 'en' (inglés)
    """
    texto = texto.lower()
    
    palabras_es = ['el', 'la', 'los', 'las', 'con', 'para', 'vino', 'tinto', 'blanco', 'maridaje']
    palabras_en = ['the', 'with', 'for', 'wine', 'red', 'white', 'pairing', 'recommend']
    
    count_es = sum(1 for palabra in palabras_es if palabra in texto)
    count_en = sum(1 for palabra in palabras_en if palabra in texto)
    
    # Si claramente inglés
    if count_en > count_es + 2:
        return 'en'
    # Por defecto español (nuestro caso principal)
    return 'es'

if __name__ == "__main__":
    # Pruebas
    tests = [
        "Malbec con carne",
        "Red wine with steak",
        "Vino blanco para pescado",
        "What wine for chicken?"
    ]
    
    for test in tests:
        print(f"'{test}' -> {detectar_idioma(test)}")
