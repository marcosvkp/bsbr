import hashlib
import os

class Security:
    """
    Classe utilitária para hashing e verificação de senhas.
    Usando hashlib com salt para uma implementação segura sem dependências externas pesadas.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera um hash seguro da senha usando PBKDF2."""
        salt = os.urandom(32) # Gera um salt aleatório
        key = hashlib.pbkdf2_hmac(
            'sha256', # Algoritmo de hash
            password.encode('utf-8'), # Senha
            salt, # Salt
            100000 # Iterações
        )
        # Armazena o salt e o hash juntos
        return salt.hex() + ':' + key.hex()

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        try:
            salt_hex, key_hex = stored_password.split(':')
            salt = bytes.fromhex(salt_hex)
            stored_key = bytes.fromhex(key_hex)
            
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                provided_password.encode('utf-8'),
                salt,
                100000
            )
            return new_key == stored_key
        except Exception:
            return False
