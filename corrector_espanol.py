import re

class CorrectorEspanol:
    """Corrector ULTRA AGRESIVO para doble encoding"""
    
    @staticmethod
    def corregir_texto(texto):
        if not texto:
            return texto
        
        original = texto
        cambios = []
        
        # PRIMERO: Corregir DOBLE encoding (ÃÂ)
        # ÃÂ³ -> Ã³ -> ó
        texto = texto.replace('ÃÂ¡', 'á')
        texto = texto.replace('ÃÂ©', 'é')
        texto = texto.replace('ÃÂ', 'í')
        texto = texto.replace('ÃÂ³', 'ó')
        texto = texto.replace('ÃÂº', 'ú')
        texto = texto.replace('ÃÂ±', 'ñ')
        texto = texto.replace('ÃÂ¼', 'ü')
        texto = texto.replace('ÃÂ¿', '¿')
        texto = texto.replace('ÃÂ¡', '¡')
        
        # SEGUNDO: Corregir encoding simple (Ã)
        texto = texto.replace('Ã¡', 'á')
        texto = texto.replace('Ã©', 'é')
        texto = texto.replace('Ã', 'í')
        texto = texto.replace('Ã³', 'ó')
        texto = texto.replace('Ãº', 'ú')
        texto = texto.replace('Ã±', 'ñ')
        texto = texto.replace('Ã¼', 'ü')
        texto = texto.replace('Â¿', '¿')
        texto = texto.replace('Â¡', '¡')
        
        # TERCERO: Corregir palabras específicas
        reemplazos = {
            'Mxico': 'México',
            'regin': 'región', 
            'caracteristicas': 'características',
            'caractersticas': 'características',
            'azcar': 'azúcar',
            'unica': 'única',
            'unico': 'único',
            'espana': 'España',
            'espaa': 'España',
            'espaola': 'española'
        }
        
        for palabra, corregida in reemplazos.items():
            if palabra in texto:
                texto = texto.replace(palabra, corregida)
                cambios.append(f'{palabra}→{corregida}')
        
        # Verificar cambios
        if texto != original:
            tildes_antes = sum(1 for c in original if c in 'áéíóúñüÁÉÍÓÚÑÜ')
            tildes_despues = sum(1 for c in texto if c in 'áéíóúñüÁÉÍÓÚÑÜ')
            
            print(f'[Corrector] Cambios: {", ".join(cambios) if cambios else "encoding"}')
            print(f'[Corrector] Tildes: {tildes_antes} → {tildes_despues}')
        
        return texto

if __name__ == "__main__":
    corrector = CorrectorEspanol()
    
    tests = [
        "preparaciÃÂ³n Mxico regin",
        "caracterÃÂsticas Ãºnicas",
        "azÃÂºcar en vinos espaÃ±oles"
    ]
    
    for test in tests:
        print(f"\nTest: {test}")
        print(f"Corregido: {corrector.corregir_texto(test)}")
